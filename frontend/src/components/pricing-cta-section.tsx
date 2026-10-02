import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";

/** Homepage used to embed the full distance-tier price table directly (and
 * now /cennik also carries the event/wedding hourly-rate pricing) — showing
 * every price table on the homepage too would mean two sources of the same
 * numbers drifting out of sync over time. This is a single, lightweight
 * pointer to the one real price list instead. */
export async function PricingCtaSection() {
  const t = await getTranslations("PricingCta");

  return (
    <section className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="flex flex-col items-start gap-6 rounded-[14px] border border-line bg-panel p-8 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-5">
            <span className="flex h-[60px] w-[60px] shrink-0 items-center justify-center rounded-[14px] bg-amber/10 text-amber">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                <path
                  d="M11.5 3h5.5A2 2 0 0 1 19 5v5.5a2 2 0 0 1-.59 1.41l-7 7a2 2 0 0 1-2.82 0l-5.5-5.5a2 2 0 0 1 0-2.82l7-7A2 2 0 0 1 11.5 3Z"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinejoin="round"
                />
                <circle cx="14.5" cy="7.5" r="1.3" fill="currentColor" />
                <path d="M3 19c2-1 4 1 6 0s4-1 6 0" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
              </svg>
            </span>
            <div>
              <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
                {t("eyebrow")}
              </span>
              <h2 className="font-heading mt-1.5 text-[22px] font-semibold">{t("title")}</h2>
              <p className="mt-1.5 max-w-[480px] text-[14px] leading-relaxed text-muted">{t("body")}</p>
            </div>
          </div>
          <Link
            href="/cennik"
            className="shrink-0 rounded-md bg-amber px-5 py-3 text-[14.5px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
          >
            {t("cta")} →
          </Link>
        </div>
      </div>
    </section>
  );
}
