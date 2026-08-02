"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { wsBaseUrl } from "@/lib/api";
import type { DriverLiveStatus } from "@/lib/types";

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

  const mapDrivers =
    driver?.current_lat && driver?.current_lng
      ? [
          {
            id: driver.id,
            position: [Number(driver.current_lat), Number(driver.current_lng)] as [number, number],
            color: "#F5A623",
            label: driver.name,
          },
        ]
      : [];

  return (
    <div className="isolate relative overflow-hidden rounded-[14px] border border-line bg-panel">
      <div className="absolute top-3.5 left-3.5 z-[400] flex items-center gap-1.5 rounded-full border border-line bg-[#121a24]/90 px-3 py-1.5 text-[12.5px] font-semibold backdrop-blur-sm">
        <span
          className={`h-2 w-2 rounded-full ${connectionState === "open" ? "bg-green" : "bg-muted"}`}
        />
        {driver ? tStatus(STATUS_KEY[driver.status] as never) : tMap("noActiveDriver")}
      </div>

      <LiveMapInner drivers={mapDrivers} />

      <div className="absolute right-3.5 bottom-3.5 left-3.5 z-[400] rounded-xl border border-line bg-[#121a24]/92 px-3.5 py-3 backdrop-blur-md">
        <div className="text-[13.5px] font-semibold">
          {driverName ?? tMap("vehicleUnknown")}
          {driverVehicle ? ` · ${driverVehicle}` : ""}
        </div>
      </div>
    </div>
  );
}
