"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { DepositPaymentForm } from "@/components/deposit-payment-form";
import { Link } from "@/i18n/navigation";
import { netFromGross } from "@/lib/format";
import type { Booking } from "@/lib/types";

const TRACKABLE_STATUSES = ["KIEROWCA_W_DRODZE", "W_TRAKCIE"];
const ARCHIVE_STATUSES = ["ZAKONCZONA", "ANULOWANA"];
const PAID_GATE_STATUSES = ["OPLACONA", "KIEROWCA_W_DRODZE", "W_TRAKCIE", "ZAKONCZONA"];

export function BookingsList({ bookings, locale }: { bookings: Booking[]; locale: string }) {
  const t = useTranslations("Panel");
  const tStatus = useTranslations("BookingStatus");
  const tPayment = useTranslations("BookingPayment");
  const [showArchive, setShowArchive] = useState(false);

  const archiveCount = bookings.filter((b) => ARCHIVE_STATUSES.includes(b.status)).length;
  const visible = showArchive ? bookings : bookings.filter((b) => !ARCHIVE_STATUSES.includes(b.status));

  if (bookings.length === 0) {
    return <p className="text-muted">{t("empty")}</p>;
  }

  return (
    <div className="flex flex-col gap-3">
      {archiveCount > 0 && (
        <button
          type="button"
          onClick={() => setShowArchive((v) => !v)}
          className="self-start text-[12.5px] font-semibold text-amber underline"
        >
          {showArchive ? t("hideArchive") : t("showArchive", { count: archiveCount })}
        </button>
      )}

      {visible.length === 0 ? (
        <p className="text-muted">{t("emptyCurrent")}</p>
      ) : (
        visible.map((booking) => (
          <div key={booking.id} className="rounded-[12px] border border-line bg-panel p-5">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <span className="font-heading text-[15px] font-semibold">
                {booking.pickup_address} → {booking.dropoff_address}
              </span>
              <span className="font-label rounded-full border border-line px-2.5 py-1 text-[11px] font-semibold tracking-wide text-amber uppercase">
                {tStatus(booking.status)}
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-[13px] text-muted">
              <span>
                {t("date")}: {new Date(booking.scheduled_at).toLocaleString(locale)}
              </span>
              <span>
                {t("price")}:{" "}
                {booking.price
                  ? `${Number(booking.price).toFixed(0)} zł (${t("vatIncluded", { net: netFromGross(booking.price).toFixed(2) })})`
                  : "—"}
              </span>
              {TRACKABLE_STATUSES.includes(booking.status) && (
                <Link href={`/panel/kurs/${booking.id}`} className="font-semibold text-amber underline">
                  {t("trackDriver")}
                </Link>
              )}
            </div>

            {booking.status === "NOWA" && (
              <p className="mt-3 text-[13px] text-muted">{tPayment("waitingForConfirmation")}</p>
            )}

            {booking.status === "POTWIERDZONA" && booking.deposit_amount && (
              <div className="mt-3 flex flex-col gap-2">
                <DepositPaymentForm bookingId={booking.id} amount={booking.deposit_amount} kind="deposit" />
                {booking.price && booking.price !== booking.deposit_amount && (
                  <>
                    <span className="text-[12px] text-muted">{tPayment("orPayFull")}</span>
                    <DepositPaymentForm
                      bookingId={booking.id}
                      amount={booking.price}
                      kind="full"
                      showVatNote={false}
                    />
                  </>
                )}
                {booking.payment_deadline && (
                  <span className="text-[12px] text-muted">
                    {tPayment("payBy", { time: new Date(booking.payment_deadline).toLocaleString(locale) })}
                  </span>
                )}
              </div>
            )}

            {PAID_GATE_STATUSES.includes(booking.status) && (
              <div className="mt-3 flex flex-col gap-2">
                {booking.remainder_paid_at ? (
                  <p className="text-[13px] text-green">{tPayment("fullyPaid")}</p>
                ) : (
                  <>
                    <p className="text-[13px] text-green">{tPayment("paidConfirmed")}</p>
                    {booking.remaining_amount && (
                      <div className="flex flex-col gap-2">
                        <span className="text-[12px] text-muted">
                          {tPayment("remainingAmount", { amount: Number(booking.remaining_amount).toFixed(0) })}
                        </span>
                        <DepositPaymentForm
                          bookingId={booking.id}
                          amount={booking.remaining_amount}
                          kind="remainder"
                          showVatNote={false}
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
