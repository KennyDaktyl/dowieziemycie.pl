const VAT_RATE = 0.23;

/** All PLN prices in this app are gross (VAT-inclusive) — this derives the
 * net amount for display next to the final price a customer is about to
 * pay (booking summary, deposit payment). */
export function netFromGross(grossPln: string | number): number {
  const gross = typeof grossPln === "string" ? parseFloat(grossPln) : grossPln;
  return gross / (1 + VAT_RATE);
}
