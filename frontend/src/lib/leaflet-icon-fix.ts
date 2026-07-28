import L from "leaflet";

// Leaflet's default marker icon URLs are relative paths into its own package,
// which bundlers don't resolve — point them at the matching CDN build instead.
let patched = false;
export function fixLeafletDefaultIcon() {
  if (patched) return;
  patched = true;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });
}
