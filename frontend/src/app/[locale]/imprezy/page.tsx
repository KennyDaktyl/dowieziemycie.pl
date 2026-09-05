import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { BreadcrumbJsonLd } from "@/components/breadcrumb-jsonld";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { MarkdownContent } from "@/components/markdown-content";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { WhatsAppButton } from "@/components/whatsapp-button";
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { ContactInfo, ContentPage, EventOfferListItem } from "@/lib/types";

async function getPage(): Promise<ContentPage | null> {
  return apiFetch<ContentPage>("/api/content-pages/imprezy/", { next: { revalidate: 60 } }).catch(() => null);
}

async function getOffers(): Promise<EventOfferListItem[]> {
  return apiFetch<EventOfferListItem[]>("/api/events/", { next: { revalidate: 60 } }).catch(() => []);
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

  const [t, tCrumbs, appLocale, page, offers, contact] = await Promise.all([
    getTranslations("Imprezy"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    getPage(),
    getOffers(),
    apiFetch<ContactInfo>("/api/contact-info/", { next: { revalidate: 60 } }),
  ]);

  if (!page) notFound();

  const title = localize(page, "title", appLocale);
  const body = localize(page, "body", appLocale);
  const breadcrumbItems = [{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("imprezy") }];

  return (
    <>
      <BreadcrumbJsonLd items={breadcrumbItems} locale={locale} />
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs items={breadcrumbItems} />
        <h1 className="font-heading mt-3 mb-4 text-[32px] font-semibold md:text-[40px]">{title}</h1>
        <div className="mb-8 flex flex-wrap gap-3">
          <a
            href={`tel:${contact.phone}`}
            className="rounded-md bg-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
          >
            {t("callCta")}
          </a>
          <a
            href={`https://wa.me/${contact.phone.replace(/\D/g, "")}`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-amber transition-colors hover:bg-amber/10"
          >
            {t("whatsappCta")}
          </a>
        </div>
        <div className="max-w-[720px]">
          <MarkdownContent markdown={body} />
        </div>

        {offers.length > 0 && (
          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {offers.map((offer) => (
              <Link
                key={offer.slug}
                href={`/imprezy/${offer.slug}`}
                className="group overflow-hidden rounded-xl border border-line bg-panel transition-colors hover:border-amber"
              >
                {offer.cover_image ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={absoluteImageUrl(offer.cover_image)}
                    alt={localize(offer, "title", appLocale)}
                    className="h-[160px] w-full object-cover"
                  />
                ) : null}
                <div className="p-6">
                  {offer.icon && <span className="text-[28px]">{offer.icon}</span>}
                  <h2 className="mt-3 text-[18px] font-semibold">{localize(offer, "title", appLocale)}</h2>
                  <p className="mt-2 text-[13.5px] leading-relaxed text-muted">
                    {localize(offer, "excerpt", appLocale)}
                  </p>
                  {offer.price_from != null && (
                    <p className="mt-2 text-[13.5px] font-bold text-green">
                      {t("priceFrom", { price: Number(offer.price_from).toFixed(0) })}
                    </p>
                  )}
                  <span className="mt-4 inline-block text-[13.5px] font-semibold text-amber group-hover:underline">
                    {t("seeMore")} →
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
      <SiteFooter />
      <WhatsAppButton />
    </>
  );
}
