import { apiFetch } from "@/lib/api";
import { routing } from "@/i18n/routing";
import type { BlogPost, EventOfferListItem, LocalRoute } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

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

function localizedUrls(path: string): string[] {
  return routing.locales.map((locale) => `${SITE_URL}/${locale}${path}`);
}

function urlXml(url: string): string {
  return [
    "  <url>",
    `    <loc>${escapeXml(url)}</loc>`,
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

  const urls = [
    ...localizedUrls(""),
    ...localizedUrls("/kierunki"),
    ...localizedUrls("/cennik"),
    ...localizedUrls("/flota"),
    ...localizedUrls("/imprezy"),
    ...localizedUrls("/wynajem-busa-z-kierowca"),
    ...localizedUrls("/blog"),
    ...routeSlugs.flatMap((slug) => localizedUrls(`/trasa/${slug}`)),
    ...eventSlugs.flatMap((slug) => localizedUrls(`/imprezy/${slug}`)),
    ...blogSlugs.flatMap((slug) => localizedUrls(`/blog/${slug}`)),
  ];

  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    urls.map(urlXml).join("\n"),
    "</urlset>",
    "",
  ].join("\n");

  return new Response(body, {
    headers: {
      "Cache-Control": "public, max-age=0, must-revalidate",
      "Content-Type": "application/xml; charset=utf-8",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
