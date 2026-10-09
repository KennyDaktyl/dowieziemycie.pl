import Image from "next/image";
import { getTranslations } from "next-intl/server";

import { BreadcrumbJsonLd } from "@/components/breadcrumb-jsonld";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { FaqJsonLd } from "@/components/faq-jsonld";
import { GoodsPricingTable } from "@/components/goods-pricing-table";
import { MarkdownContent } from "@/components/markdown-content";
import { PricingOptions } from "@/components/pricing-options";
import { ServiceGallery } from "@/components/service-gallery";
import { ServiceJsonLd } from "@/components/service-jsonld";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { TrackedContactLink } from "@/components/tracked-contact-link";
import { TransportInquiryForm } from "@/components/transport-inquiry-form";
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { extractFaqPairs, splitFaqSection } from "@/lib/faq";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import { fillRateTokens, getGoodsPricing } from "@/lib/rates";
import { servicePagePath } from "@/lib/service-pages";
import type { ContactInfo, ServicePage, ServicePageListItem } from "@/lib/types";

/** One layout for every service page — the category (/transport-rzeczy)
 * and its subpages: H1 + lead + contact, cover, pricing cards, Markdown
 * body, gallery, FAQ as <details> (no JS), related pages and the inquiry
 * form. Server-rendered; only the form, gallery and option buttons ship JS. */
export async function ServicePageView({
  page,
  locale,
  related,
  breadcrumbItems,
}: {
  page: ServicePage;
  locale: AppLocale;
  related: ServicePageListItem[];
  breadcrumbItems: { label: string; href?: string }[];
}) {
  const [t, contact, pricing] = await Promise.all([
    getTranslations("Transport"),
    apiFetch<ContactInfo>("/api/contact-info/"),
    getGoodsPricing(),
  ]);
  const fill = (text: string) => fillRateTokens(text, pricing, locale);

  const path = servicePagePath(page);
  const title = localize(page, "title", locale);
  const h1 = localize(page, "h1", locale) || title;
  const lead = fill(localize(page, "lead", locale));
  const body = fill(localize(page, "body", locale));
  const description = fill(localize(page, "seo_description", locale)) || lead;
  const faq = splitFaqSection(body);
  const photos = page.photos.map((photo) => ({
    src: photo.image,
    thumbnailSrc: photo.thumbnail || photo.image,
    width: photo.width ?? 1600,
    height: photo.height ?? 1200,
    alt: localize(photo, "alt", locale) || h1,
    caption: localize(photo, "caption", locale),
  }));
  const whatsappHref = `https://wa.me/${contact.phone.replace(/\D/g, "")}`;
  // "+48515020770" -> "+48 515 020 770" for the button label.
  const phoneLabel = contact.phone.replace(/^(\+48)(\d{3})(\d{3})(\d{3})$/, "$1 $2 $3 $4");

  return (
    <>
      <BreadcrumbJsonLd items={breadcrumbItems} locale={locale} />
      <FaqJsonLd faqs={extractFaqPairs(body)} />
      <ServiceJsonLd
        name={h1}
        description={description}
        path={`/${locale}${path}`}
        phone={contact.phone}
        image={page.cover_image ? absoluteImageUrl(page.cover_image) : undefined}
        options={page.pricing_options}
      />
      <SiteHeader />
      <main className="px-6 py-[70px]">
        <div className="mx-auto max-w-[1360px]">
          <Breadcrumbs items={breadcrumbItems} />
          <h1 className="font-heading mt-3 mb-4 max-w-[900px] text-[32px] leading-[1.15] font-semibold md:text-[40px]">
            {h1}
          </h1>
          {lead && <p className="max-w-[760px] text-[16.5px] leading-relaxed text-muted">{lead}</p>}

          <div className="mt-6 flex flex-wrap gap-3">
            <a
              href="#zapytanie"
              className="rounded-md bg-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
            >
              {t("ctaForm")}
            </a>
            <TrackedContactLink
              kind="call"
              href={`tel:${contact.phone}`}
              pageSlug={page.slug}
              className="rounded-md border border-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-amber transition-colors hover:bg-amber/10"
            >
              {t("ctaCall", { phone: phoneLabel })}
            </TrackedContactLink>
            <TrackedContactLink
              kind="whatsapp"
              href={whatsappHref}
              pageSlug={page.slug}
              className="rounded-md border border-line px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-text transition-colors hover:border-amber"
            >
              WhatsApp
            </TrackedContactLink>
          </div>

          {page.cover_image && (
            <Image
              src={absoluteImageUrl(page.cover_image)}
              alt={h1}
              width={1360}
              height={560}
              sizes="(max-width: 1408px) 100vw, 1360px"
              loading="eager"
              fetchPriority="high"
              className="mt-8 h-[240px] w-full rounded-[14px] object-cover sm:h-[380px]"
            />
          )}

          <PricingOptions options={page.pricing_options} locale={locale} pricing={pricing} />
          {pricing && page.pricing_options.length > 0 && <GoodsPricingTable pricing={pricing} locale={locale} />}

          <div className="mt-10 max-w-[900px]">
            <MarkdownContent markdown={faq.before} locale={locale} />
          </div>

          {photos.length > 0 && (
            <section aria-labelledby="gallery-heading" className="mt-12">
              <h2 id="gallery-heading" className="font-heading mb-4 text-[24px] font-semibold">
                {t("galleryHeading")}
              </h2>
              <ServiceGallery photos={photos} openLabel={t("galleryOpen")} />
            </section>
          )}

          {faq.pairs.length > 0 && (
            <section aria-labelledby="faq-heading" className="mt-12 max-w-[900px]">
              <h2 id="faq-heading" className="font-heading mb-4 text-[24px] font-semibold">
                {faq.heading}
              </h2>
              <div className="divide-y divide-line rounded-xl border border-line">
                {faq.pairs.map((pair) => (
                  <details key={pair.question} className="group px-5 py-4">
                    <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-[15.5px] font-semibold">
                      {pair.question}
                      <span aria-hidden className="text-amber transition-transform group-open:rotate-45">
                        +
                      </span>
                    </summary>
                    <div className="mt-3 text-[14.5px] text-muted">
                      <MarkdownContent markdown={pair.answerMarkdown} locale={locale} />
                    </div>
                  </details>
                ))}
              </div>
            </section>
          )}
          {faq.after && (
            <div className="mt-8 max-w-[900px]">
              <MarkdownContent markdown={faq.after} locale={locale} />
            </div>
          )}

          {related.length > 0 && (
            <nav aria-labelledby="related-heading" className="mt-12">
              <h2 id="related-heading" className="font-heading mb-4 text-[20px] font-semibold">
                {t("seeAlso")}
              </h2>
              <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {related.map((item) => (
                  <li key={item.slug}>
                    <Link
                      href={servicePagePath(item)}
                      className="block h-full rounded-xl border border-line bg-panel p-5 transition-colors hover:border-amber"
                    >
                      <span className="text-[16px] font-semibold">{localize(item, "title", locale)}</span>
                      <span className="mt-1.5 line-clamp-2 block text-[13.5px] text-muted">
                        {localize(item, "lead", locale)}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          )}

          <section id="zapytanie" aria-labelledby="inquiry-heading" className="mt-14 scroll-mt-28 max-w-[900px]">
            <h2 id="inquiry-heading" className="font-heading text-[26px] font-semibold">
              {t("formHeading")}
            </h2>
            <p className="mt-2 mb-6 text-[14.5px] leading-relaxed text-muted">{t("formLead")}</p>
            <div className="rounded-xl border border-line bg-panel p-5 sm:p-7">
              <TransportInquiryForm
                pageSlug={page.slug}
                locale={locale}
                defaultItemType={page.default_item_type}
                phone={contact.phone}
              />
            </div>
          </section>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
