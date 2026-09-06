import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";

import { LiveMapPanel } from "@/components/live-map-panel";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  robots: {
    index: false,
    follow: false,
  },
};

export default async function LiveTrackingPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("LiveMap");

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <h1 className="font-heading mb-2 text-2xl font-semibold">{t("caption")}</h1>
        <p className="mb-6 text-[14px] text-muted">{t("pageDescription")}</p>
        <LiveMapPanel />
      </main>
      <SiteFooter />
    </>
  );
}
