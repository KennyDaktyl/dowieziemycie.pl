import { NextResponse } from "next/server";
import createIntlMiddleware from "next-intl/middleware";

import { routing } from "./i18n/routing";

const intlMiddleware = createIntlMiddleware(routing);

// Next.js 16 renamed the `middleware.ts` file convention to `proxy.ts`
// (exported function `proxy` instead of `middleware`) — next-intl's own
// APIs are unaffected, we just export its handler under the new name.
export function proxy(request: Parameters<typeof intlMiddleware>[0]) {
  const response = intlMiddleware(request);

  // next-intl's "no locale prefix -> defaultLocale" redirect is permanent
  // (the site never actually serves unprefixed URLs), but NextResponse
  // .redirect() always issues a 307. Google's coverage report treats a
  // temporary status as "don't consolidate ranking signals here", so every
  // bare internal/external link (old bookmarks, backlinks, pre-i18n
  // sitemap entries) would keep bleeding SEO value. Rewrite it to 308 — the
  // GET-safe equivalent of a permanent 301 — while keeping every other
  // header (Location, Link alternate-links, Set-Cookie) intact.
  if (response.status === 307) {
    const location = response.headers.get("location");
    if (location) {
      const permanent = NextResponse.redirect(location, 308);
      response.headers.forEach((value, key) => {
        if (key.toLowerCase() !== "location") permanent.headers.set(key, value);
      });
      return permanent;
    }
  }

  return response;
}

export const config = {
  matcher: ["/((?!api|_next|.*\\..*).*)"],
};
