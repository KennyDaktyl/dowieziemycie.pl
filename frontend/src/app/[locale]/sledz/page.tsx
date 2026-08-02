import { setRequestLocale } from "next-intl/server";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { TrackByCode } from "@/components/track-by-code";

export default async function TrackByCodePage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[900px] px-6 py-16">
        <h1 className="font-heading mb-2 text-center text-2xl font-semibold">Śledź pozycję kierowcy</h1>
        <p className="mb-8 text-center text-[14px] text-muted">
          Wpisz 4-cyfrowy kod, który dostałeś SMS-em od kierowcy — kod jest ważny przez godzinę od przyjęcia kursu.
        </p>
        <TrackByCode />
      </main>
      <SiteFooter />
    </>
  );
}
