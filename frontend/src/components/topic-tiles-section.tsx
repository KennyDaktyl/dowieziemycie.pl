import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";

export async function TopicTilesSection() {
  const t = await getTranslations("TopicTiles");

  const tiles = [
    { icon: "🎤", title: t("concertsTitle"), body: t("concertsBody"), href: "/imprezy" },
    { icon: "🤵", title: t("stagTitle"), body: t("stagBody"), href: "/imprezy" },
    { icon: "👰", title: t("henTitle"), body: t("henBody"), href: "/imprezy" },
    { icon: "🌙", title: t("nightTitle"), body: t("nightBody"), href: "#routes" },
    { icon: "🏢", title: t("businessTitle"), body: t("businessBody"), href: "/wynajem-busa-z-kierowca" },
  ];

  return (
    <section className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[600px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
        </div>
        <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
          {tiles.map((tile) =>
            tile.href.includes("#") ? (
              <a
                key={tile.title}
                href={tile.href}
                className="rounded-lg border border-line bg-panel p-5 transition-colors hover:border-amber"
              >
                <span className="text-[22px]">{tile.icon}</span>
                <h3 className="mt-2.5 text-[15.5px] font-semibold">{tile.title}</h3>
                <p className="mt-1.5 text-[13px] leading-relaxed text-muted">{tile.body}</p>
              </a>
            ) : (
              <Link
                key={tile.title}
                href={tile.href}
                className="rounded-lg border border-line bg-panel p-5 transition-colors hover:border-amber"
              >
                <span className="text-[22px]">{tile.icon}</span>
                <h3 className="mt-2.5 text-[15.5px] font-semibold">{tile.title}</h3>
                <p className="mt-1.5 text-[13px] leading-relaxed text-muted">{tile.body}</p>
              </Link>
            ),
          )}
        </div>
      </div>
    </section>
  );
}
