import Script from "next/script";

import { GaDeferredLoader } from "@/components/ga-deferred-loader";

/** Google Consent Mode v2 + GA4, in the order Google requires — and without
 * slowing the page down:
 *
 * 1. Consent default (denied) — a few bytes inline, `beforeInteractive`, so
 *    it runs before any Google tag and defines gtag() (calls queue in
 *    dataLayer). Must live in the root layout.
 * 2. gtag.js + config — GaDeferredLoader, on the first interaction or after
 *    10 s, so the library never runs inside the window web.dev measures.
 *    Consent Mode, not the script tag, decides what may be sent; the banner
 *    (CookieConsentBanner) updates it. */
export function AnalyticsScripts() {
  return (
    <>
      <Script id="consent-default" strategy="beforeInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('consent', 'default', {
            'ad_storage': 'denied',
            'ad_user_data': 'denied',
            'ad_personalization': 'denied',
            'analytics_storage': 'denied',
            'wait_for_update': 500
          });
        `}
      </Script>
      <GaDeferredLoader />
    </>
  );
}
