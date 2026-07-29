"use client";

import "leaflet/dist/leaflet.css";

import { useEffect, useMemo } from "react";
import { CircleMarker, MapContainer, TileLayer, Tooltip, useMap } from "react-leaflet";

import { fixLeafletDefaultIcon } from "@/lib/leaflet-icon-fix";

fixLeafletDefaultIcon();

const KRAKOW_CENTER: [number, number] = [50.0614, 19.9366];

export interface MapDriver {
  id: number;
  position: [number, number];
  color: string;
  label: string;
}

function FitToDrivers({ drivers }: { drivers: MapDriver[] }) {
  const map = useMap();
  const key = drivers.map((d) => `${d.id}:${d.position[0]},${d.position[1]}`).join("|");
  useEffect(() => {
    if (drivers.length === 0) return;
    if (drivers.length === 1) {
      map.setView(drivers[0].position, Math.max(map.getZoom(), 12), { animate: true });
    } else {
      map.fitBounds(
        drivers.map((d) => d.position),
        { padding: [50, 50], animate: true },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return null;
}

export function LiveMapInner({ drivers }: { drivers: MapDriver[] }) {
  const center = useMemo(() => drivers[0]?.position ?? KRAKOW_CENTER, [drivers]);

  return (
    <MapContainer
      center={center}
      zoom={drivers.length ? 12 : 10}
      scrollWheelZoom={false}
      className="h-[340px] w-full md:h-[460px] lg:h-[560px]"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitToDrivers drivers={drivers} />
      {drivers.map((d) => (
        <CircleMarker
          key={d.id}
          center={d.position}
          radius={9}
          pathOptions={{ color: "#0B0F16", weight: 2, fillColor: d.color, fillOpacity: 1 }}
        >
          <Tooltip direction="top" offset={[0, -10]}>
            {d.label}
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
