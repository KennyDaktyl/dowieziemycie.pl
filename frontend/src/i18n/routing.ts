import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["pl", "en"],
  defaultLocale: "pl",
  // A bare, unprefixed URL (old links, external backlinks, content authored
  // before the /pl/en split) always means "the default site" here, not
  // "guess from the visitor's browser" — with detection on, the same URL
  // could 307 different visitors (and Googlebot) to different locales,
  // which is incompatible with treating that redirect as permanent.
  localeDetection: false,
  // next-intl's middleware also emits its own hreflang set as an HTTP `Link`
  // header on every response, with x-default pointing at the UNPREFIXED path
  // (e.g. /blog) — which 308-redirects. Googlebot reads that header, so every
  // page handed it one redirecting URL: GSC's "page with redirect" count grew
  // with every page added. Correct hreflang/canonical are already emitted in
  // the HTML via buildAlternates() (lib/seo.ts), so the header adds nothing.
  alternateLinks: false,
});

export type AppLocale = (typeof routing.locales)[number];
