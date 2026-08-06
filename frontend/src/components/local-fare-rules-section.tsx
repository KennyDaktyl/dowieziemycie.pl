import { getTranslations } from "next-intl/server";

import { apiFetch } from "@/lib/api";
import type { LocalFarePolicy } from "@/lib/types";

// Reads the live LocalFarePolicy from the backend so this copy always
// matches whatever's actually configured in admin (minimum fare, per-km
// rate, radius) instead of drifting out of sync with a hardcoded number.
export async function LocalFareRulesSection() {
  const [t, policy] = await Promise.all([
    getTranslations("LocalFareRules"),
    apiFetch<LocalFarePolicy | null>("/api/local-fare-policy/", { next: { revalidate: 60 } }).catch(() => null),
  ]);

  if (!policy) return null;

  return (
    <section className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="max-w-[720px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
          <p className="mt-3 text-[15.5px] leading-relaxed text-muted">
            {t("body", {
              radius: Number(policy.proximity_threshold_km).toFixed(0),
              maxKm: policy.local_max_distance_km,
              minFare: Number(policy.minimum_fare).toFixed(0),
              includedKm: policy.included_km,
              perKm: Number(policy.price_per_km).toFixed(0),
            })}
          </p>
        </div>
      </div>
    </section>
  );
}
