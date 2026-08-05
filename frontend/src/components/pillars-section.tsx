import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";

export async function PillarsSection() {
  const t = await getTranslations("Pillars");

  return (
    <section className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[600px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
        </div>
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <Link
            href="/imprezy"
            className="group rounded-xl border border-line bg-panel p-8 transition-colors hover:border-amber"
          >
            <span className="text-[34px]">🎉</span>
            <h3 className="font-heading mt-4 text-[22px] font-semibold">{t("eventsTitle")}</h3>
            <p className="mt-2.5 text-[14.5px] leading-relaxed text-muted">{t("eventsBody")}</p>
            <span className="mt-5 inline-block text-[14px] font-semibold text-amber group-hover:underline">
              {t("eventsCta")} →
            </span>
          </Link>
          <a
            href="#routes"
            className="group rounded-xl border border-line bg-panel p-8 transition-colors hover:border-amber"
          >
            <span className="text-[34px]">🚐</span>
            <h3 className="font-heading mt-4 text-[22px] font-semibold">{t("localTitle")}</h3>
            <p className="mt-2.5 text-[14.5px] leading-relaxed text-muted">{t("localBody")}</p>
            <span className="mt-5 inline-block text-[14px] font-semibold text-amber group-hover:underline">
              {t("localCta")} →
            </span>
          </a>
        </div>
      </div>
    </section>
  );
}
