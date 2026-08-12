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
    return [
      { source: "/", destination: "/pl", permanent: true },
      { source: "/na-zywo", destination: "/pl/na-zywo", permanent: true },
      { source: "/kierunki", destination: "/pl/kierunki", permanent: true },
      { source: "/cennik", destination: "/pl/cennik", permanent: true },
      { source: "/flota", destination: "/pl/flota", permanent: true },
      { source: "/blog", destination: "/pl/blog", permanent: true },
      { source: "/blog/:slug", destination: "/pl/blog/:slug", permanent: true },
      { source: "/trasa/:slug", destination: "/pl/trasa/:slug", permanent: true },
      { source: "/imprezy", destination: "/pl/imprezy", permanent: true },
      { source: "/imprezy/:slug", destination: "/pl/imprezy/:slug", permanent: true },
      {
        source: "/wynajem-busa-z-kierowca",
        destination: "/pl/wynajem-busa-z-kierowca",
        permanent: true,
      },
      ...Object.entries(renames).map(([oldSlug, newSlug]) => ({
        source: `/:locale(pl|en)/imprezy/${oldSlug}`,
        destination: `/:locale/imprezy/${newSlug}`,
        permanent: true,
      })),
    ];
  },
};

export default withNextIntl(nextConfig);
