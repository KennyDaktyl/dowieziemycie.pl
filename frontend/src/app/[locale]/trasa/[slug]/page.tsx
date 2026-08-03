import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { Link } from "@/i18n/navigation";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { apiFetch } from "@/lib/api";
import type { LocalRoute } from "@/lib/types";

async function getRoute(slug: string): Promise<LocalRoute | null> {
  try {
    return await apiFetch<LocalRoute>(`/api/routes/${slug}/`, { next: { revalidate: 60 } });
  } catch {
    return null;
  }
}

export async function generateStaticParams() {
  try {
    const routes = await apiFetch<LocalRoute[]>("/api/routes/");
    return routes.map((r) => ({ slug: r.slug }));
  } catch {
    return [];
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  const route = await getRoute(slug);
  if (!route) return {};

  const seoTitle = locale === "en" ? route.seo_title_en : route.seo_title_pl;
  const seoDescription = locale === "en" ? route.seo_description_en : route.seo_description_pl;
  const title = locale === "en" ? route.title_en : route.title_pl;
  const description = locale === "en" ? route.lead_en : route.lead_pl;

  return {
    title: seoTitle || title,
    description: seoDescription || description,
  };
}

export default async function RoutePage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, allRoutes, route] = await Promise.all([
    getTranslations("RoutePage"),
    getTranslations("Breadcrumbs"),
    apiFetch<LocalRoute[]>("/api/routes/", { next: { revalidate: 60 } }),
    getRoute(slug),
  ]);

  if (!route) notFound();

  const title = locale === "en" ? route.title_en : route.title_pl;
  const lead = locale === "en" ? route.lead_en : route.lead_pl;
  const body = locale === "en" ? route.body_en : route.body_pl;
  const otherRoutes = allRoutes.filter((r) => r.slug !== route.slug);

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs
          items={[
            { label: tCrumbs("home"), href: "/" },
            { label: tCrumbs("routes"), href: "/#routes" },
            { label: title },
          ]}
        />

        <Link href="/#routes" className="mt-3 mb-6 inline-block text-[13px] font-semibold text-amber">
          {t("backToHome")}
        </Link>

        <h1 className="font-heading mb-4 text-[34px] leading-[1.08] font-semibold tracking-tight md:text-[44px]">
          {title}
        </h1>
        <p className="mb-8 text-[17px] leading-relaxed text-muted">{lead}</p>

        <div className="mb-8 flex flex-wrap items-center justify-between gap-4 rounded-[14px] border border-line bg-panel p-6">
          <div>
            <div className="font-label text-xs font-semibold tracking-[0.1em] text-muted uppercase">
              {t("exampleTitle")}
            </div>
            <div className="mt-0.5 text-[11.5px] text-muted">{t("exampleFrom")}</div>
          </div>
          <div className="text-right">
            {route.example_price != null ? (
              <>
                <div className="font-heading text-3xl font-bold text-green">
                  {route.example_price.toFixed(0)} zł
                </div>
                <div className="text-xs text-muted">{t("vatNote")}</div>
              </>
            ) : (
              <div className="font-heading text-xl font-semibold text-muted">
                {locale === "en" ? "Custom quote" : "Wycena indywidualna"}
              </div>
            )}
            <div className="font-label mt-0.5 text-xs text-muted">
              {t("exampleDistance", { km: route.example_distance_km })}
            </div>
          </div>
        </div>

        {body && (
          <div className="mb-10 flex flex-col gap-4 text-[15.5px] leading-relaxed text-muted">
            {body.split("\n").filter(Boolean).map((paragraph, i) => (
              <p key={i}>{paragraph}</p>
            ))}
          </div>
        )}

        <Link
          href="/#routes"
          className="mb-14 inline-block rounded-[9px] bg-amber px-6 py-[15px] text-[15.5px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)]"
        >
          {t("bookCta")}
        </Link>

        {otherRoutes.length > 0 && (
          <div className="border-t border-line pt-10">
            <h2 className="font-heading mb-4 text-lg font-semibold">{t("otherRoutes")}</h2>
            <div className="flex flex-wrap gap-2">
              {otherRoutes.map((r) => (
                <Link
                  key={r.slug}
                  href={`/trasa/${r.slug}`}
                  className="rounded-full border border-line px-4 py-2 text-[13.5px] text-muted transition-colors hover:border-amber hover:text-text"
                >
                  Kraków ↔ {r.destination_town}
                </Link>
              ))}
            </div>
          </div>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
