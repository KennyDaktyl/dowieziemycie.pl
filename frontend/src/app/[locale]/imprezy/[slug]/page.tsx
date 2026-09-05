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
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { extractFaqPairs } from "@/lib/faq";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { ContactInfo, EventOffer, EventOfferListItem } from "@/lib/types";

async function getOffers(): Promise<EventOfferListItem[]> {
  return apiFetch<EventOfferListItem[]>("/api/events/", { next: { revalidate: 60 } }).catch(() => []);
}

async function getOffer(slug: string): Promise<EventOffer | null> {
  return apiFetch<EventOffer>(`/api/events/${slug}/`, { next: { revalidate: 60 } }).catch(() => null);
}

export async function generateStaticParams() {
  const offers = await getOffers();
  return offers.map((o) => ({ slug: o.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  const offer = await getOffer(slug);
  if (!offer) return {};
  const appLocale = locale as AppLocale;
  const title = localize(offer, "seo_title", appLocale) || localize(offer, "title", appLocale);
  const description = localize(offer, "seo_description", appLocale) || localize(offer, "excerpt", appLocale);
  return { title, description, alternates: buildAlternates(`/imprezy/${slug}`, appLocale) };
}

export default async function EventOfferPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, appLocale, offer, contact] = await Promise.all([
    getTranslations("Imprezy"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    getOffer(slug),
    apiFetch<ContactInfo>("/api/contact-info/", { next: { revalidate: 60 } }),
  ]);

  if (!offer) notFound();

  const title = localize(offer, "title", appLocale);
  const h1 = localize(offer, "h1", appLocale) || title;
  const body = localize(offer, "body", appLocale);
  const faqs = extractFaqPairs(body);
  const photos = [...offer.photos].sort((a, b) => a.order - b.order);
  const breadcrumbItems = [
    { label: tCrumbs("home"), href: "/" },
    { label: tCrumbs("imprezy"), href: "/imprezy" },
    { label: title },
  ];

  return (
    <>
      <BreadcrumbJsonLd items={breadcrumbItems} locale={locale} />
      <FaqJsonLd faqs={faqs} />
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs items={breadcrumbItems} />
        <Link href="/imprezy" className="mt-3 inline-block text-[13px] font-medium text-amber">
          {t("backToIndex")}
        </Link>
        <h1 className="font-heading mt-3 mb-4 text-[32px] font-semibold md:text-[40px]">
          {offer.icon && <span className="mr-2">{offer.icon}</span>}
          {h1}
        </h1>

        {offer.cover_image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={absoluteImageUrl(offer.cover_image)}
            alt={h1}
            className="mb-8 h-[240px] w-full rounded-[14px] object-cover sm:h-[360px]"
          />
        ) : null}

        {offer.price_from != null && (
          <p className="mb-4 text-[15px] font-bold text-green">
            {t("priceFrom", { price: Number(offer.price_from).toFixed(0) })}
          </p>
        )}

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

        <div className="max-w-[900px]">
          <MarkdownContent markdown={body} />
        </div>

        {photos.length > 0 && (
          <div className="mt-10">
            <h2 className="font-label mb-3 text-xs font-semibold tracking-[0.1em] text-muted uppercase">
              {t("galleryHeading")}
            </h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {photos.map((photo, i) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  key={i}
                  src={absoluteImageUrl(photo.thumbnail || photo.image)}
                  alt={photo.caption || h1}
                  className="h-[140px] w-full rounded-lg object-cover"
                />
              ))}
            </div>
          </div>
        )}
      </main>
      <SiteFooter />
      <WhatsAppButton />
    </>
  );
}
