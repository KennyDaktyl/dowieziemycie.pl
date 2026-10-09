export const GA_MEASUREMENT_ID = "G-LFDNRNE2M0";

export const CONSENT_STORAGE_KEY = "dowieziemycie:cookie-consent";
export const CONSENT_REOPEN_EVENT = "dowieziemycie:cookie-consent-reopen";

export type ConsentDecision = "granted" | "denied";

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

/** Pushes a Consent Mode v2 update — `gtag` itself is defined by the inline
 * "default denied" script in the root layout (AnalyticsScripts), so it's
 * there before any client component runs. A no-op if that script was
 * blocked (ad blocker). One Accept/Reject choice covers analytics and
 * advertising storage together, same as transfer247.pl. */
export function updateAnalyticsConsent(decision: ConsentDecision): void {
  window.gtag?.("consent", "update", {
    analytics_storage: decision,
    ad_storage: decision,
    ad_user_data: decision,
    ad_personalization: decision,
  });
}

/** GA4 custom event (generate_lead, click_call, click_whatsapp). gtag.js
 * applies Consent Mode itself — before consent it sends cookieless pings
 * only. Never pass personal data (name, phone, address) as a parameter. */
export function trackEvent(name: string, params?: Record<string, string | number | boolean>): void {
  window.gtag?.("event", name, params);
}

export function getStoredConsent(): ConsentDecision | null {
  try {
    const value = localStorage.getItem(CONSENT_STORAGE_KEY);
    return value === "granted" || value === "denied" ? value : null;
  } catch {
    return null; // storage unavailable — the banner just asks again
  }
}

export function storeConsent(decision: ConsentDecision): void {
  try {
    localStorage.setItem(CONSENT_STORAGE_KEY, decision);
  } catch {
    // consent still applies to this page load via updateAnalyticsConsent
  }
}

/** Footer's "Cookie settings" button reopens the banner without a reload. */
export function reopenConsentBanner(): void {
  window.dispatchEvent(new Event(CONSENT_REOPEN_EVENT));
}
