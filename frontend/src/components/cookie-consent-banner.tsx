"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { Link } from "@/i18n/navigation";
import { CONSENT_REOPEN_EVENT, getStoredConsent, storeConsent, updateAnalyticsConsent } from "@/lib/analytics";

/** Accept / Reject for analytics + advertising cookies (Consent Mode v2).
 * Rendered only after hydration — never part of the server HTML, so it
 * can't become the LCP element or shift the layout. */
export function CookieConsentBanner() {
  const t = useTranslations("CookieConsent");
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const stored = getStoredConsent();
    // Consent defaults to denied on every page load, so a returning
    // visitor's earlier "yes" has to be re-applied each time.
    if (stored === "granted") updateAnalyticsConsent("granted");

    const reopen = () => setVisible(true);
    window.addEventListener(CONSENT_REOPEN_EVENT, reopen);
    // Deferred to a task so the banner never renders during hydration.
    const timer = stored === null ? window.setTimeout(reopen, 0) : undefined;
    return () => {
      window.removeEventListener(CONSENT_REOPEN_EVENT, reopen);
      window.clearTimeout(timer);
    };
  }, []);

  function decide(decision: "granted" | "denied") {
    storeConsent(decision);
    updateAnalyticsConsent(decision);
    setVisible(false);
  }

  if (!visible) return null;

  return (
    <div className="fixed inset-x-0 bottom-0 z-[60] p-4 sm:p-6" role="dialog" aria-live="polite" aria-label={t("title")}>
      <div className="mx-auto flex max-w-[860px] flex-col gap-4 rounded-xl border border-line bg-panel p-5 shadow-[0_10px_40px_-10px_rgba(0,0,0,0.6)] sm:flex-row sm:items-center sm:p-6">
        <p className="text-[13.5px] leading-relaxed text-muted">
          {t("text")}{" "}
          <Link href="/regulamin" className="text-amber underline underline-offset-2">
            {t("privacyLinkText")}
          </Link>
        </p>
        <div className="flex shrink-0 gap-3">
          <button
            type="button"
            onClick={() => decide("denied")}
            className="flex-1 rounded-md border border-line px-5 py-2.5 text-[14px] font-semibold whitespace-nowrap text-text transition-colors hover:border-amber sm:flex-none"
          >
            {t("reject")}
          </button>
          <button
            type="button"
            onClick={() => decide("granted")}
            className="flex-1 rounded-md bg-amber px-5 py-2.5 text-[14px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px sm:flex-none"
          >
            {t("acceptAll")}
          </button>
        </div>
      </div>
    </div>
  );
}
