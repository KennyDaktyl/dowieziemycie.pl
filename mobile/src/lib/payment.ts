import type { StatusTone } from "./theme";
import type { Currency, DriverBooking } from "./types";

export const CURRENCY_LABEL: Record<Currency, string> = { pln: "zł", eur: "EUR" };

/** "75 zł" / "18 EUR" / "13.33 EUR" — whole amounts without decimals. */
export function formatMoney(amount: number | string | null | undefined, currency: Currency): string {
  if (amount == null || amount === "") return "—";
  const value = Number(amount);
  if (!Number.isFinite(value)) return "—";
  const text = Number.isInteger(value) ? String(value) : value.toFixed(2);
  return `${text} ${CURRENCY_LABEL[currency]}`;
}

/** Deposit / still-owed / price of a booking in ONE currency — the one the
 * customer pays in (Booking.payment_currency) unless told otherwise. The
 * server does all the arithmetic (deposit set for that currency or the
 * default rule, a balance fixed by hand, …); the app only reads it. */
export function amountsIn(booking: DriverBooking, currency: Currency = booking.payment_currency ?? "pln") {
  const pln = currency === "pln";
  const deposit = pln ? booking.deposit_amount : booking.deposit_amount_eur;
  const remaining = pln ? booking.remaining_amount : booking.remaining_amount_eur;
  const depositNum = deposit != null ? Number(deposit) : null;
  const remainingNum = remaining != null ? Number(remaining) : 0;
  const total = pln
    ? booking.price != null ? Number(booking.price) : null
    : booking.price_eur != null
      ? Number(booking.price_eur)
      : depositNum != null ? depositNum + remainingNum : null;
  return { currency, deposit: depositNum, remaining: remainingNum, total };
}

/** How much has actually landed vs. what's still owed — the driver needs
 * real numbers here, not just a status label, since they're often the one
 * collecting the remainder in person at the end of the ride. */
export function paymentAmounts(booking: DriverBooking): { paid: number; remaining: number; currency: Currency } | null {
  const a = amountsIn(booking);
  if (a.total == null) return null;
  if (booking.remainder_paid_at) return { paid: a.total, remaining: 0, currency: a.currency };
  if (booking.paid_at && a.deposit != null) return { paid: a.deposit, remaining: a.remaining, currency: a.currency };
  return { paid: 0, remaining: a.total, currency: a.currency };
}

/** The single most important thing a driver needs to see at a glance about
 * a booking: is it paid, and if not, how much is still owed. One combined
 * label + color so it can render as one prominent badge instead of a
 * "Płatność" row buried among a dozen other equally-styled rows. */
export function paymentStatus(booking: DriverBooking): { label: string; tone: StatusTone } {
  if (booking.remainder_paid_at) return { label: "Zapłacono w całości", tone: "green" };
  if (booking.paid_at) {
    const amounts = paymentAmounts(booking);
    const remaining =
      amounts && amounts.remaining > 0 ? ` — do pobrania: ${formatMoney(amounts.remaining, amounts.currency)}` : "";
    return { label: `Zaliczka wpłacona${remaining}`, tone: "amber" };
  }
  return { label: "Nieopłacone", tone: "red" };
}

export function formatDateTime(value: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("pl-PL", {
    day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export function formatDuration(startedAt: string | null, completedAt: string | null): string | null {
  if (!startedAt || !completedAt) return null;
  const minutes = Math.round((new Date(completedAt).getTime() - new Date(startedAt).getTime()) / 60000);
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h} godz. ${m} min` : `${m} min`;
}
