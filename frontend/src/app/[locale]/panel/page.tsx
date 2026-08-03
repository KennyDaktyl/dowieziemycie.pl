import { getTranslations, setRequestLocale } from "next-intl/server";

import { DepositPaymentForm } from "@/components/deposit-payment-form";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Link, redirect } from "@/i18n/navigation";
import { apiBaseUrl, withSiteHeader } from "@/lib/api";
import { getSession } from "@/lib/auth";
import { netFromGross } from "@/lib/format";
import type { Booking } from "@/lib/types";

const TRACKABLE_STATUSES = ["KIEROWCA_W_DRODZE", "W_TRAKCIE"];

export default async function PanelPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, tStatus, tPayment, { customer, accessToken }] = await Promise.all([
    getTranslations("Panel"),
    getTranslations("BookingStatus"),
    getTranslations("BookingPayment"),
    getSession(),
  ]);

  if (!customer || !accessToken) {
    redirect({ href: "/logowanie", locale });
  }

  const res = await fetch(`${apiBaseUrl()}/api/bookings/mine/`, {
    headers: withSiteHeader({ Authorization: `Bearer ${accessToken}` }),
    cache: "no-store",
  });
  const bookings: Booking[] = res.ok ? await res.json() : [];

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[900px] px-6 py-16">
        <h1 className="font-heading mb-8 text-2xl font-semibold">{t("title")}</h1>

        {bookings.length === 0 ? (
          <p className="text-muted">{t("empty")}</p>
        ) : (
          <div className="flex flex-col gap-3">
            {bookings.map((booking) => (
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
                    <DepositPaymentForm bookingId={booking.id} depositAmount={booking.deposit_amount} />
                    {booking.payment_deadline && (
                      <span className="text-[12px] text-muted">
                        {tPayment("payBy", { time: new Date(booking.payment_deadline).toLocaleString(locale) })}
                      </span>
                    )}
                  </div>
                )}

                {booking.status === "OPLACONA" && (
                  <p className="mt-3 text-[13px] text-green">{tPayment("paidConfirmed")}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
