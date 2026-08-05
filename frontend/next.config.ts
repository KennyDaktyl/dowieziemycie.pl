import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  // Root layout lives at app/[locale]/layout.tsx (a top-level dynamic
  // segment), so a nested app/[locale]/not-found.tsx never fires for a
  // genuinely unmatched path — only global-not-found.tsx does, per Next's
  // own docs for this exact setup.
  experimental: {
    globalNotFound: true,
  },
  async redirects() {
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
