import { getTranslations } from "next-intl/server";

import type { AppLocale } from "@/i18n/routing";
import { localize } from "@/lib/localize";
import { formatAmount } from "@/lib/rates";
import type { GoodsTransportPricing, ServicePricingOption } from "@/lib/types";

import { PickVehicleOptionButton } from "./pick-vehicle-option-button";

export async function PricingOptions({
  options,
  locale,
  pricing,
}: {
  options: ServicePricingOption[];
  locale: AppLocale;
  pricing: GoodsTransportPricing | null;
}) {
  const t = await getTranslations("Transport");
  if (options.length === 0) return null;

  return (
    <section aria-labelledby="pricing-heading" className="mt-10">
      <h2 id="pricing-heading" className="font-heading text-[24px] font-semibold">
        {t("pricingHeading")}
      </h2>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {options.map((option) => {
          const note = localize(option, "price_note", locale);
          // Rates come from the Admin price list ("Cennik transportu rzeczy"),
          // never from the option's own text.
          const rate =
            pricing && option.code === "bus"
              ? t("busRate", {
                  hour: formatAmount(pricing.hourly_rate, locale),
                  km: formatAmount(pricing.price_per_100km, locale),
                })
              : pricing && option.code === "trailer"
                ? t("trailerRate", { amount: formatAmount(pricing.trailer_price_per_day, locale) })
                : "";
          return (
            <article key={option.code} className="flex flex-col rounded-xl border border-line bg-panel p-6">
              <h3 className="font-heading text-[20px] font-semibold">{localize(option, "name", locale)}</h3>
              <p className="mt-2 text-[17px] font-bold text-green">
                {option.on_request ? t("onRequest") : rate || note || t("priceAfterPhoto")}
              </p>
              {option.on_request && rate && <p className="text-[13px] text-muted">{rate}</p>}
              {!option.on_request && rate && note && <p className="text-[13px] text-muted">{note}</p>}
              <p className="mt-3 flex-1 text-[14.5px] leading-relaxed text-muted">
                {localize(option, "description", locale)}
              </p>
              <div>
                <PickVehicleOptionButton option={option.code} label={t("chooseOption")} />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
