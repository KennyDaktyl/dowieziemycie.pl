import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";

import { Breadcrumbs } from "@/components/breadcrumbs";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { VehicleGallery } from "@/components/vehicle-gallery";
import type { AppLocale } from "@/i18n/routing";
import { Link } from "@/i18n/navigation";
import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import { buildAlternates } from "@/lib/seo";
import type { Vehicle } from "@/lib/types";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Fleet" });
  return {
    title: t("title"),
    description: t("pageLead"),
    alternates: buildAlternates("/flota", locale as AppLocale),
  };
}

export default async function FleetPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, appLocale, vehicles] = await Promise.all([
    getTranslations("Fleet"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    apiFetch<Vehicle[]>("/api/fleet/vehicles/", { next: { revalidate: 60 } }).catch(() => []),
  ]);

  const descriptionKey = appLocale === "en" ? "description_en" : "description_pl";
  const sortedVehicles = [...vehicles].sort((a, b) => b.seats - a.seats);

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[1360px] px-6 py-16">
        <Breadcrumbs items={[{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("fleet") }]} />
        <div className="mt-3 mb-10 max-w-[720px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h1 className="font-heading mt-2.5 text-[34px] font-semibold md:text-[44px]">{t("title")}</h1>
          <p className="mt-3.5 text-[16px] leading-relaxed text-muted">{t("pageLead")}</p>
        </div>

        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_360px]">
          <div className="flex flex-col gap-5">
            {sortedVehicles.length === 0 ? <p className="text-muted">{t("empty")}</p> : null}
            {sortedVehicles.map((vehicle) => {
              const cover = vehicle.cover_photo || vehicle.photos[0]?.image;
              const galleryImages = [
                ...(vehicle.cover_photo ? [{ image: vehicle.cover_photo, caption: vehicle.name }] : []),
                ...vehicle.photos.map((photo) => ({
                  image: photo.image,
                  thumbnail: photo.thumbnail,
                  caption: photo.caption,
                })),
              ];
              const description = vehicle[descriptionKey] || vehicle.description_pl;

              return (
                <article key={vehicle.id} className="rounded-[14px] border border-line bg-panel p-5 md:p-6">
                  <div className="grid grid-cols-1 gap-6 md:grid-cols-[320px_1fr]">
                    <div className="overflow-hidden rounded-[12px] border border-line bg-panel-2">
                      {cover ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={absoluteImageUrl(cover)} alt={vehicle.name} className="h-[220px] w-full object-cover" />
                      ) : (
                        <div className="flex h-[220px] items-center justify-center text-muted">{vehicle.name}</div>
                      )}
                    </div>
                    <div>
                      <h2 className="font-heading text-[24px] font-semibold">{vehicle.name}</h2>
                      {vehicle.model && <p className="mt-1 text-[14px] text-muted">{vehicle.model}</p>}
                      <p className="mt-4 font-heading text-[22px] font-semibold text-amber">
                        {t("customerSeats", { count: vehicle.seats })}
                      </p>
                      {description && <p className="mt-3 max-w-[680px] text-[15px] leading-relaxed text-muted">{description}</p>}
                    </div>
                  </div>
                  {galleryImages.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-label mb-3 text-xs font-semibold tracking-[0.1em] text-muted uppercase">
                        {t("gallery")}
                      </h3>
                      <VehicleGallery images={galleryImages} name={vehicle.name} />
                    </div>
                  )}
                </article>
              );
            })}
          </div>

          <aside className="h-fit rounded-[14px] border border-amber/35 bg-amber/10 p-6">
            <h2 className="font-heading text-[22px] font-semibold">{t("plannedTitle")}</h2>
            <p className="mt-3 text-[14.5px] leading-relaxed text-muted">{t("plannedBody")}</p>
            <Link
              href="/rezerwacja"
              className="mt-5 inline-flex rounded-md bg-amber px-5 py-3 text-[14px] font-semibold text-[#1a1305] transition-all hover:-translate-y-px"
            >
              {t("bookRide")}
            </Link>
          </aside>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
