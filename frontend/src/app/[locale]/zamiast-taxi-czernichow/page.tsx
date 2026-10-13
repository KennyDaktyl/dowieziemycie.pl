import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { BreadcrumbJsonLd } from "@/components/breadcrumb-jsonld";
import { Breadcrumbs } from "@/components/breadcrumbs";
import { FaqJsonLd } from "@/components/faq-jsonld";
import { MarkdownContent } from "@/components/markdown-content";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { extractFaqPairs } from "@/lib/faq";
import { localize } from "@/lib/localize";
import { formatAmount } from "@/lib/rates";
import { buildAlternates } from "@/lib/seo";
import type { ContactInfo, ContentPage, ExampleFare } from "@/lib/types";

// Google Ads landing page + local SEO for "taxi Czernichów / Rybna /
// Alwernia". The copy (CMS) never calls the service a taxi — see backend
// migration 0079. Prices come from the Admin price list via ExampleFare.
const SLUG = "zamiast-taxi-czernichow";

async function getPage(): Promise<ContentPage | null> {
  return apiFetch<ContentPage>(`/api/content-pages/${SLUG}/`).catch(() => null);
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
  return { title, description, alternates: buildAlternates(`/${SLUG}`, appLocale) };
}

export default async function ZamiastTaxiPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, appLocale, page, contact, fares] = await Promise.all([
    getTranslations("ZamiastTaxi"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    getPage(),
    apiFetch<ContactInfo>("/api/contact-info/"),
    apiFetch<ExampleFare[]>(`/api/example-fares/?group=${SLUG}`).catch(() => [] as ExampleFare[]),
  ]);

  if (!page) notFound();

  const title = localize(page, "title", appLocale);
  const body = localize(page, "body", appLocale);
  const faqs = extractFaqPairs(body);
  const breadcrumbItems = [{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("zamiastTaxi") }];
  const whatsappHref = `https://wa.me/${contact.phone.replace(/\D/g, "")}`;
  // Non-breaking space: "149 zł" never wraps inside a narrow phone column.
  const price = (value: string | number | null) =>
    value == null ? t("individualQuote") : formatAmount(value, appLocale).replace(" ", "\u00a0");

  return (
    <>
      <BreadcrumbJsonLd items={breadcrumbItems} locale={locale} />
      <FaqJsonLd faqs={faqs} />
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs items={breadcrumbItems} />
        <h1 className="font-heading mt-3 mb-6 max-w-[900px] text-[32px] leading-[1.15] font-semibold md:text-[40px]">
          {title}
        </h1>
        <div data-track-location="hero" className="mb-4 flex flex-wrap gap-3">
          <a
            href={`tel:${contact.phone}`}
            className="rounded-md bg-amber px-6 py-4 text-[17px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
          >
            📞 {t("callCta", { phone: contact.phone_display })}
          </a>
          <a
            href={whatsappHref}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-md border border-amber px-6 py-4 text-[17px] font-semibold whitespace-nowrap text-amber transition-colors hover:bg-amber/10"
          >
            WhatsApp
          </a>
        </div>
        <Link href="/rezerwacja" className="text-[14.5px] font-semibold text-amber hover:underline">
          {t("bookCta")} →
        </Link>

        {fares.length > 0 && (
          <section className="mt-10 max-w-[900px]">
            <h2 className="font-heading mb-4 text-[24px] font-semibold">{t("pricesTitle")}</h2>
            <div className="overflow-x-auto rounded-xl border border-line bg-panel">
              <table className="w-full text-left text-[13.5px] sm:text-[14.5px]">
                <thead className="border-b border-line text-muted">
                  <tr>
                    <th className="px-3 py-3 font-semibold sm:px-4">{t("colRoute")}</th>
                    <th className="px-3 py-3 text-right font-semibold sm:px-4">{t("colReserved")}</th>
                    <th className="px-3 py-3 text-right font-semibold sm:px-4">{t("colOnDemand")}</th>
                  </tr>
                </thead>
                <tbody>
                  {fares.map((fare) => (
                    <tr key={`${fare.order}-${fare.from_label_pl}-${fare.to_label_pl}`} className="border-b border-line last:border-0">
                      <td className="px-3 py-3 sm:px-4">
                        {localize(fare, "from_label", appLocale)}{" "}
                        <span className="block text-muted sm:inline sm:text-text">
                          → {localize(fare, "to_label", appLocale)}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right font-semibold text-amber sm:px-4">{price(fare.price_reserved)}</td>
                      <td className="px-3 py-3 text-right sm:px-4">{price(fare.price_on_demand)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-[13px] leading-relaxed text-muted">{t("pricesNote")}</p>
          </section>
        )}

        <div className="mt-10 max-w-[900px]">
          <MarkdownContent markdown={body} locale={appLocale} />
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
