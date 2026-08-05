import { getLocale, getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { apiFetch } from "@/lib/api";
import type { HomeContent } from "@/lib/types";

function renderHeadline(headline: string, highlight: string) {
  // "Bezpieczny przejazd. Każdej {highlight}" -> "Bezpieczny przejazd." <br/> "Każdej " + <amber>highlight</amber>
  const [firstLine, ...restParts] = headline.split(". ");
  const rest = restParts.join(". ").replace("{highlight}", "").trim();
  return (
    <>
      {firstLine}.
      <br />
      {rest} <span className="text-amber">{highlight}</span>
    </>
  );
}

export async function HeroSection() {
  const [locale, t, homeContent] = await Promise.all([
    getLocale(),
    getTranslations("Hero"),
    apiFetch<HomeContent>("/api/home-content/", { next: { revalidate: 60 } }),
  ]);

  const eyebrow = locale === "en" ? homeContent.eyebrow_en : homeContent.eyebrow_pl;
  const headline = locale === "en" ? homeContent.headline_en : homeContent.headline_pl;
  const highlight = locale === "en" ? homeContent.headline_highlight_en : homeContent.headline_highlight_pl;
  const lead = locale === "en" ? homeContent.lead_en : homeContent.lead_pl;

  return (
    <section className="px-6 pt-16 pb-10">
      <div className="mx-auto max-w-[1360px]">
        <div className="max-w-[720px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {eyebrow}
          </span>
          <h1 className="font-heading my-[18px] text-[38px] leading-[1.03] font-semibold tracking-tight md:text-[52px] lg:text-[58px]">
            {renderHeadline(headline, highlight)}
          </h1>
          <p className="max-w-[560px] text-[16.5px] leading-relaxed text-muted">{lead}</p>
        </div>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/rezerwacja"
            className="rounded-md bg-amber px-6 py-3.5 text-[15px] font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
          >
            {t("ctaBook")}
          </Link>
          <Link
            href="/imprezy"
            className="rounded-md border border-line px-6 py-3.5 text-[15px] font-semibold whitespace-nowrap text-text transition-colors hover:border-amber hover:text-amber"
          >
            {t("ctaEvents")}
          </Link>
        </div>
        <p className="mt-5 text-[13px] text-muted">{t("trustBar")}</p>
      </div>
    </section>
  );
}
