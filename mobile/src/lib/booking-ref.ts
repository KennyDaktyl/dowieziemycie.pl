/** Short, human-readable booking reference — e.g. "Ry6Sk" for booking #6,
 * Rybna -> Skawina. Built purely from data already on the booking (no
 * backend field), so it's consistent everywhere it's displayed without
 * needing a migration. The number IS the booking's real id, not a
 * separately-tracked sequence — searching/reading it off always points
 * back to the same record. */

const NOISE_PREFIXES = ["gmina ", "powiat ", "województwo "];
const POSTAL_CODE_RE = /\b\d{2}-\d{3}\b/;

function extractLocality(address: string): string {
  const cleaned = address
    .split(",")
    .map((part) => part.replace(POSTAL_CODE_RE, "").trim())
    .filter(Boolean)
    .filter((part) => !["polska", "poland"].includes(part.toLowerCase()))
    .filter((part) => !NOISE_PREFIXES.some((prefix) => part.toLowerCase().startsWith(prefix)));

  // Addresses run street -> locality -> gmina/powiat/województwo -> postal
  // -> country; after stripping the noise, whatever's left is the street
  // (if any) followed by the actual town/village — the last remaining
  // segment is the one that names an actual place.
  return cleaned[cleaned.length - 1] ?? "";
}

function cityAbbreviation(address: string): string {
  const locality = extractLocality(address);
  const letters = locality.replace(/[^\p{L}]/gu, "").slice(0, 2);
  if (letters.length < 2) return "Xx";
  return letters.charAt(0).toUpperCase() + letters.charAt(1).toLowerCase();
}

export function bookingRef(booking: { id: number; pickup_address: string; dropoff_address: string }): string {
  return `${cityAbbreviation(booking.pickup_address)}${booking.id}${cityAbbreviation(booking.dropoff_address)}`;
}
