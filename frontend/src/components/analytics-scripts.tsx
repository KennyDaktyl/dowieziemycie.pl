import Script from "next/script";

import { GA_MEASUREMENT_ID, GOOGLE_ADS_ID } from "@/lib/analytics";

/** Google Consent Mode v2 (advanced) + one Google tag for Google Ads and GA4:
 *
 * 1. Consent default (denied) — a few bytes inline, `beforeInteractive`, so
 *    it runs before any Google tag and defines gtag() (calls queue in
 *    dataLayer). Must live in the root layout.
 * 2. gtag.js (loaded with the Ads ID) + config for Ads and GA4 —
 *    `afterInteractive`, on every page, whatever the consent state: Google
 *    Ads' tag check must find it without anyone accepting cookies. Consent
 *    Mode, not the script tag, decides what may be sent (cookieless pings
 *    until then); the banner (CookieConsentBanner) only updates consent. */
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
      <Script
        id="gtag-js"
        src={`https://www.googletagmanager.com/gtag/js?id=${GOOGLE_ADS_ID}`}
        strategy="afterInteractive"
      />
      <Script id="gtag-config" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GOOGLE_ADS_ID}');
          gtag('config', '${GA_MEASUREMENT_ID}', { 'anonymize_ip': true });
        `}
      </Script>
    </>
  );
}
