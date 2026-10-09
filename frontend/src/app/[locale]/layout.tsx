import type { Metadata } from "next";
import { NextIntlClientProvider, hasLocale } from "next-intl";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";
import { Barlow_Condensed, Inter, Space_Grotesk } from "next/font/google";

import { WhatsAppButton } from "@/components/whatsapp-button";
import { routing } from "@/i18n/routing";
import { AnalyticsScripts } from "@/components/analytics-scripts";
import { CookieConsentBanner } from "@/components/cookie-consent-banner";
import "./globals.css";

// Inter and Space Grotesk are variable fonts: with no `weight` list each
// subset is ONE file covering 100–900, instead of one file per weight — this
// cut the fonts fetched before first render from 10 files (~250 KB) and was
// the main cause of a 4 s mobile LCP (the LCP is body text waiting for them).
const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "latin-ext"],
  display: "swap",
});

// Small uppercase labels only — never the LCP, so not preloaded.
const barlowCondensed = Barlow_Condensed({
  variable: "--font-barlow-condensed",
  subsets: ["latin", "latin-ext"],
  weight: ["500", "600", "700"],
  display: "swap",
  preload: false,
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Metadata" });
  return { title: t("title"), description: t("description"), metadataBase: new URL(SITE_URL) };
}

export default async function LocaleLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}>) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }
  setRequestLocale(locale);

  return (
    <html
      lang={locale}
      className={`${spaceGrotesk.variable} ${inter.variable} ${barlowCondensed.variable} overflow-x-hidden antialiased`}
    >
      <body className="bg-bg text-text min-h-screen overflow-x-hidden" suppressHydrationWarning>
        <AnalyticsScripts />
        <NextIntlClientProvider>
          {children}
          <WhatsAppButton />
          <CookieConsentBanner />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
