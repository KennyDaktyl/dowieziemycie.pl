import { extractLocality } from "./booking-ref";

/** The raw geocoded address ("Długa, Rybna, gmina Czernichów, powiat
 * krakowski, województwo małopolskie, 32-061, Polska") is fine for a
 * detail screen but wraps to 4-5 lines in a list card, making a list of
 * bookings hard to scan. Shows just the street (if any) + locality —
 * reuses the same locality-extraction booking-ref.ts already needed for
 * short reference codes, so "Rybna" and "Ry" in a ref agree. */
export function shortAddress(address: string): string {
  const locality = extractLocality(address);
  if (!locality) return address;
  const street = address.split(",")[0]?.trim();
  return street && street !== locality ? `${street}, ${locality}` : locality;
}
