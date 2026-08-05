import type { StatusTone } from "./theme";
import type { DriverBooking } from "./types";

/** How much has actually landed vs. what's still owed — the driver needs
 * real numbers here, not just a status label, since they're often the one
 * collecting the remainder in person at the end of the ride. */
export function paymentAmounts(booking: DriverBooking): { paid: number; remaining: number } | null {
  if (booking.price == null) return null;
  const price = Number(booking.price);
  if (booking.remainder_paid_at) return { paid: price, remaining: 0 };
  if (booking.paid_at && booking.deposit_amount != null) {
    const deposit = Number(booking.deposit_amount);
    return { paid: deposit, remaining: Math.max(price - deposit, 0) };
  }
  return { paid: 0, remaining: price };
}

/** The single most important thing a driver needs to see at a glance about
 * a booking: is it paid, and if not, how much is still owed. One combined
 * label + color so it can render as one prominent badge instead of a
 * "Płatność" row buried among a dozen other equally-styled rows. */
export function paymentStatus(booking: DriverBooking): { label: string; tone: StatusTone } {
  if (booking.remainder_paid_at) return { label: "Zapłacono w całości", tone: "green" };
  if (booking.paid_at) {
    const amounts = paymentAmounts(booking);
    const remaining = amounts && amounts.remaining > 0 ? ` — do pobrania: ${amounts.remaining.toFixed(0)} zł` : "";
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
