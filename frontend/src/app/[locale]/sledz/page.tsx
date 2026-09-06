import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { TrackByCode } from "@/components/track-by-code";

export const metadata: Metadata = {
  robots: {
    index: false,
    follow: false,
  },
};

export default async function TrackByCodePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("TrackByCode");

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <h1 className="font-heading mb-2 text-center text-2xl font-semibold">{t("title")}</h1>
        <p className="mb-8 text-center text-[14px] text-muted">{t("lead")}</p>
        <TrackByCode />
      </main>
      <SiteFooter />
    </>
  );
}
