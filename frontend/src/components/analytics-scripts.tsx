import Script from "next/script";

import { GA_MEASUREMENT_ID } from "@/lib/analytics";

/** Google Consent Mode v2 + GA4, in the order Google requires — and without
 * slowing the page down:
 *
 * 1. Consent default (denied) — a few bytes inline, `beforeInteractive`, so
 *    it runs before any Google tag. Must live in the root layout.
 * 2. gtag.js (~170 KB) and the config call — `lazyOnload`: fetched only
 *    after the page's load event, so it never competes with first paint or
 *    LCP. Consent Mode, not the script tag, decides what may be sent; the
 *    banner (CookieConsentBanner) updates it. */
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
      <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`} strategy="lazyOnload" />
      <Script id="ga4-init" strategy="lazyOnload">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_MEASUREMENT_ID}', {
            'anonymize_ip': true
          });
        `}
      </Script>
    </>
  );
}
