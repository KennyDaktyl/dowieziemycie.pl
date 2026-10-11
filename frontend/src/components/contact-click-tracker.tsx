"use client";

import { useEffect } from "react";

import { trackEvent } from "@/lib/analytics";

const WHATSAPP_HREF = /^https?:\/\/(wa\.me|api\.whatsapp\.com)\//i;

/** Where on the page a contact link sits: the nearest `data-track-location`
 * wins (hero, form, floating_button…), otherwise the site header/footer,
 * otherwise "content" (article bodies, FAQ answers…). */
function linkLocation(link: Element): string {
  const tagged = link.closest("[data-track-location]");
  if (tagged) return tagged.getAttribute("data-track-location") || "content";
  if (link.closest("header")) return "header";
  if (link.closest("footer")) return "footer";
  return "content";
}

/** One delegated click listener for every tel: and WhatsApp link on the
 * site — including ones inside CMS markdown — so no link needs its own
 * onClick. Sends phone_click / whatsapp_click (Google Ads conversions).
 * Costs nothing until a click: no DOM scan, no extra script. */
export function ContactClickTracker() {
  useEffect(() => {
    function onClick(event: MouseEvent) {
      const link = (event.target as Element | null)?.closest?.("a[href]");
      if (!link) return;
      const href = link.getAttribute("href") ?? "";
      const name = href.startsWith("tel:") ? "phone_click" : WHATSAPP_HREF.test(href) ? "whatsapp_click" : null;
      if (!name) return;
      trackEvent(name, {
        link_url: href,
        link_location: linkLocation(link),
        page_path: window.location.pathname,
      });
    }

    document.addEventListener("click", onClick, { capture: true, passive: true });
    return () => document.removeEventListener("click", onClick, { capture: true });
  }, []);

  return null;
}
