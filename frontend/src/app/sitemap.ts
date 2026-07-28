import type { MetadataRoute } from "next";

import { apiFetch } from "@/lib/api";
import { routing } from "@/i18n/routing";
import type { LocalRoute } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

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
  try {
    const routes = await apiFetch<LocalRoute[]>("/api/routes/");
    routeSlugs = routes.map((r) => r.slug);
  } catch {
    routeSlugs = [];
  }

  return [
    ...localizedEntry("", 1, "daily"),
    ...localizedEntry("/na-zywo", 0.5, "always"),
    ...routeSlugs.flatMap((slug) => localizedEntry(`/trasa/${slug}`, 0.8, "weekly")),
  ];
}
