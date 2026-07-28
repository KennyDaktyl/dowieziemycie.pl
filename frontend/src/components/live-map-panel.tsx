"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { publicApiBaseUrl } from "@/lib/api";
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

const POLL_INTERVAL_MS = 15000;

export function LiveMapPanel() {
  const tStatus = useTranslations("StatusLegend");
  const tMap = useTranslations("LiveMap");
  const [drivers, setDrivers] = useState<DriverLiveStatus[]>([]);

  useEffect(() => {
    let cancelled = false;
    async function poll() {
      try {
        const res = await fetch(`${publicApiBaseUrl()}/api/fleet/live-status/`);
        if (!res.ok || cancelled) return;
        setDrivers(await res.json());
      } catch {
        // silently keep last known state — a transient network hiccup shouldn't blank the map
      }
    }
    poll();
    const timer = setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const driver = drivers[0] ?? null;
  const position: [number, number] | null =
    driver?.current_lat && driver?.current_lng ? [Number(driver.current_lat), Number(driver.current_lng)] : null;
  const color = driver ? (STATUS_COLORS[driver.status] ?? "#8B96A3") : "#8B96A3";
  const statusLabel = driver ? tStatus(STATUS_KEY[driver.status] as never) : tStatus("offline");
  const statusDesc = driver ? tStatus(`${STATUS_KEY[driver.status]}Desc` as never) : tMap("noActiveDriver");

  return (
    <div className="isolate relative overflow-hidden rounded-[14px] border border-line bg-panel">
      <div className="absolute top-3.5 left-3.5 z-[400] flex items-center gap-1.5 rounded-full border border-line bg-[#121a24]/90 px-3 py-1.5 text-[12.5px] font-semibold backdrop-blur-sm">
        <span className="relative h-2 w-2 rounded-full" style={{ backgroundColor: color }}>
          {driver && (
            <span
              className="absolute -inset-1 animate-ping rounded-full border-[1.5px]"
              style={{ borderColor: color }}
            />
          )}
        </span>
        {statusLabel}
      </div>

      <LiveMapInner position={position} color={color} />

      <div className="absolute right-3.5 bottom-3.5 left-3.5 z-[400] flex items-center justify-between rounded-xl border border-line bg-[#121a24]/92 px-3.5 py-3 backdrop-blur-md">
        <div>
          <div className="text-[13.5px] font-semibold">
            {driver ? `${driver.name} · ${driver.vehicle_name ?? tMap("vehicleUnknown")}` : tMap("vehicleUnknown")}
          </div>
          <div className="text-[11.5px] text-muted">{statusDesc}</div>
        </div>
      </div>
    </div>
  );
}
