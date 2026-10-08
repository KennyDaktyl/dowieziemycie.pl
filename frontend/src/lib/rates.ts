import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import type { GoodsTransportPricing } from "@/lib/types";

/** The goods-transport price list lives only in Django Admin ("Cennik
 * transportu rzeczy"). Page and blog texts never contain amounts — they use
 * {rate:hour} {rate:night} {rate:100km} {rate:trailer} {rate:loading},
 * filled here, so changing a rate in Admin updates every page at once. */
export async function getGoodsPricing(): Promise<GoodsTransportPricing | null> {
  return apiFetch<GoodsTransportPricing>("/api/goods-transport-pricing/").catch(() => null);
}

export function formatAmount(value: string | number, locale: AppLocale): string {
  const amount = Number(value).toLocaleString(locale === "pl" ? "pl-PL" : "en-GB", { maximumFractionDigits: 2 });
  return locale === "pl" ? `${amount} zł` : `${amount} PLN`;
}

const RATE_TOKEN_RE = /\{rate:(hour|night|100km|trailer|loading)\}/g;

export function fillRateTokens(text: string, pricing: GoodsTransportPricing | null, locale: AppLocale): string {
  if (!text || !text.includes("{rate:")) return text;
  const individual = locale === "pl" ? "wycena indywidualna" : "individual quote";
  return text.replace(RATE_TOKEN_RE, (_, key: string) => {
    if (!pricing) return individual;
    const value = {
      hour: pricing.hourly_rate,
      night: pricing.night_hourly_rate,
      "100km": pricing.price_per_100km,
      trailer: pricing.trailer_price_per_day,
      loading: pricing.loading_price_from,
    }[key];
    return value ? formatAmount(value, locale) : individual;
  });
}
