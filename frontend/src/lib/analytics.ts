"use client";

/** GA4 event, if GA4/GTM is on the page — a no-op otherwise (dowieziemycie.pl
 * doesn't load GA yet; the events start counting as soon as it does).
 * Never pass personal data (name, phone, address) as a parameter. */
export function trackEvent(name: string, params: Record<string, string | number | boolean> = {}): void {
  if (typeof window === "undefined") return;
  const w = window as unknown as { gtag?: (...args: unknown[]) => void; dataLayer?: unknown[] };
  if (typeof w.gtag === "function") {
    w.gtag("event", name, params);
  } else if (Array.isArray(w.dataLayer)) {
    w.dataLayer.push({ event: name, ...params });
  }
}
