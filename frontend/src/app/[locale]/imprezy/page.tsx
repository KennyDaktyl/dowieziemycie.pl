import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { BreadcrumbJsonLd } from "@/components/breadcrumb-jsonld";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { FaqJsonLd } from "@/components/faq-jsonld";
import { MarkdownContent } from "@/components/markdown-content";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { WhatsAppButton } from "@/components/whatsapp-button";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { extractFaqPairs } from "@/lib/faq";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { ContentPage } from "@/lib/types";

async function getPage(): Promise<ContentPage | null> {
  return apiFetch<ContentPage>("/api/content-pages/imprezy/", { next: { revalidate: 60 } }).catch(() => null);
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
  return { title, description, alternates: buildAlternates("/imprezy", appLocale) };
}

export default async function ImprezyPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, appLocale, page] = await Promise.all([
    getTranslations("Imprezy"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    getPage(),
  ]);

  if (!page) notFound();

  const title = localize(page, "title", appLocale);
  const body = localize(page, "body", appLocale);
  const faqs = extractFaqPairs(body);
  const breadcrumbItems = [{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("imprezy") }];

  return (
    <>
      <BreadcrumbJsonLd items={breadcrumbItems} locale={locale} />
      <FaqJsonLd faqs={faqs} />
      <SiteHeader />
      <main className="mx-auto max-w-[900px] px-6 py-16">
        <Breadcrumbs items={breadcrumbItems} />
        <h1 className="font-heading mt-3 mb-4 text-[32px] font-semibold md:text-[40px]">{title}</h1>
        <div className="mb-8 flex flex-wrap gap-3">
          <a
            href="tel:+48506029980"
            className="rounded-md bg-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
          >
            {t("callCta")}
          </a>
          <a
            href="https://wa.me/48506029980"
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-amber transition-colors hover:bg-amber/10"
          >
            {t("whatsappCta")}
          </a>
        </div>
        <MarkdownContent markdown={body} />
      </main>
      <SiteFooter />
      <WhatsAppButton />
    </>
  );
}
