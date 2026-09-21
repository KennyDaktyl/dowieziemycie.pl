/** Reverse-geocodes coordinates to a human address via Nominatim (OSM), client-side. */
export async function reverseGeocode(lat: number, lng: number): Promise<string | null> {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=16`,
      { headers: { Accept: "application/json" } },
    );
    if (!res.ok) return null;
    const data = await res.json();
    return data.display_name ? shortenAddress(data.display_name as string) : null;
  } catch {
    return null;
  }
}

export interface AddressSuggestion {
  label: string;
  lat: number;
  lng: number;
}

/** Forward address search (autocomplete) via Nominatim, biased to Poland. */
export async function searchAddress(query: string): Promise<AddressSuggestion[]> {
  if (query.trim().length < 3) return [];
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=pl&limit=5`,
      { headers: { Accept: "application/json" } },
    );
    if (!res.ok) return [];
    const data = await res.json();
    return (data as Array<{ display_name: string; lat: string; lon: string }>).map((item) => ({
      label: shortenAddress(item.display_name),
      lat: Number(item.lat),
      lng: Number(item.lon),
    }));
  } catch {
    return [];
  }
}

const MAX_ADDRESS_LEN = 190; // backend column is 200 — keep headroom

/** Nominatim's display_name appends every administrative level ("…, gmina X,
 * powiat Y, Górnośląsko-Zagłębiowska Metropolia, województwo Z, 42-625,
 * Polska") — up to 236 chars for Katowice Airport, past the backend's
 * 200-char address column, which made every such booking a 400. Those tail
 * segments add nothing a driver can navigate by (lat/lng do that), so drop
 * them, then hard-cap at a segment boundary as a last resort. */
export function shortenAddress(label: string): string {
  const parts = label.split(", ").filter((p) => !/^(gmina|powiat|województwo|Polska)\b/i.test(p) && !/Metropolia/i.test(p));
  let out = parts.join(", ");
  if (out.length > MAX_ADDRESS_LEN) {
    const cut = out.slice(0, MAX_ADDRESS_LEN);
    const at = cut.lastIndexOf(", ");
    out = at > MAX_ADDRESS_LEN / 2 ? cut.slice(0, at) : cut;
  }
  return out || label.slice(0, MAX_ADDRESS_LEN);
}
