import type { MetadataRoute } from "next";

import { apiFetch } from "@/lib/api";
import { routing } from "@/i18n/routing";
import type { BlogPost, EventOfferListItem, LocalRoute } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

export const dynamic = "force-dynamic";
export const revalidate = 0;

function localizedEntry(path: string, priority: number, changeFrequency: MetadataRoute.Sitemap[number]["changeFrequency"]) {
  return routing.locales.map((locale) => ({
    url: `${SITE_URL}/${locale}${path}`,
    priority,
    changeFrequency,
    alternates: {
      languages: Object.fromEntries(routing.locales.map((l) => [l, `${SITE_URL}/${l}${path}`])),
    },
  }));
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  let routeSlugs: string[] = [];
  let blogSlugs: string[] = [];
  let eventSlugs: string[] = [];
  try {
    const routes = await apiFetch<LocalRoute[]>("/api/routes/", { cache: "no-store" });
    routeSlugs = routes.map((r) => r.slug);
  } catch {
    routeSlugs = [];
  }
  try {
    const posts = await apiFetch<BlogPost[]>("/api/blog/", { cache: "no-store" });
    blogSlugs = posts.map((p) => p.slug);
  } catch {
    blogSlugs = [];
  }
  try {
    const events = await apiFetch<EventOfferListItem[]>("/api/events/", { cache: "no-store" });
    eventSlugs = events.map((e) => e.slug);
  } catch {
    eventSlugs = [];
  }

  return [
    ...localizedEntry("", 1, "daily"),
    ...localizedEntry("/na-zywo", 0.5, "always"),
    ...localizedEntry("/kierunki", 0.9, "weekly"),
    ...localizedEntry("/cennik", 0.8, "weekly"),
    ...localizedEntry("/flota", 0.8, "weekly"),
    ...localizedEntry("/imprezy", 0.9, "weekly"),
    ...localizedEntry("/wynajem-busa-z-kierowca", 0.9, "weekly"),
    ...localizedEntry("/blog", 0.8, "weekly"),
    ...routeSlugs.flatMap((slug) => localizedEntry(`/trasa/${slug}`, 0.8, "weekly")),
    ...eventSlugs.flatMap((slug) => localizedEntry(`/imprezy/${slug}`, 0.8, "weekly")),
    ...blogSlugs.flatMap((slug) => localizedEntry(`/blog/${slug}`, 0.7, "monthly")),
  ];
}
