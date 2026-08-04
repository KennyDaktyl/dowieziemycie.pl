import type { AppLocale } from "@/i18n/routing";
import { routing } from "@/i18n/routing";

export function siteUrl(): string {
  return process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";
}

export function buildAlternates(path: string, locale: AppLocale) {
  const languages: Record<string, string> = {};
  for (const loc of routing.locales) {
    languages[loc] = `${siteUrl()}/${loc}${path}`;
  }
  languages["x-default"] = `${siteUrl()}/${routing.defaultLocale}${path}`;
  return { canonical: `${siteUrl()}/${locale}${path}`, languages };
}
