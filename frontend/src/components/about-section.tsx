import { getLocale, getTranslations } from "next-intl/server";

import { apiFetch } from "@/lib/api";
import type { HomeContent } from "@/lib/types";

export async function AboutSection() {
  const [locale, t, content] = await Promise.all([
    getLocale(),
    getTranslations("About"),
    apiFetch<HomeContent>("/api/home-content/", { next: { revalidate: 60 } }),
  ]);

  const about = locale === "en" ? content.about_en : content.about_pl;
  if (!about) return null;

  return (
    <section className="border-line border-t px-6 py-16">
      <div className="mx-auto max-w-[1360px]">
        <h2 className="font-heading text-[24px] font-semibold">{t("heading")}</h2>
        <p className="mt-4 text-[15px] leading-relaxed text-muted">{about}</p>
        <a
          href="https://czernichow.pl/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-amber mt-4 inline-block text-[13.5px] font-medium hover:underline"
        >
          {t("gminaLink")} →
        </a>
      </div>
    </section>
  );
}
