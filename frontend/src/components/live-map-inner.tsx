"use client";

import "leaflet/dist/leaflet.css";

import { useEffect } from "react";
import { CircleMarker, MapContainer, TileLayer, useMap } from "react-leaflet";

import { fixLeafletDefaultIcon } from "@/lib/leaflet-icon-fix";

fixLeafletDefaultIcon();

const KRAKOW_CENTER: [number, number] = [50.0614, 19.9366];

function Recenter({ position }: { position: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(position, map.getZoom(), { animate: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [position[0], position[1]]);
  return null;
}

export function LiveMapInner({
  position,
  color,
}: {
  position: [number, number] | null;
  color: string;
}) {
  const center = position ?? KRAKOW_CENTER;

  return (
    <MapContainer
      center={center}
      zoom={position ? 12 : 10}
      scrollWheelZoom={false}
      className="h-[340px] w-full md:h-[460px] lg:h-[560px]"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {position && <Recenter position={position} />}
      {position && (
        <CircleMarker
          center={position}
          radius={9}
          pathOptions={{ color: "#0B0F16", weight: 2, fillColor: color, fillOpacity: 1 }}
        />
      )}
    </MapContainer>
  );
}
