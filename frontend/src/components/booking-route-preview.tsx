"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect, useMemo } from "react";
import { MapContainer, Marker, Polyline, TileLayer, useMap } from "react-leaflet";

import { fixLeafletDefaultIcon } from "@/lib/leaflet-icon-fix";

fixLeafletDefaultIcon();

interface LatLng {
  lat: number;
  lng: number;
}

const pickupIcon = new L.Icon.Default();
const dropoffIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  className: "hue-rotate-[130deg]",
});

function FitBounds({ points }: { points: LatLng[] }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(
      points.map((p) => [p.lat, p.lng]),
      { padding: [24, 24] },
    );
  }, [map, points]);
  return null;
}

/** Small, read-only route thumbnail for an already-placed booking — no
 * click/drag handling, unlike BookingMap which is for actively picking a
 * new pickup/dropoff. Just a visual "this is where you're going". */
export function BookingRoutePreview({ pickup, dropoff }: { pickup: LatLng; dropoff: LatLng }) {
  const points = useMemo(() => [pickup, dropoff], [pickup, dropoff]);

  return (
    <div className="isolate h-[140px] w-full overflow-hidden rounded-lg">
      <MapContainer center={pickup} zoom={12} scrollWheelZoom={false} dragging={false} zoomControl={false} className="h-full w-full">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds points={points} />
        <Polyline positions={points} pathOptions={{ color: "#f5a623", weight: 3, opacity: 0.8, dashArray: "6 6" }} />
        <Marker position={pickup} icon={pickupIcon} />
        <Marker position={dropoff} icon={dropoffIcon} />
      </MapContainer>
    </div>
  );
}
