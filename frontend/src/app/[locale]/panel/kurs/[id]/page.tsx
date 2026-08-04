import { getTranslations, setRequestLocale } from "next-intl/server";

import { BookingTracker } from "@/components/booking-tracker";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { redirect } from "@/i18n/navigation";
import { apiBaseUrl, withSiteHeader } from "@/lib/api";
import { getSession } from "@/lib/auth";
import type { Booking } from "@/lib/types";

const TRACKABLE_STATUSES = ["KIEROWCA_W_DRODZE", "W_TRAKCIE"];

export default async function BookingTrackingPage({
  params,
}: {
  params: Promise<{ locale: string; id: string }>;
}) {
  const { locale, id } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, { customer, accessToken }] = await Promise.all([
    getTranslations("Panel"),
    getTranslations("Breadcrumbs"),
    getSession(),
  ]);

  if (!customer || !accessToken) {
    return redirect({ href: "/logowanie", locale });
  }

  const res = await fetch(`${apiBaseUrl()}/api/bookings/mine/`, {
    headers: withSiteHeader({ Authorization: `Bearer ${accessToken}` }),
    cache: "no-store",
  });
  const bookings: Booking[] = res.ok ? await res.json() : [];
  const booking = bookings.find((b) => String(b.id) === id);

  if (!booking || !TRACKABLE_STATUSES.includes(booking.status)) {
    return redirect({ href: "/panel", locale });
  }

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs
          items={[
            { label: tCrumbs("home"), href: "/" },
            { label: tCrumbs("myTrips"), href: "/panel" },
            { label: tCrumbs("tracking") },
          ]}
        />
        <h1 className="font-heading mt-3 mb-2 text-2xl font-semibold">{t("trackingTitle")}</h1>
        <p className="mb-6 text-[14px] text-muted">
          {booking.pickup_address} → {booking.dropoff_address}
        </p>
        <BookingTracker
          bookingId={booking.id}
          accessToken={accessToken}
          driverName={booking.driver_name}
          driverVehicle={booking.driver_vehicle}
        />
      </main>
      <SiteFooter />
    </>
  );
}
