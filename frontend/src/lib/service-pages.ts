import type { Metadata } from "next";

import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { ServicePage, ServicePageListItem } from "@/lib/types";

export const GOODS_CATEGORY_SLUG = "transport-rzeczy";

export async function getServicePage(slug: string): Promise<ServicePage | null> {
  return apiFetch<ServicePage>(`/api/service-pages/${slug}/`).catch(() => null);
}

export async function getServicePages(query = ""): Promise<ServicePageListItem[]> {
  return apiFetch<ServicePageListItem[]>(`/api/service-pages/${query}`).catch(() => []);
}

/** URL path (no locale) of a service page: category at /<slug>, subpage
 * at /<parent>/<slug>. */
export function servicePagePath(page: Pick<ServicePageListItem, "slug" | "parent_slug">): string {
  return page.parent_slug ? `/${page.parent_slug}/${page.slug}` : `/${page.slug}`;
}

export function servicePageMetadata(page: ServicePage, locale: AppLocale): Metadata {
  const title = localize(page, "seo_title", locale) || localize(page, "title", locale);
  const description = localize(page, "seo_description", locale) || localize(page, "lead", locale);
  return {
    title,
    description,
    alternates: buildAlternates(servicePagePath(page), locale),
    ...(page.noindex ? { robots: { index: false, follow: true } } : {}),
    openGraph: {
      title,
      description,
      ...(page.cover_image ? { images: [{ url: absoluteImageUrl(page.cover_image) }] } : {}),
    },
  };
}
