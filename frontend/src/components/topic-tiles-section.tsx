import { getLocale, getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { localize } from "@/lib/localize";
import type { EventOfferListItem } from "@/lib/types";

async function getFeaturedEvents(): Promise<EventOfferListItem[]> {
  // ?homepage=1 — only events flagged show_on_homepage in admin. Adding a
  // new event there (with an article, gallery, example price) makes it
  // appear here automatically, no code change needed.
  return apiFetch<EventOfferListItem[]>("/api/events/?homepage=1", { next: { revalidate: 60 } }).catch(() => []);
}

export async function TopicTilesSection() {
  const [t, appLocale, events] = await Promise.all([
    getTranslations("TopicTiles"),
    getLocale() as Promise<AppLocale>,
    getFeaturedEvents(),
  ]);

  // Two evergreen tiles not tied to a specific EventOffer — night-transport
  // messaging (points back at the homepage's own routes section) and the
  // business/long-route offer page.
  const staticTiles = [
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
          {events.map((event) => (
            <Link
              key={event.slug}
              href={`/imprezy/${event.slug}`}
              className="rounded-lg border border-line bg-panel p-5 transition-colors hover:border-amber"
            >
              {event.icon && <span className="text-[22px]">{event.icon}</span>}
              <h3 className="mt-2.5 text-[15.5px] font-semibold">{localize(event, "title", appLocale)}</h3>
              <p className="mt-1.5 text-[13px] leading-relaxed text-muted">
                {localize(event, "excerpt", appLocale)}
              </p>
              {event.price_from != null && (
                <p className="mt-2 text-[13px] font-bold text-green">
                  {t("priceFrom", { price: Number(event.price_from).toFixed(0) })}
                </p>
              )}
            </Link>
          ))}
          {staticTiles.map((tile) => (
            <a
              key={tile.title}
              href={tile.href}
              className="rounded-lg border border-line bg-panel p-5 transition-colors hover:border-amber"
            >
              <span className="text-[22px]">{tile.icon}</span>
              <h3 className="mt-2.5 text-[15.5px] font-semibold">{tile.title}</h3>
              <p className="mt-1.5 text-[13px] leading-relaxed text-muted">{tile.body}</p>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
