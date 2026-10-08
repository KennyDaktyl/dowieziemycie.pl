import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { ServicePageView } from "@/components/service-page-view";
import type { AppLocale } from "@/i18n/routing";
import { localize } from "@/lib/localize";
import { GOODS_CATEGORY_SLUG, getServicePage, servicePageMetadata } from "@/lib/service-pages";

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const page = await getServicePage(GOODS_CATEGORY_SLUG);
  return page ? servicePageMetadata(page, locale as AppLocale) : {};
}

export default async function GoodsTransportPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const appLocale = locale as AppLocale;

  const [tCrumbs, page] = await Promise.all([getTranslations("Breadcrumbs"), getServicePage(GOODS_CATEGORY_SLUG)]);
  if (!page) notFound();

  const breadcrumbItems = [
    { label: tCrumbs("home"), href: "/" },
    { label: localize(page, "menu_label", appLocale) || localize(page, "title", appLocale) },
  ];

  return (
    <ServicePageView page={page} locale={appLocale} related={page.children} breadcrumbItems={breadcrumbItems} />
  );
}
