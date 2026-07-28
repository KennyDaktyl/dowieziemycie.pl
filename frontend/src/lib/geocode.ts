/** Reverse-geocodes coordinates to a human address via Nominatim (OSM), client-side. */
export async function reverseGeocode(lat: number, lng: number): Promise<string | null> {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=16`,
      { headers: { Accept: "application/json" } },
    );
    if (!res.ok) return null;
    const data = await res.json();
    return (data.display_name as string) ?? null;
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
      label: item.display_name,
      lat: Number(item.lat),
      lng: Number(item.lon),
    }));
  } catch {
    return [];
  }
}
