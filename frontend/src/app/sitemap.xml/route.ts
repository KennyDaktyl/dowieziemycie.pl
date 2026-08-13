import { apiFetch } from "@/lib/api";
import { routing } from "@/i18n/routing";
import type { BlogPost, EventOfferListItem, LocalRoute } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

type Entry = {
  path: string;
  priority: number;
  changeFrequency: "always" | "daily" | "weekly" | "monthly";
};

export const dynamic = "force-dynamic";
export const revalidate = 0;

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function localizedEntries(path: string, priority: number, changeFrequency: Entry["changeFrequency"]): Entry[] {
  return routing.locales.map((locale) => ({ path: `/${locale}${path}`, priority, changeFrequency }));
}

function urlXml(entry: Entry): string {
  const url = `${SITE_URL}${entry.path}`;
  const alternatePath = entry.path.replace(/^\/(pl|en)/, "");
  const alternates = routing.locales
    .map((locale) => {
      const href = `${SITE_URL}/${locale}${alternatePath}`;
      return `    <xhtml:link rel="alternate" hreflang="${locale}" href="${escapeXml(href)}" />`;
    })
    .join("\n");

  return [
    "  <url>",
    `    <loc>${escapeXml(url)}</loc>`,
    alternates,
    `    <changefreq>${entry.changeFrequency}</changefreq>`,
    `    <priority>${entry.priority}</priority>`,
    "  </url>",
  ].join("\n");
}

async function getSlugs<T extends { slug: string }>(path: string): Promise<string[]> {
  try {
    const items = await apiFetch<T[]>(path, { cache: "no-store" });
    return items.map((item) => item.slug);
  } catch {
    return [];
  }
}

export async function GET() {
  const [routeSlugs, blogSlugs, eventSlugs] = await Promise.all([
    getSlugs<LocalRoute>("/api/routes/"),
    getSlugs<BlogPost>("/api/blog/"),
    getSlugs<EventOfferListItem>("/api/events/"),
  ]);

  const entries = [
    ...localizedEntries("", 1, "daily"),
    ...localizedEntries("/na-zywo", 0.5, "always"),
    ...localizedEntries("/kierunki", 0.9, "weekly"),
    ...localizedEntries("/cennik", 0.8, "weekly"),
    ...localizedEntries("/flota", 0.8, "weekly"),
    ...localizedEntries("/imprezy", 0.9, "weekly"),
    ...localizedEntries("/wynajem-busa-z-kierowca", 0.9, "weekly"),
    ...localizedEntries("/blog", 0.8, "weekly"),
    ...routeSlugs.flatMap((slug) => localizedEntries(`/trasa/${slug}`, 0.8, "weekly")),
    ...eventSlugs.flatMap((slug) => localizedEntries(`/imprezy/${slug}`, 0.8, "weekly")),
    ...blogSlugs.flatMap((slug) => localizedEntries(`/blog/${slug}`, 0.7, "monthly")),
  ];

  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    entries.map(urlXml).join("\n"),
    "</urlset>",
    "",
  ].join("\n");

  return new Response(body, {
    headers: {
      "Cache-Control": "public, max-age=0, must-revalidate",
      "Content-Type": "application/xml; charset=utf-8",
    },
  });
}
