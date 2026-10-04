import { getTranslations } from "next-intl/server";

import { CustomQuoteCta } from "@/components/custom-quote-cta";
import { apiFetch } from "@/lib/api";
import type { ContactInfo, EventDriverPricing } from "@/lib/types";

/** "06:00:00" -> "06:00" — Django's TimeField serializes with seconds, the
 * copy only ever needs hours:minutes. */
function shortTime(value: string): string {
  return value.slice(0, 5);
}

/** Explains how hourly driver-with-car rental for weddings/events is billed
 * — shown on /imprezy and /cennik. Reads the live EventDriverPricing from
 * the backend so the numbers never drift out of sync with what's actually
 * quoted (same pattern as LocalFareRulesSection/PricingTierSection).
 * Renders nothing if the admin has turned the section off (is_active=false)
 * or the request fails — never shows a half-built pricing box. */
export async function EventDriverPricingSection() {
  const [t, pricing, contact] = await Promise.all([
    getTranslations("EventDriverPricing"),
    apiFetch<EventDriverPricing | null>("/api/event-driver-pricing/").catch(
      () => null,
    ),
    apiFetch<ContactInfo>("/api/contact-info/"),
  ]);

  if (!pricing) return null;

  return (
    <section className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="max-w-[720px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
          <p className="mt-3 text-[15.5px] leading-relaxed text-muted">{t("intro")}</p>
        </div>

        <div className="mt-8 grid grid-cols-1 gap-3.5 sm:grid-cols-3">
          <div className="rounded-md border border-line border-l-4 border-l-amber bg-panel px-[18px] py-4">
            <div className="text-[13px] text-muted">{t("dayLabel")}</div>
            <div className="font-heading mt-1 text-[26px] font-bold">
              {Number(pricing.day_hourly_rate).toFixed(0)}{" "}
              <span className="text-[15px] font-semibold text-muted">{t("perHour")}</span>
            </div>
            <div className="mt-1 text-[12.5px] text-muted">{t("dayNote", { time: shortTime(pricing.day_starts_at) })}</div>
          </div>
          <div className="rounded-md border border-line border-l-4 border-l-green bg-panel px-[18px] py-4">
            <div className="text-[13px] text-muted">{t("nightLabel")}</div>
            <div className="font-heading mt-1 text-[26px] font-bold">
              {Number(pricing.night_hourly_rate).toFixed(0)}{" "}
              <span className="text-[15px] font-semibold text-muted">{t("perHour")}</span>
            </div>
            <div className="mt-1 text-[12.5px] text-muted">
              {t("nightNote", { time: shortTime(pricing.night_starts_at) })}
            </div>
          </div>
          <div className="rounded-md border border-line bg-panel px-[18px] py-4">
            <div className="text-[13px] text-muted">{t("perKmLabel")}</div>
            <div className="font-heading mt-1 text-[26px] font-bold">
              {Number(pricing.price_per_100km).toFixed(0)} <span className="text-[15px] font-semibold text-muted">{t("perKmUnit")}</span>
            </div>
            <div className="mt-1 text-[12.5px] text-muted">{t("perKmNote")}</div>
          </div>
        </div>

        <p className="mt-5 max-w-[720px] text-[13px] leading-relaxed text-muted">{t("footnote")}</p>
        <p className="mt-1.5 text-[12px] text-muted">{t("vatNote")}</p>
        <CustomQuoteCta phone={contact.phone} phoneDisplay={contact.phone_display} email={contact.email} className="mt-3" />
      </div>
    </section>
  );
}
