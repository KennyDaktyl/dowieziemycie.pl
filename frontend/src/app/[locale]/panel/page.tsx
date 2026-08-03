import { getTranslations, setRequestLocale } from "next-intl/server";

import { BookingsList } from "@/components/bookings-list";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { redirect } from "@/i18n/navigation";
import { apiBaseUrl, withSiteHeader } from "@/lib/api";
import { getSession } from "@/lib/auth";
import type { Booking } from "@/lib/types";

export default async function PanelPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, { customer, accessToken }] = await Promise.all([getTranslations("Panel"), getSession()]);

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
        <BookingsList bookings={bookings} locale={locale} />
      </main>
      <SiteFooter />
    </>
  );
}
