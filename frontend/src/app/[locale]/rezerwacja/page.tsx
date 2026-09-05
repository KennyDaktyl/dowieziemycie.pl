import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";

import { Breadcrumbs } from "@/components/breadcrumbs";
import { BookingCard } from "@/components/booking-card";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { buildAlternates } from "@/lib/seo";
import type { ContactInfo } from "@/lib/types";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Rezerwacja" });
  return {
    title: t("seoTitle"),
    description: t("seoDescription"),
    alternates: buildAlternates("/rezerwacja", locale as AppLocale),
  };
}

export default async function RezerwacjaPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, contact] = await Promise.all([
    getTranslations("Rezerwacja"),
    getTranslations("Breadcrumbs"),
    apiFetch<ContactInfo>("/api/contact-info/", { next: { revalidate: 60 } }),
  ]);

  return (
    <>
      <SiteHeader />
      <main className="px-6 pt-16 pb-20">
        <div className="mx-auto max-w-[1360px]">
          <Breadcrumbs items={[{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("booking") }]} />
          <h1 className="font-heading mt-3 mb-3 text-[32px] font-semibold md:text-[40px]">{t("title")}</h1>
          <p className="mb-10 max-w-[560px] text-[15.5px] leading-relaxed text-muted">{t("lead")}</p>
          <BookingCard contact={contact} />
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
