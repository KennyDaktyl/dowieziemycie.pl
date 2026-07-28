"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect, useMemo } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";

import { fixLeafletDefaultIcon } from "@/lib/leaflet-icon-fix";

fixLeafletDefaultIcon();

export interface LatLng {
  lat: number;
  lng: number;
}

const KRAKOW_CENTER: LatLng = { lat: 50.0614, lng: 19.9366 };

const pickupIcon = new L.Icon.Default();
const dropoffIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  className: "hue-rotate-[130deg]",
});

function ClickToPlace({ onPick }: { onPick: (pos: LatLng) => void }) {
  useMapEvents({
    click(e) {
      onPick({ lat: e.latlng.lat, lng: e.latlng.lng });
    },
  });
  return null;
}

function FitBounds({ points }: { points: LatLng[] }) {
  const map = useMap();
  const key = points.map((p) => `${p.lat},${p.lng}`).join("|");
  useEffect(() => {
    if (points.length === 0) return;
    if (points.length === 1) {
      map.setView(points[0], 13, { animate: true });
    } else {
      map.fitBounds(
        points.map((p) => [p.lat, p.lng]),
        { padding: [40, 40], animate: true },
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  return null;
}

export function BookingMap({
  pickup,
  dropoff,
  activeField,
  onPickupChange,
  onDropoffChange,
}: {
  pickup: LatLng | null;
  dropoff: LatLng | null;
  activeField: "pickup" | "dropoff";
  onPickupChange: (pos: LatLng) => void;
  onDropoffChange: (pos: LatLng) => void;
}) {
  const points = useMemo(() => [pickup, dropoff].filter((p): p is LatLng => p !== null), [pickup, dropoff]);

  function handlePick(pos: LatLng) {
    if (activeField === "pickup") onPickupChange(pos);
    else onDropoffChange(pos);
  }

  return (
    <div className="isolate">
      <MapContainer
        center={pickup ?? dropoff ?? KRAKOW_CENTER}
        zoom={points.length ? 12 : 9}
        scrollWheelZoom={false}
        className="h-[240px] w-full rounded-lg md:h-[380px] lg:h-full lg:min-h-[420px]"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickToPlace onPick={handlePick} />
        <FitBounds points={points} />
        {pickup && (
          <Marker
            position={pickup}
            icon={pickupIcon}
            draggable
            eventHandlers={{
              dragend: (e) => {
                const pos = e.target.getLatLng();
                onPickupChange({ lat: pos.lat, lng: pos.lng });
              },
            }}
          />
        )}
        {dropoff && (
          <Marker
            position={dropoff}
            icon={dropoffIcon}
            draggable
            eventHandlers={{
              dragend: (e) => {
                const pos = e.target.getLatLng();
                onDropoffChange({ lat: pos.lat, lng: pos.lng });
              },
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
