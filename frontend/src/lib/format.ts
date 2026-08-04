const VAT_RATE = 0.23;

/** All PLN prices in this app are gross (VAT-inclusive) — this derives the
 * net amount for display next to the final price a customer is about to
 * pay (booking summary, deposit payment). */
export function netFromGross(grossPln: string | number): number {
  const gross = typeof grossPln === "string" ? parseFloat(grossPln) : grossPln;
  return gross / (1 + VAT_RATE);
}

/** "850 m" under a kilometer, "2.4 km" above — a live "driver is 400m
 * away" reads a lot clearer than "0.4 km" when they're right around the
 * corner. */
export function formatDistance(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)} m`;
  return `${km.toFixed(1)} km`;
}
