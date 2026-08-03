"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Polyline, TileLayer, useMap } from "react-leaflet";

import { publicApiBaseUrl, withSiteHeader } from "@/lib/api";
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

/** Real road-following geometry from the same OSRM-backed endpoint the
 * booking forms use — a straight line between pickup/dropoff would show a
 * route that ignores the actual streets, so this is fetched rather than
 * just drawn between the two points. Falls back to a straight dashed line
 * only if the request fails (still better than no line at all). */
function useRoadRoute(pickup: LatLng, dropoff: LatLng): LatLng[] | null {
  const [geometry, setGeometry] = useState<LatLng[] | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setGeometry(null);
    (async () => {
      try {
        const params = new URLSearchParams({
          pickup_lat: String(pickup.lat),
          pickup_lng: String(pickup.lng),
          dropoff_lat: String(dropoff.lat),
          dropoff_lng: String(dropoff.lng),
          scheduled_at: new Date().toISOString(),
        });
        const res = await fetch(`${publicApiBaseUrl()}/api/route-estimate/?${params}`, {
          signal: controller.signal,
          headers: withSiteHeader(),
        });
        if (res.ok) {
          const data: { geometry: [number, number][] } = await res.json();
          setGeometry(data.geometry.map(([lat, lng]) => ({ lat, lng })));
        }
      } catch {
        // ignore — falls back to the straight line below
      }
    })();
    return () => controller.abort();
  }, [pickup.lat, pickup.lng, dropoff.lat, dropoff.lng]);

  return geometry;
}

/** Small, read-only route thumbnail for an already-placed booking — no
 * click/drag handling, unlike BookingMap which is for actively picking a
 * new pickup/dropoff. Just a visual "this is where you're going". */
export function BookingRoutePreview({ pickup, dropoff }: { pickup: LatLng; dropoff: LatLng }) {
  const points = useMemo(() => [pickup, dropoff], [pickup, dropoff]);
  const roadRoute = useRoadRoute(pickup, dropoff);
  const line = roadRoute && roadRoute.length > 1 ? roadRoute : points;
  const fitPoints = roadRoute && roadRoute.length > 1 ? roadRoute : points;

  return (
    <div className="isolate h-[140px] w-full overflow-hidden rounded-lg">
      <MapContainer center={pickup} zoom={12} scrollWheelZoom={false} dragging={false} zoomControl={false} className="h-full w-full">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds points={fitPoints} />
        <Polyline
          positions={line}
          pathOptions={
            roadRoute
              ? { color: "#f5a623", weight: 3.5, opacity: 0.85 }
              : { color: "#f5a623", weight: 3, opacity: 0.6, dashArray: "6 6" }
          }
        />
        <Marker position={pickup} icon={pickupIcon} />
        <Marker position={dropoff} icon={dropoffIcon} />
      </MapContainer>
    </div>
  );
}
