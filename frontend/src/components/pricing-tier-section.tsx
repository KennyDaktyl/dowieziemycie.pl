import { getTranslations } from "next-intl/server";

import { CustomQuoteCta } from "@/components/custom-quote-cta";
import { apiFetch } from "@/lib/api";
import type { ContactInfo, PricingTier } from "@/lib/types";

export async function PricingTierSection() {
  const [t, tiers, contact] = await Promise.all([
    getTranslations("PricingTiers"),
    apiFetch<PricingTier[]>("/api/pricing-tiers/", { next: { revalidate: 60 } }),
    apiFetch<ContactInfo>("/api/contact-info/", { next: { revalidate: 60 } }),
  ]);

  const maxKm = tiers.length > 0 ? Math.max(...tiers.map((tier) => tier.max_distance_km)) : null;

  return (
    <section id="coverage" className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[600px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
          <p className="mt-3 text-[15.5px] leading-relaxed text-muted">{t("description")}</p>
        </div>
        <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
          {tiers.map((tier) => (
            <div key={tier.id} className="rounded-md border border-line border-l-4 border-l-green bg-panel px-[18px] py-4">
              <div className="font-heading text-[17px] font-bold">{t("upTo", { km: tier.max_distance_km })}</div>
              <div className="mt-2.5 flex items-center justify-between text-[13px]">
                <span className="text-muted">{t("reserved")}</span>
                <span className="font-heading font-bold text-green">{Number(tier.price_reserved).toFixed(0)} zł</span>
              </div>
              <div className="mt-1 flex items-center justify-between text-[13px]">
                <span className="text-muted">{t("onDemand")}</span>
                <span className="font-heading font-bold text-amber">{Number(tier.price_on_demand).toFixed(0)} zł</span>
              </div>
            </div>
          ))}
        </div>
        {maxKm !== null && (
          <div className="mt-5">
            <p className="text-[13px] text-muted">{t("beyond", { km: maxKm })}</p>
            <CustomQuoteCta
              phone={contact.phone}
              phoneDisplay={contact.phone_display}
              email={contact.email}
              className="mt-1.5"
            />
          </div>
        )}
        <p className="mt-1.5 text-[12px] text-muted">{t("vatNote")}</p>
      </div>
    </section>
  );
}
