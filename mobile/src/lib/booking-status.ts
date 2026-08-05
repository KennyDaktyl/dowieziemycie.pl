import type { StatusTone } from "./theme";

/** One place for what a Booking.status means visually — label + color tone
 * — reused by every card and the detail screen's badge, instead of each
 * screen keeping its own partial STATUS_LABELS map with inconsistent
 * coloring (the old all-bookings.tsx rendered every status in amber,
 * NOWA and ZAKONCZONA alike). */
export const BOOKING_STATUS: Record<string, { label: string; tone: StatusTone }> = {
  NOWA: { label: "Nowa", tone: "blue" },
  POTWIERDZONA: { label: "Potwierdzona", tone: "amber" },
  OPLACONA: { label: "Opłacona", tone: "amber" },
  KIEROWCA_W_DRODZE: { label: "W drodze do klienta", tone: "amber" },
  W_TRAKCIE: { label: "W trakcie kursu", tone: "amber" },
  ZAKONCZONA: { label: "Zakończona", tone: "green" },
  ANULOWANA: { label: "Anulowana", tone: "red" },
};

export function bookingStatusInfo(status: string): { label: string; tone: StatusTone } {
  return BOOKING_STATUS[status] ?? { label: status, tone: "muted" };
}
