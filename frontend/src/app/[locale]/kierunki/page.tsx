import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";

import { Breadcrumbs } from "@/components/breadcrumbs";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { buildAlternates } from "@/lib/seo";
import type { LocalRoute } from "@/lib/types";

async function getRoutes(): Promise<LocalRoute[]> {
  return apiFetch<LocalRoute[]>("/api/routes/", { next: { revalidate: 60 } }).catch(() => []);
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Routes" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: buildAlternates("/kierunki", locale as AppLocale),
  };
}

export default async function KierunkiPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, routes] = await Promise.all([
    getTranslations("Routes"),
    getTranslations("Breadcrumbs"),
    getRoutes(),
  ]);

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs items={[{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("routes") }]} />
        <div className="mt-3 mb-10 max-w-[640px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h1 className="font-heading mt-2.5 text-[32px] font-semibold md:text-[40px]">{t("title")}</h1>
          <p className="mt-3 text-[15.5px] leading-relaxed text-muted">{t("description")}</p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {routes.map((route) => (
            <Link
              key={route.slug}
              href={`/trasa/${route.slug}`}
              className="rounded-[14px] border border-line bg-panel p-5 transition-colors hover:border-amber"
            >
              <h2 className="font-heading mb-1.5 text-[17px] font-semibold">
                Kraków ↔ {route.destination_town}
              </h2>
              <p className="mb-4 text-[13.5px] leading-relaxed text-muted">
                {locale === "en" ? route.lead_en : route.lead_pl}
              </p>
              {route.example_price != null ? (
                <div className="font-heading text-[16px] font-bold text-green">
                  {t("priceFrom", { price: route.example_price.toFixed(0) })}
                </div>
              ) : (
                <div className="font-heading text-[16px] font-bold text-muted">{t("customQuote")}</div>
              )}
              <span className="mt-3.5 inline-block text-[13px] font-semibold text-amber">{t("cta")}</span>
            </Link>
          ))}
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
