"use client";

import { useEffect } from "react";

import { GA_MEASUREMENT_ID } from "@/lib/analytics";

const INTERACTION_EVENTS = ["pointerdown", "keydown", "scroll", "touchstart"] as const;
// Short enough for Google's own tag check (it loads the page without
// scrolling) to find the tag, long enough to stay out of the Lighthouse trace.
const FALLBACK_DELAY_MS = 4_000;

/** Loads gtag.js on the visitor's first interaction (or after 4 s without
 * one) instead of right after the load event: its ~170 KB of script then
 * never runs inside the window web.dev / Lighthouse measures (it added
 * ~200 ms of Total Blocking Time and cost ~6 Performance points when it
 * loaded at onload). Events tracked earlier aren't lost — the inline
 * consent-default script already defined gtag(), which queues calls in
 * dataLayer until the library arrives. */
export function GaDeferredLoader() {
  useEffect(() => {
    let loaded = false;

    function load() {
      if (loaded) return;
      loaded = true;
      cleanup();
      const script = document.createElement("script");
      script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
      script.async = true;
      document.head.appendChild(script);
      window.gtag?.("js", new Date());
      window.gtag?.("config", GA_MEASUREMENT_ID, { anonymize_ip: true });
    }

    const timer = window.setTimeout(load, FALLBACK_DELAY_MS);
    function cleanup() {
      window.clearTimeout(timer);
      for (const event of INTERACTION_EVENTS) window.removeEventListener(event, load);
    }
    for (const event of INTERACTION_EVENTS) window.addEventListener(event, load, { once: true, passive: true });
    return cleanup;
  }, []);

  return null;
}
