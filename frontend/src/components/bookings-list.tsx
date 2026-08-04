"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { BookingCancelButton } from "@/components/booking-cancel-button";
import { DepositPaymentForm } from "@/components/deposit-payment-form";
import { Link } from "@/i18n/navigation";
import { formatDistance, netFromGross } from "@/lib/format";
import type { Booking, BookingStatus } from "@/lib/types";
import { useDriverEta } from "@/lib/use-driver-eta";

const BookingRoutePreview = dynamic(
  () => import("./booking-route-preview").then((m) => m.BookingRoutePreview),
  { ssr: false, loading: () => <div className="h-[140px] w-full animate-pulse rounded-lg bg-panel-2" /> },
);

const TRACKABLE_STATUSES = ["KIEROWCA_W_DRODZE", "W_TRAKCIE"];
const CANCELLABLE_STATUSES = ["NOWA", "POTWIERDZONA", "OPLACONA", "KIEROWCA_W_DRODZE"];
const PAID_GATE_STATUSES = ["OPLACONA", "KIEROWCA_W_DRODZE", "W_TRAKCIE", "ZAKONCZONA"];

type Tab = "upcoming" | "history" | "cancelled";

const TAB_STATUSES: Record<Tab, BookingStatus[]> = {
  upcoming: ["NOWA", "POTWIERDZONA", "OPLACONA", "KIEROWCA_W_DRODZE", "W_TRAKCIE"],
  history: ["ZAKONCZONA"],
  cancelled: ["ANULOWANA"],
};

const STATUS_DOT: Record<BookingStatus, string> = {
  NOWA: "bg-amber",
  POTWIERDZONA: "bg-amber",
  OPLACONA: "bg-green",
  KIEROWCA_W_DRODZE: "bg-green",
  W_TRAKCIE: "bg-green",
  ZAKONCZONA: "bg-muted",
  ANULOWANA: "bg-red",
};

const STATUS_COLOR: Record<BookingStatus, string> = {
  NOWA: "text-amber",
  POTWIERDZONA: "text-amber",
  OPLACONA: "text-green",
  KIEROWCA_W_DRODZE: "text-green",
  W_TRAKCIE: "text-green",
  ZAKONCZONA: "text-muted",
  ANULOWANA: "text-red",
};

/** Booking reference shown to the customer — not stored anywhere, just a
 * stable, readable label derived from data we already have. */
function bookingRef(booking: Booking): string {
  const date = new Date(booking.created_at);
  const pad = (n: number) => String(n).padStart(2, "0");
  const y = date.getFullYear();
  const m = pad(date.getMonth() + 1);
  const d = pad(date.getDate());
  return `#DK-${y}${m}${d}-${String(booking.id).padStart(4, "0")}`;
}

function formatCountdown(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const h = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const m = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const s = String(totalSeconds % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

function useCountdown(deadline: string | null): string | null {
  // `now` starts as null so the server-rendered HTML and the client's first
  // hydration pass produce identical output (no countdown text yet) — the
  // real clock value is only read once mounted, avoiding a text mismatch
  // between the server's render time and the client's (React error #418).
  const [now, setNow] = useState<number | null>(null);

  useEffect(() => {
    if (!deadline) return;
    setNow(Date.now());
    const interval = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(interval);
  }, [deadline]);

  if (!deadline || now === null) return null;
  return formatCountdown(new Date(deadline).getTime() - now);
}

function vehicleChip(booking: Booking): string | null {
  if (booking.driver_vehicle) {
    const parts = [booking.driver_vehicle];
    if (booking.driver_vehicle_seats) parts.push(`${booking.driver_vehicle_seats} os.`);
    if (booking.driver_vehicle_plate) parts.push(booking.driver_vehicle_plate);
    return parts.join(" · ");
  }
  return null;
}

// Statuses change from the mobile driver app (confirm/accept/start/finish),
// not from anything the customer does in this tab — without polling, the
// customer would have no way to find out except an SMS/email landing, or a
// manual page reload. 20s keeps the panel feeling live without hammering
// the backend.
const POLL_INTERVAL_MS = 20_000;

export function BookingsList({ bookings: initialBookings, locale }: { bookings: Booking[]; locale: string }) {
  const t = useTranslations("Panel");
  const tStatus = useTranslations("BookingStatus");
  const tPayment = useTranslations("BookingPayment");
  const [tab, setTab] = useState<Tab>("upcoming");
  const [bookings, setBookings] = useState(initialBookings);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("/api/bookings/mine", { cache: "no-store" });
        if (res.ok) setBookings(await res.json());
      } catch {
        // ignore — try again next tick
      }
    }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  if (bookings.length === 0) {
    return <p className="text-muted">{t("empty")}</p>;
  }

  const counts: Record<Tab, number> = {
    upcoming: bookings.filter((b) => TAB_STATUSES.upcoming.includes(b.status)).length,
    history: bookings.filter((b) => TAB_STATUSES.history.includes(b.status)).length,
    cancelled: bookings.filter((b) => TAB_STATUSES.cancelled.includes(b.status)).length,
  };
  const visible = bookings.filter((b) => TAB_STATUSES[tab].includes(b.status));
  const emptyKey = { upcoming: "emptyUpcoming", history: "emptyHistory", cancelled: "emptyCancelled" }[tab] as
    | "emptyUpcoming"
    | "emptyHistory"
    | "emptyCancelled";

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-1 overflow-x-auto overflow-y-hidden border-b border-line">
        {(["upcoming", "history", "cancelled"] as Tab[]).map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`flex shrink-0 items-center gap-1.5 border-b-2 px-1 py-2.5 mr-5 text-[14px] font-semibold whitespace-nowrap transition-colors ${
              tab === key ? "border-amber text-text" : "border-transparent text-muted hover:text-text"
            }`}
          >
            {t(key === "upcoming" ? "tabUpcoming" : key === "history" ? "tabHistory" : "tabCancelled")}
            <span
              className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                tab === key ? "bg-amber/15 text-amber" : "bg-panel-2 text-muted"
              }`}
            >
              {counts[key]}
            </span>
          </button>
        ))}
      </div>

      {visible.length === 0 ? (
        <p className="text-muted">{t(emptyKey)}</p>
      ) : (
        <div className="flex flex-col gap-4">
          {visible.map((booking) => {
            const vehicle = vehicleChip(booking);
            const showUrgency =
              booking.status === "POTWIERDZONA" && booking.payment_deadline && booking.deposit_amount;
            return (
              <BookingCard
                key={booking.id}
                booking={booking}
                locale={locale}
                vehicle={vehicle}
                showUrgency={Boolean(showUrgency)}
                t={t}
                tStatus={tStatus}
                tPayment={tPayment}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

function BookingCard({
  booking,
  locale,
  vehicle,
  showUrgency,
  t,
  tStatus,
  tPayment,
}: {
  booking: Booking;
  locale: string;
  vehicle: string | null;
  showUrgency: boolean;
  t: ReturnType<typeof useTranslations<"Panel">>;
  tStatus: ReturnType<typeof useTranslations<"BookingStatus">>;
  tPayment: ReturnType<typeof useTranslations<"BookingPayment">>;
}) {
  const countdown = useCountdown(showUrgency ? booking.payment_deadline : null);
  const showPaymentButtons = booking.status === "POTWIERDZONA" && booking.deposit_amount;
  const showSecureNote = Boolean(showPaymentButtons || (PAID_GATE_STATUSES.includes(booking.status) && booking.remaining_amount));
  const isTrackable = TRACKABLE_STATUSES.includes(booking.status);
  const eta = useDriverEta(booking.id, isTrackable);

  return (
    <div
      className={`rounded-[14px] border bg-panel p-5 sm:p-[22px] ${
        showUrgency ? "border-amber/35" : "border-line"
      }`}
    >
      <div className="mb-4 flex items-center justify-between gap-2">
        <span className="font-label text-[12px] font-semibold tracking-wide text-muted">{bookingRef(booking)}</span>
        <span
          className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-bold tracking-wide uppercase ${STATUS_COLOR[booking.status]}`}
          style={{ background: "var(--color-panel-2)" }}
        >
          <span className={`h-[6px] w-[6px] rounded-full ${STATUS_DOT[booking.status]}`} />
          {tStatus(booking.status)}
        </span>
      </div>

      <div className="mb-4 flex flex-col gap-0.5">
        <div className="flex gap-3">
          <div className="flex w-3 flex-col items-center pt-1">
            <span className="h-2 w-2 flex-shrink-0 rounded-full bg-amber" />
            <span className="my-0.5 min-h-[16px] w-px flex-1 bg-line" />
          </div>
          <span className="pb-2 text-[14.5px] font-semibold">{booking.pickup_address}</span>
        </div>
        <div className="flex gap-3">
          <div className="flex w-3 flex-col items-center pt-1">
            <span className="h-2 w-2 flex-shrink-0 rounded-full bg-green" />
          </div>
          <span className="text-[14.5px] font-semibold">{booking.dropoff_address}</span>
        </div>
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        <span className="flex items-center gap-1.5 rounded-lg border border-line bg-panel-2 px-2.5 py-1.5 text-[12.5px] text-muted">
          {new Date(booking.scheduled_at).toLocaleString(locale)}
        </span>
        {vehicle && (
          <span className="flex items-center gap-1.5 rounded-lg border border-line bg-panel-2 px-2.5 py-1.5 text-[12.5px] text-text">
            {vehicle}
          </span>
        )}
        {(booking.distance_km || booking.duration_minutes) && (
          <span className="flex items-center gap-1.5 rounded-lg border border-line bg-panel-2 px-2.5 py-1.5 text-[12.5px] text-muted">
            {booking.distance_km && `${booking.distance_km} ${t("km")}`}
            {booking.distance_km && booking.duration_minutes && " · "}
            {booking.duration_minutes && `~${booking.duration_minutes} ${t("min")}`}
          </span>
        )}
      </div>

      {booking.pickup_lat && booking.pickup_lng && booking.dropoff_lat && booking.dropoff_lng && (
        <div className="mb-3">
          <BookingRoutePreview
            pickup={{ lat: Number(booking.pickup_lat), lng: Number(booking.pickup_lng) }}
            dropoff={{ lat: Number(booking.dropoff_lat), lng: Number(booking.dropoff_lng) }}
          />
        </div>
      )}

      {showUrgency && countdown && (
        <div className="mb-3 flex items-center gap-2 rounded-[10px] border border-amber/35 bg-amber/10 px-3.5 py-2.5 text-[13px]">
          {tPayment("urgencyCountdown", {
            time: new Date(booking.payment_deadline!).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" }),
            countdown,
          })}
        </div>
      )}

      {booking.status === "NOWA" && <p className="mb-3 text-[13px] text-muted">{tPayment("waitingForConfirmation")}</p>}

      {showPaymentButtons && (
        <div className="mb-3 rounded-[10px] border border-line bg-panel-2 p-4">
          {booking.price && (
            <div className="mb-3">
              <div className="font-heading text-[20px] font-bold">{Number(booking.price).toFixed(0)} zł</div>
              <div className="text-[11.5px] text-muted">
                {t("vatIncluded", { net: netFromGross(booking.price).toFixed(2) })}
              </div>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            <DepositPaymentForm bookingId={booking.id} amount={booking.deposit_amount!} kind="deposit" showVatNote={false} />
            {booking.price && booking.price !== booking.deposit_amount && (
              <DepositPaymentForm bookingId={booking.id} amount={booking.price} kind="full" showVatNote={false} />
            )}
          </div>
        </div>
      )}

      {PAID_GATE_STATUSES.includes(booking.status) && (
        <div className="mb-3 flex flex-col gap-2">
          {booking.remainder_paid_at ? (
            <p className="text-[13px] text-green">{tPayment("fullyPaid")}</p>
          ) : (
            <>
              <p className="text-[13px] text-green">{tPayment("paidConfirmed")}</p>
              {booking.remaining_amount && (
                <div className="flex flex-col gap-2 rounded-[10px] border border-line bg-panel-2 p-4">
                  <span className="text-[12px] text-muted">
                    {tPayment("remainingAmount", { amount: Number(booking.remaining_amount).toFixed(0) })}
                  </span>
                  <DepositPaymentForm bookingId={booking.id} amount={booking.remaining_amount} kind="remainder" showVatNote={false} />
                </div>
              )}
            </>
          )}
        </div>
      )}

      {isTrackable && (
        <Link
          href={`/panel/kurs/${booking.id}`}
          className="mb-3 flex items-center gap-2 rounded-[10px] bg-amber/10 px-3.5 py-2.5 text-[13px] font-semibold text-amber transition-colors hover:bg-amber/15"
        >
          <span aria-hidden className="text-[15px]">📍</span>
          <span className="flex-1">{t("trackDriver")}</span>
          {eta && (
            <span className="text-[12px] font-semibold whitespace-nowrap text-amber/80">
              ~{Math.round(eta.duration_min)} {t("min")} · {formatDistance(eta.distance_km)}
            </span>
          )}
        </Link>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line pt-3">
        <div className="flex flex-wrap items-center gap-4">
          {booking.status === "ZAKONCZONA" && (
            <Link href="/#routes" className="text-[12.5px] font-semibold text-amber underline">
              {t("bookSimilar")}
            </Link>
          )}
          {CANCELLABLE_STATUSES.includes(booking.status) && <BookingCancelButton bookingId={booking.id} />}
        </div>
        {showSecureNote && <span className="text-[11px] text-muted">{tPayment("securedByStripe")}</span>}
      </div>
    </div>
  );
}
