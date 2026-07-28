import { getLocale } from "next-intl/server";

import { apiFetch } from "@/lib/api";
import type { HomeContent } from "@/lib/types";

import { BookingCard } from "./booking-card";

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
  const locale = await getLocale();
  const homeContent = await apiFetch<HomeContent>("/api/home-content/", { next: { revalidate: 60 } });

  const eyebrow = locale === "en" ? homeContent.eyebrow_en : homeContent.eyebrow_pl;
  const headline = locale === "en" ? homeContent.headline_en : homeContent.headline_pl;
  const highlight = locale === "en" ? homeContent.headline_highlight_en : homeContent.headline_highlight_pl;
  const lead = locale === "en" ? homeContent.lead_en : homeContent.lead_pl;

  return (
    <section className="px-6 pt-16 pb-10">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[720px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {eyebrow}
          </span>
          <h1 className="font-heading my-[18px] text-[38px] leading-[1.03] font-semibold tracking-tight md:text-[52px] lg:text-[58px]">
            {renderHeadline(headline, highlight)}
          </h1>
          <p className="max-w-[560px] text-[16.5px] leading-relaxed text-muted">{lead}</p>
        </div>
        <BookingCard />
      </div>
    </section>
  );
}
