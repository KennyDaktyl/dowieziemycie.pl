import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { ServicePageView } from "@/components/service-page-view";
import type { AppLocale } from "@/i18n/routing";
import { localize } from "@/lib/localize";
import { GOODS_CATEGORY_SLUG, getServicePage, getServicePages, servicePageMetadata } from "@/lib/service-pages";

export async function generateStaticParams() {
  const pages = await getServicePages(`?parent=${GOODS_CATEGORY_SLUG}`);
  return pages.map((page) => ({ slug: page.slug }));
}

async function getSubpage(slug: string) {
  const page = await getServicePage(slug);
  return page && page.parent_slug === GOODS_CATEGORY_SLUG ? page : null;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  const page = await getSubpage(slug);
  return page ? servicePageMetadata(page, locale as AppLocale) : {};
}

export default async function GoodsTransportSubpage({ params }: { params: Promise<{ locale: string; slug: string }> }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const appLocale = locale as AppLocale;

  const [tCrumbs, page, siblings] = await Promise.all([
    getTranslations("Breadcrumbs"),
    getSubpage(slug),
    getServicePages(`?parent=${GOODS_CATEGORY_SLUG}`),
  ]);
  if (!page) notFound();

  const parentLabel = localize(
    { menu_label_pl: page.parent_menu_label_pl ?? "", menu_label_en: page.parent_menu_label_en ?? "" },
    "menu_label",
    appLocale,
  );
  const breadcrumbItems = [
    { label: tCrumbs("home"), href: "/" },
    { label: parentLabel, href: `/${GOODS_CATEGORY_SLUG}` },
    { label: localize(page, "menu_label", appLocale) || localize(page, "title", appLocale) },
  ];

  return (
    <ServicePageView
      page={page}
      locale={appLocale}
      related={siblings.filter((sibling) => sibling.slug !== page.slug)}
      breadcrumbItems={breadcrumbItems}
    />
  );
}
