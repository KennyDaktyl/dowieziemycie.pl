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

const STATUS_COLORS: Record<string, string> = {
  OFFLINE: "#8B96A3",
  DOSTEPNY: "#3ECF8E",
  JADACY_PO_KLIENTA: "#F5A623",
  W_KURSIE: "#E5484D",
  WRACA_DO_BAZY: "#F5A623",
};

const STATUS_KEY: Record<string, string> = {
  OFFLINE: "offline",
  DOSTEPNY: "available",
  JADACY_PO_KLIENTA: "enRoute",
  W_KURSIE: "busy",
  WRACA_DO_BAZY: "enRoute",
};

const RECONNECT_BASE_MS = 2000;
const RECONNECT_MAX_MS = 15000;

interface LiveMapMessage {
  type: "snapshot" | "update";
  drivers?: DriverLiveStatus[];
  driver?: DriverLiveStatus;
}

export function LiveMapPanel() {
  const tStatus = useTranslations("StatusLegend");
  const tMap = useTranslations("LiveMap");
  const [driversById, setDriversById] = useState<Record<number, DriverLiveStatus>>({});

  // WebSocket, not polling — apps.tracking pushes a position update the
  // instant a driver's own panel sends one, instead of waiting up to 15s.
  // Reconnects with capped exponential backoff since this is a public page
  // that visitors may leave open for a while.
  useEffect(() => {
    let cancelled = false;
    let retryDelay = RECONNECT_BASE_MS;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;
    let socket: WebSocket | null = null;

    function upsert(driver: DriverLiveStatus) {
      setDriversById((prev) => {
        const next = { ...prev };
        if (driver.status === "OFFLINE" || !driver.current_lat || !driver.current_lng) {
          delete next[driver.id];
        } else {
          next[driver.id] = driver;
        }
        return next;
      });
    }

    function connect() {
      if (cancelled) return;
      socket = new WebSocket(`${wsBaseUrl()}/ws/live-map/`);

      socket.onopen = () => {
        retryDelay = RECONNECT_BASE_MS;
      };
      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data) as LiveMapMessage;
          if (msg.type === "snapshot" && msg.drivers) {
            const next: Record<number, DriverLiveStatus> = {};
            for (const d of msg.drivers) next[d.id] = d;
            setDriversById(next);
          } else if (msg.type === "update" && msg.driver) {
            upsert(msg.driver);
          }
        } catch {
          // ignore malformed frame
        }
      };
      socket.onclose = () => {
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
  }, []);

  const drivers = Object.values(driversById);
  const mapDrivers = drivers.map((d) => ({
    id: d.id,
    position: [Number(d.current_lat), Number(d.current_lng)] as [number, number],
    color: STATUS_COLORS[d.status] ?? "#8B96A3",
    label: `${d.name} · ${tStatus(STATUS_KEY[d.status] as never)}`,
  }));

  let badgeLabel: string;
  let badgeColor = "#8B96A3";
  if (drivers.length === 0) {
    badgeLabel = tStatus("offline");
  } else if (drivers.length === 1) {
    badgeLabel = tStatus(STATUS_KEY[drivers[0].status] as never);
    badgeColor = STATUS_COLORS[drivers[0].status] ?? "#8B96A3";
  } else {
    badgeLabel = tMap("driversOnline", { count: drivers.length });
  }

  return (
    <div className="isolate relative overflow-hidden rounded-[14px] border border-line bg-panel">
      <div className="absolute top-3.5 left-3.5 z-[400] flex items-center gap-1.5 rounded-full border border-line bg-[#121a24]/90 px-3 py-1.5 text-[12.5px] font-semibold backdrop-blur-sm">
        <span className="relative h-2 w-2 rounded-full" style={{ backgroundColor: badgeColor }}>
          {drivers.length > 0 && (
            <span
              className="absolute -inset-1 animate-ping rounded-full border-[1.5px]"
              style={{ borderColor: badgeColor }}
            />
          )}
        </span>
        {badgeLabel}
      </div>

      <LiveMapInner drivers={mapDrivers} />

      <div className="absolute right-3.5 bottom-3.5 left-3.5 z-[400] flex flex-col gap-2 rounded-xl border border-line bg-[#121a24]/92 px-3.5 py-3 backdrop-blur-md">
        {drivers.length === 0 ? (
          <div className="text-[13.5px] font-semibold">{tMap("noActiveDriver")}</div>
        ) : (
          drivers.map((d) => (
            <div key={d.id} className="flex items-center justify-between gap-3">
              <div>
                <div className="text-[13.5px] font-semibold">
                  {d.name} · {d.vehicle_name ?? tMap("vehicleUnknown")}
                </div>
                <div className="text-[11.5px] text-muted">{tStatus(`${STATUS_KEY[d.status]}Desc` as never)}</div>
              </div>
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ backgroundColor: STATUS_COLORS[d.status] ?? "#8B96A3" }}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
