"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect, useMemo } from "react";
import { MapContainer, Marker, Polyline, TileLayer, useMap, useMapEvents } from "react-leaflet";

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

// Leaflet reports click/drag coordinates at full floating-point precision,
// which the backend's DecimalField(decimal_places=6) rejects outright.
function roundCoord(n: number): number {
  return Math.round(n * 1e6) / 1e6;
}

function ClickToPlace({ onPick }: { onPick: (pos: LatLng) => void }) {
  useMapEvents({
    click(e) {
      onPick({ lat: roundCoord(e.latlng.lat), lng: roundCoord(e.latlng.lng) });
    },
  });
  return null;
}

// The map's container height depends on sibling content (e.g. the driver-ETA
// card appearing/disappearing changes the grid row it row-spans into) —
// Leaflet caches its own size and doesn't notice, leaving stale gray tile
// area until something nudges it. ResizeObserver keeps it in sync.
function InvalidateSizeOnResize() {
  const map = useMap();
  useEffect(() => {
    const container = map.getContainer();
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(container);
    return () => observer.disconnect();
  }, [map]);
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
  routeGeometry,
  onPickupChange,
  onDropoffChange,
}: {
  pickup: LatLng | null;
  dropoff: LatLng | null;
  activeField: "pickup" | "dropoff";
  routeGeometry?: [number, number][] | null;
  onPickupChange: (pos: LatLng) => void;
  onDropoffChange: (pos: LatLng) => void;
}) {
  const points = useMemo(() => [pickup, dropoff].filter((p): p is LatLng => p !== null), [pickup, dropoff]);
  const routeLine = useMemo(
    () => (routeGeometry && routeGeometry.length > 1 ? routeGeometry.map(([lat, lng]) => ({ lat, lng })) : null),
    [routeGeometry],
  );
  const fitPoints = routeLine ?? points;

  function handlePick(pos: LatLng) {
    if (activeField === "pickup") onPickupChange(pos);
    else onDropoffChange(pos);
  }

  return (
    <div className="isolate h-full">
      <MapContainer
        center={pickup ?? dropoff ?? KRAKOW_CENTER}
        zoom={points.length ? 12 : 9}
        scrollWheelZoom={false}
        className="h-full w-full rounded-lg"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ClickToPlace onPick={handlePick} />
        <InvalidateSizeOnResize />
        <FitBounds points={fitPoints} />
        {routeLine && (
          <Polyline positions={routeLine} pathOptions={{ color: "#f5a623", weight: 4, opacity: 0.85 }} />
        )}
        {pickup && (
          <Marker
            position={pickup}
            icon={pickupIcon}
            draggable
            eventHandlers={{
              dragend: (e) => {
                const pos = e.target.getLatLng();
                onPickupChange({ lat: roundCoord(pos.lat), lng: roundCoord(pos.lng) });
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
                onDropoffChange({ lat: roundCoord(pos.lat), lng: roundCoord(pos.lng) });
              },
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
