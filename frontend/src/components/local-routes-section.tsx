import { getLocale, getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { apiFetch } from "@/lib/api";
import type { LocalRoute } from "@/lib/types";

export async function LocalRoutesSection() {
  const [t, locale, routes] = await Promise.all([
    getTranslations("Routes"),
    getLocale(),
    // ?homepage=1 — only routes flagged show_on_homepage in admin, so the
    // homepage shows a curated set rather than every published route.
    apiFetch<LocalRoute[]>("/api/routes/?homepage=1", { next: { revalidate: 60 } }),
  ]);

  return (
    <section id="routes" className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[640px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
          <p className="mt-3 text-[15.5px] leading-relaxed text-muted">{t("description")}</p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {routes.map((route) => (
            <Link
              key={route.slug}
              href={`/trasa/${route.slug}`}
              className="rounded-[14px] border border-line bg-panel p-5 transition-colors hover:border-amber"
            >
              <h3 className="font-heading mb-1.5 text-[17px] font-semibold">
                Kraków ↔ {route.destination_town}
              </h3>
              <p className="mb-4 text-[13.5px] leading-relaxed text-muted">
                {locale === "en" ? route.lead_en : route.lead_pl}
              </p>
              {route.example_price != null ? (
                <div className="font-heading text-[16px] font-bold text-green">
                  {t("priceFrom", { price: route.example_price.toFixed(0) })}
                </div>
              ) : (
                <div className="font-heading text-[16px] font-bold text-muted">{t("customQuote")}</div>
              )}
              <span className="mt-3.5 inline-block text-[13px] font-semibold text-amber">{t("cta")}</span>
            </Link>
          ))}
        </div>
        <Link href="/kierunki" className="mt-8 inline-block text-[13.5px] font-semibold text-amber hover:underline">
          {t("seeAll")} →
        </Link>
      </div>
    </section>
  );
}
