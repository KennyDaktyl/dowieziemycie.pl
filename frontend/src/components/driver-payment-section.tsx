import { getLocale, getTranslations } from "next-intl/server";

import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import type { AppLocale } from "@/i18n/routing";
import type { ShowcasePhoto } from "@/lib/types";

const PAYMENT_BRANDS = ["VISA", "Mastercard", "BLIK"];

/** "Twój kierowca" + "Płatność" — the two things a first-time caller wants
 * confirmed: it's one known driver (not a dispatcher pool), and a card
 * terminal is in the car. Driver photo comes from the SiteShowcasePhoto
 * model (Django admin → Zdjęcia na stronę główną, category "Kierowca"),
 * site-scoped to dowieziemycie. */
export async function DriverPaymentSection() {
  const [t, locale, photos] = await Promise.all([
    getTranslations("DriverPayment"),
    getLocale() as Promise<AppLocale>,
    apiFetch<ShowcasePhoto[]>("/api/showcase-photos/", { next: { revalidate: 60 } }).catch(
      () => [] as ShowcasePhoto[],
    ),
  ]);

  const driver = photos.find((p) => p.category === "DRIVER");

  return (
    <section className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto grid max-w-[1360px] grid-cols-1 gap-5 md:grid-cols-2">
        <div className="flex items-center gap-5 rounded-[14px] border border-line bg-panel p-6">
          {driver ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={absoluteImageUrl(driver.thumbnail || driver.image)}
              alt={localize(driver, "caption", locale) || t("driverAlt")}
              className="h-[72px] w-[72px] shrink-0 rounded-full border-2 border-amber/60 object-cover"
            />
          ) : (
            <span className="flex h-[72px] w-[72px] shrink-0 items-center justify-center rounded-full border-2 border-amber/60 bg-panel-2">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" className="text-muted">
                <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="1.6" />
                <path d="M4.5 20c1.6-4 5-6 7.5-6s5.9 2 7.5 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
            </span>
          )}
          <div>
            <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
              {t("driverEyebrow")}
            </span>
            <h3 className="font-heading mt-1 text-[20px] font-semibold">{t("driverHeading")}</h3>
            <p className="mt-1.5 text-[14px] leading-relaxed text-muted">{t("driverBody")}</p>
          </div>
        </div>

        <div className="flex items-start gap-5 rounded-[14px] border border-line bg-panel p-6">
          <span className="flex h-[60px] w-[60px] shrink-0 items-center justify-center rounded-[14px] bg-amber/10 text-amber">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <rect x="2.5" y="5" width="19" height="14" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
              <path d="M2.5 9.5h19" stroke="currentColor" strokeWidth="1.7" />
              <path d="M6 14.5h5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
              <circle cx="16.5" cy="14.5" r="1.4" fill="currentColor" />
            </svg>
          </span>
          <div>
            <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
              {t("paymentEyebrow")}
            </span>
            <h3 className="font-heading mt-1 text-[20px] font-semibold">{t("paymentHeading")}</h3>
            <p className="mt-1.5 text-[14px] leading-relaxed text-muted">{t("paymentBody")}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {[...PAYMENT_BRANDS, t("paymentContactless"), t("paymentCash")].map((method) => (
                <span
                  key={method}
                  className="rounded-[7px] border border-line bg-panel-2 px-2 py-1 text-[11.5px] font-medium text-text"
                >
                  {method}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
