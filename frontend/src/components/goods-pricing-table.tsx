import { getTranslations } from "next-intl/server";

import type { AppLocale } from "@/i18n/routing";
import { formatAmount } from "@/lib/rates";
import type { GoodsTransportPricing } from "@/lib/types";

/** The goods-transport price list, straight from Admin. */
export async function GoodsPricingTable({ pricing, locale }: { pricing: GoodsTransportPricing; locale: AppLocale }) {
  const t = await getTranslations("Transport");
  const hhmm = (time: string) => time.slice(0, 5);
  const rows = [
    [
      t("rateHour", { from: hhmm(pricing.day_starts_at), to: hhmm(pricing.night_starts_at) }),
      formatAmount(pricing.hourly_rate, locale),
    ],
    [
      t("rateNight", { from: hhmm(pricing.night_starts_at), to: hhmm(pricing.day_starts_at) }),
      formatAmount(pricing.night_hourly_rate, locale),
    ],
    [t("rate100km"), formatAmount(pricing.price_per_100km, locale)],
    [t("rateTrailer"), t("fromAmount", { amount: formatAmount(pricing.trailer_price_per_day, locale) })],
    [
      t("rateLoading"),
      pricing.loading_price_from
        ? t("fromAmount", { amount: formatAmount(pricing.loading_price_from, locale) })
        : t("individualQuote"),
    ],
  ];

  return (
    <section aria-labelledby="rates-heading" className="mt-8 max-w-[900px]">
      <h2 id="rates-heading" className="font-heading text-[22px] font-semibold">
        {t("ratesHeading")}
      </h2>
      <table className="mt-4 w-full overflow-hidden rounded-xl border border-line text-[14.5px]">
        <tbody className="divide-y divide-line">
          {rows.map(([label, value]) => (
            <tr key={label} className="bg-panel">
              <th scope="row" className="px-4 py-3 text-left font-normal text-muted">
                {label}
              </th>
              <td className="px-4 py-3 text-right font-semibold whitespace-nowrap">{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-[12.5px] text-muted">{t("ratesNote")}</p>
    </section>
  );
}
