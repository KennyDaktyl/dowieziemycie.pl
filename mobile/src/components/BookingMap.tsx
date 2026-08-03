import { useEffect, useState } from "react";
import { StyleSheet, View } from "react-native";
import { WebView } from "react-native-webview";

import { API_BASE_URL } from "@/lib/api";
import { colors } from "@/lib/theme";

interface LatLng {
  lat: number;
  lng: number;
}

/** Real road-following geometry from the shared backend's OSRM-backed
 * endpoint — same one the web frontends use — so the driver sees the actual
 * streets the customer will be picked up/dropped off from, not a straight
 * line ignoring the road network. */
function useRoadRoute(pickup: LatLng | null, dropoff: LatLng | null): LatLng[] | null {
  const [geometry, setGeometry] = useState<LatLng[] | null>(null);

  useEffect(() => {
    if (!pickup || !dropoff) {
      setGeometry(null);
      return;
    }
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
        const res = await fetch(`${API_BASE_URL}/api/route-estimate/?${params}`, { signal: controller.signal });
        if (res.ok) {
          const data: { geometry: [number, number][] } = await res.json();
          setGeometry(data.geometry.map(([lat, lng]) => ({ lat, lng })));
        }
      } catch {
        // ignore — falls back to a straight line below
      }
    })();
    return () => controller.abort();
  }, [pickup?.lat, pickup?.lng, dropoff?.lat, dropoff?.lng]);

  return geometry;
}

function buildHtml(pickup: LatLng, dropoff: LatLng | null, route: LatLng[] | null): string {
  const points = dropoff ? [pickup, dropoff] : [pickup];
  const line = route && route.length > 1 ? route : points;
  const pointsJson = JSON.stringify(points.map((p) => [p.lat, p.lng]));
  const lineJson = JSON.stringify(line.map((p) => [p.lat, p.lng]));
  const dashed = !route;

  return `<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>html,body,#map{height:100%;margin:0;padding:0;background:${colors.panel};}</style>
</head>
<body>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    var points = ${pointsJson};
    var line = ${lineJson};
    var map = L.map('map', { zoomControl: false, attributionControl: false });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    var pickupIcon = new L.Icon.Default();
    var dropoffIcon = new L.Icon({
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      iconSize: [25, 41], iconAnchor: [12, 41], className: 'hue-rotate-180',
    });
    L.marker(points[0], { icon: pickupIcon }).addTo(map);
    if (points.length > 1) L.marker(points[1], { icon: dropoffIcon }).addTo(map);
    if (line.length > 1) {
      L.polyline(line, { color: '${colors.amber}', weight: 4, opacity: ${dashed ? "0.6" : "0.85"}${
        dashed ? ", dashArray: '6 6'" : ""
      } }).addTo(map);
    }
    if (points.length > 1) {
      map.fitBounds(line.length > 1 ? line : points, { padding: [24, 24] });
    } else {
      map.setView(points[0], 14);
    }
  </script>
</body>
</html>`;
}

/** Read-only road-route map for a booking's pickup (and optionally dropoff)
 * — rendered via a WebView + Leaflet/OpenStreetMap rather than a native
 * maps SDK, so it needs no Google/Apple Maps API key and stays visually
 * consistent with the same Leaflet maps used on both websites. */
export function BookingMap({ pickup, dropoff, height = 180 }: { pickup: LatLng; dropoff?: LatLng | null; height?: number }) {
  const route = useRoadRoute(pickup, dropoff ?? null);
  const html = buildHtml(pickup, dropoff ?? null, route);

  return (
    <View style={[styles.wrap, { height }]}>
      <WebView
        source={{ html }}
        style={styles.webview}
        scrollEnabled={false}
        originWhitelist={["*"]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { borderRadius: 12, overflow: "hidden", borderWidth: 1, borderColor: colors.line },
  webview: { flex: 1, backgroundColor: colors.panel },
});
