import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

// Photos come from the Django backend's /media/ — in production
// api.dowieziemycie.pl, locally whatever NEXT_PUBLIC_API_BASE_URL points at.
const apiBase = new URL(process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000");

const nextConfig: NextConfig = {
  // Root layout lives at app/[locale]/layout.tsx (a top-level dynamic
  // segment), so a nested app/[locale]/not-found.tsx never fires for a
  // genuinely unmatched path — only global-not-found.tsx does, per Next's
  // own docs for this exact setup.
  experimental: {
    globalNotFound: true,
  },
  // next/image resizes backend photos to the size actually displayed.
  images: {
    formats: ["image/avif", "image/webp"],
    remotePatterns: [new URL("https://api.dowieziemycie.pl/media/**"), new URL(`${apiBase.origin}/media/**`)],
    // Media files never change in place (a new upload gets a new name).
    minimumCacheTTL: 60 * 60 * 24 * 30,
    // Local dev serves media from localhost, which Next blocks by default.
    dangerouslyAllowLocalIP: process.env.NODE_ENV !== "production",
  },
  async redirects() {
    // Locale-prefix redirects (bare "/flota" -> "/pl/flota" etc.) are
    // handled centrally and permanently (308) by proxy.ts for every route,
    // current or future — no need to hand-maintain a matching list here
    // (this list previously did exactly that and had already drifted,
    // missing /kontakt, /regulamin, /logowanie, /sledz, /rezerwacja,
    // /panel, /moje-kursy). Only genuine slug renames belong here.
    //
    // Slugs renamed to include "bus" — barely a day old with no real
    // backlinks yet, but a permanent redirect costs nothing and is correct.
    const renames: Record<string, string> = {
      koncerty: "bus-na-koncert",
      "wieczor-kawalerski": "bus-na-wieczor-kawalerski",
      "wieczor-panienski": "bus-na-wieczor-panienski",
    };
    return Object.entries(renames).map(([oldSlug, newSlug]) => ({
      source: `/:locale(pl|en)/imprezy/${oldSlug}`,
      destination: `/:locale/imprezy/${newSlug}`,
      permanent: true,
    }));
  },
};

export default withNextIntl(nextConfig);
