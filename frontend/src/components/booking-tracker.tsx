"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";

import { publicApiBaseUrl, withSiteHeader, wsBaseUrl } from "@/lib/api";
import { formatDistance } from "@/lib/format";
import type { DriverLiveStatus, RouteEstimate } from "@/lib/types";

const LiveMapInner = dynamic(() => import("./live-map-inner").then((m) => m.LiveMapInner), {
  ssr: false,
  loading: () => <div className="h-[340px] w-full animate-pulse bg-panel-2" />,
});

const STATUS_KEY: Record<string, string> = {
  DOSTEPNY: "available",
  JADACY_PO_KLIENTA: "enRoute",
  W_KURSIE: "busy",
  WRACA_DO_BAZY: "enRoute",
};

const RECONNECT_BASE_MS = 2000;
const RECONNECT_MAX_MS = 15000;
// The route estimate is a real OSRM request server-side — refetching on
// every single GPS tick (every ~10s from the driver's app) would be
// wasteful for how little the ETA actually moves between ticks.
const ETA_REFRESH_MIN_MS = 20000;

type LatLng = { lat: number; lng: number };
type GeoStatus = "requesting" | "granted" | "denied" | "unsupported";

/** The customer's own live position, watched continuously (not just once)
 * so the "you are here" marker and ETA stay accurate if they're walking to
 * a different meeting spot while waiting. Exposes the permission state too
 * — silently doing nothing on denial left customers with no idea why their
 * position/ETA never showed up. */
function useMyPosition(): { position: LatLng | null; status: GeoStatus; retry: () => void } {
  const [position, setPosition] = useState<LatLng | null>(null);
  const [status, setStatus] = useState<GeoStatus>("requesting");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!("geolocation" in navigator)) {
      setStatus("unsupported");
      return;
    }
    setStatus("requesting");
    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setStatus("granted");
        setPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude });
      },
      () => setStatus("denied"),
      { enableHighAccuracy: true, maximumAge: 15000, timeout: 10000 },
    );
    return () => navigator.geolocation.clearWatch(watchId);
  }, [attempt]);

  return { position, status, retry: () => setAttempt((a) => a + 1) };
}

/** Live distance/ETA from the driver's current position to wherever the
 * customer actually is right now — reuses the same public route-estimate
 * endpoint the booking form uses, just with the driver and customer as the
 * two points instead of pickup/dropoff. */
function useLiveEta(driverPos: LatLng | null, myPos: LatLng | null): RouteEstimate | null {
  const [estimate, setEstimate] = useState<RouteEstimate | null>(null);
  const lastFetchRef = useRef(0);

  useEffect(() => {
    if (!driverPos || !myPos) return;
    const now = Date.now();
    if (now - lastFetchRef.current < ETA_REFRESH_MIN_MS) return;
    lastFetchRef.current = now;

    const controller = new AbortController();
    (async () => {
      try {
        const params = new URLSearchParams({
          pickup_lat: String(driverPos.lat),
          pickup_lng: String(driverPos.lng),
          dropoff_lat: String(myPos.lat),
          dropoff_lng: String(myPos.lng),
          scheduled_at: new Date().toISOString(),
        });
        const res = await fetch(`${publicApiBaseUrl()}/api/route-estimate/?${params}`, {
          signal: controller.signal,
          headers: withSiteHeader(),
        });
        if (res.ok) setEstimate(await res.json());
      } catch {
        // ignore — stale/aborted request or transient network hiccup
      }
    })();
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [driverPos?.lat, driverPos?.lng, myPos?.lat, myPos?.lng]);

  return estimate;
}

export function BookingTracker({
  bookingId,
  accessToken,
  code,
  driverName,
  driverVehicle,
}: {
  bookingId: number;
  accessToken?: string;
  code?: string;
  driverName: string | null;
  driverVehicle: string | null;
}) {
  const tStatus = useTranslations("StatusLegend");
  const tMap = useTranslations("LiveMap");
  const [driver, setDriver] = useState<DriverLiveStatus | null>(null);
  const [connectionState, setConnectionState] = useState<"connecting" | "open" | "closed">("connecting");
  const { position: myPos, status: geoStatus, retry: retryGeo } = useMyPosition();

  useEffect(() => {
    let cancelled = false;
    let retryDelay = RECONNECT_BASE_MS;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;
    let socket: WebSocket | null = null;

    function connect() {
      if (cancelled) return;
      setConnectionState("connecting");
      const authParam = code ? `code=${code}` : `token=${accessToken}`;
      socket = new WebSocket(`${wsBaseUrl()}/ws/booking/track/${bookingId}/?${authParam}`);

      socket.onopen = () => {
        retryDelay = RECONNECT_BASE_MS;
        setConnectionState("open");
      };
      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "update" && msg.driver) setDriver(msg.driver);
        } catch {
          // ignore malformed frame
        }
      };
      socket.onclose = () => {
        setConnectionState("closed");
        if (cancelled) return;
        retryTimer = setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, RECONNECT_MAX_MS);
      };
      socket.onerror = () => socket?.close();
    }

    connect();
    return () => {
      cancelled = true;
      if (retryTimer) clearTimeout(retryTimer);
      socket?.close();
    };
  }, [bookingId, accessToken, code]);

  const driverPos =
    driver?.current_lat && driver?.current_lng
      ? { lat: Number(driver.current_lat), lng: Number(driver.current_lng) }
      : null;
  const eta = useLiveEta(driverPos, myPos);

  const mapDrivers = [
    ...(driverPos ? [{ id: driver!.id, position: [driverPos.lat, driverPos.lng] as [number, number], color: "#F5A623", label: driver!.name }] : []),
    ...(myPos ? [{ id: -1, position: [myPos.lat, myPos.lng] as [number, number], color: "#2563eb", label: tMap("you") }] : []),
  ];

  return (
    <div className="isolate overflow-hidden rounded-[14px] border border-line bg-panel">
      <div className="relative">
        {/* Top-right, not top-left — Leaflet's own zoom control sits at
            top-left with z-index 1000, well above ours, and was silently
            covering anything placed there. */}
        <div className="absolute top-3.5 right-3.5 z-[1200] flex flex-col items-end gap-2">
          <div className="flex items-center gap-1.5 rounded-full border border-line bg-[#121a24]/95 px-3 py-1.5 text-[12.5px] font-semibold shadow-sm">
            <span
              className={`h-2 w-2 rounded-full ${connectionState === "open" ? "bg-green" : "bg-muted"}`}
            />
            {driver ? tStatus(STATUS_KEY[driver.status] as never) : tMap("noActiveDriver")}
          </div>
          {driverPos && myPos && (
            <div className="rounded-full border border-line bg-[#121a24]/95 px-3 py-1.5 text-[12.5px] font-semibold shadow-sm">
              {eta
                ? tMap("etaLabel", { minutes: Math.round(eta.duration_min), distance: formatDistance(eta.distance_km) })
                : tMap("etaCalculating")}
            </div>
          )}
        </div>

        <LiveMapInner drivers={mapDrivers} />

        <div className="absolute right-3.5 bottom-3.5 left-3.5 z-[400] rounded-xl border border-line bg-[#121a24]/92 px-3.5 py-3 backdrop-blur-md">
          <div className="text-[13.5px] font-semibold">
            {driverName ?? tMap("vehicleUnknown")}
            {driverVehicle ? ` · ${driverVehicle}` : ""}
          </div>
        </div>
      </div>

      {(geoStatus === "denied" || geoStatus === "unsupported") && (
        <div className="flex items-center justify-between gap-3 border-t border-line bg-panel-2 px-4 py-3">
          <p className="text-[12.5px] text-muted">
            {geoStatus === "denied" ? tMap("geoDenied") : tMap("geoUnsupported")}
          </p>
          {geoStatus === "denied" && (
            <button
              type="button"
              onClick={retryGeo}
              className="shrink-0 text-[12.5px] font-semibold text-amber underline"
            >
              {tMap("geoRetry")}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
