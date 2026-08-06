import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { BreadcrumbJsonLd } from "@/components/breadcrumb-jsonld";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { MarkdownContent } from "@/components/markdown-content";
import { PricingTierSection } from "@/components/pricing-tier-section";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { ContentPage } from "@/lib/types";

async function getPage(): Promise<ContentPage | null> {
  return apiFetch<ContentPage>("/api/content-pages/cennik/", { next: { revalidate: 60 } }).catch(() => null);
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const page = await getPage();
  if (!page) return {};
  const appLocale = locale as AppLocale;
  const title = localize(page, "seo_title", appLocale) || localize(page, "title", appLocale);
  const description = localize(page, "seo_description", appLocale);
  return { title, description, alternates: buildAlternates("/cennik", appLocale) };
}

export default async function CennikPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [tCrumbs, appLocale, page] = await Promise.all([
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    getPage(),
  ]);

  if (!page) notFound();

  const title = localize(page, "title", appLocale);
  const body = localize(page, "body", appLocale);
  const breadcrumbItems = [{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("pricing") }];

  return (
    <>
      <BreadcrumbJsonLd items={breadcrumbItems} locale={locale} />
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 pt-16">
        <Breadcrumbs items={breadcrumbItems} />
        <h1 className="font-heading mt-3 mb-4 text-[32px] font-semibold md:text-[40px]">{title}</h1>
        <div className="max-w-[900px]">
          <MarkdownContent markdown={body} />
        </div>
      </main>
      <PricingTierSection />
      <SiteFooter />
    </>
  );
}
