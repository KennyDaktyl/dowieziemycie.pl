import { GOOGLE_ADS_ID, trackEvent } from "@/lib/analytics";

// Conversion label of the Google Ads "Kontakt" action (Google Ads → Goals →
// Conversions → Kontakt → event snippet → the part after the slash in send_to).
export const GOOGLE_ADS_CONTACT_LABEL = "rGyuCPrw8pkdENeGgfJE";

export type ContactKind = "phone" | "whatsapp";

/** A click on a tel: or WhatsApp link: the Google Ads "Kontakt" conversion
 * plus phone_click / whatsapp_click (GA4). A no-op when gtag is missing
 * (ad blocker, script not loaded) — never throws, never blocks the link. */
export function trackContact(kind: ContactKind, params?: Record<string, string | number | boolean>): void {
  trackEvent("conversion", {
    send_to: `${GOOGLE_ADS_ID}/${GOOGLE_ADS_CONTACT_LABEL}`,
    value: 1.0,
    currency: "PLN",
  });
  trackEvent(kind === "phone" ? "phone_click" : "whatsapp_click", params);
}
