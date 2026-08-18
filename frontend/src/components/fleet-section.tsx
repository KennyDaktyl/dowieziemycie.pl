import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import type { Vehicle } from "@/lib/types";

function VanIcon() {
  return (
    <svg width="180" height="90" viewBox="0 0 180 90" fill="none">
      <rect x="10" y="30" width="150" height="35" rx="8" stroke="#F5A623" strokeWidth="2.5" />
      <rect x="25" y="15" width="90" height="20" rx="6" stroke="#F5A623" strokeWidth="2.5" />
      <circle cx="45" cy="68" r="10" stroke="#EDEEF2" strokeWidth="2.5" />
      <circle cx="130" cy="68" r="10" stroke="#EDEEF2" strokeWidth="2.5" />
    </svg>
  );
}

export async function FleetSection() {
  const [t, vehicles] = await Promise.all([
    getTranslations("Fleet"),
    apiFetch<Vehicle[]>("/api/fleet/vehicles/", { next: { revalidate: 60 } }),
  ]);

  const totalSeats = vehicles.reduce((sum, v) => sum + v.seats, 0);
  const leadVehicle = [...vehicles].sort((a, b) => b.seats - a.seats)[0];
  const leadPhoto = leadVehicle?.cover_photo ?? leadVehicle?.photos[0]?.image;
  const previewPhotos = leadVehicle
    ? [
        ...(leadVehicle.cover_photo ? [{ image: leadVehicle.cover_photo, caption: leadVehicle.name }] : []),
        ...leadVehicle.photos,
      ].slice(0, 4)
    : [];
  const specs = [
    { n: totalSeats > 0 ? String(totalSeats) : "—", l: t("seats") },
    { n: "24/7", l: t("availability") },
    { n: "25km", l: t("fixedRange") },
  ];

  return (
    <section id="fleet" className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto grid max-w-[1360px] grid-cols-1 items-center gap-12 md:grid-cols-2">
        <div>
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[30px] font-semibold">{t("title")}</h2>
          <p className="mt-3.5 text-[15px] leading-relaxed text-muted">{t("description")}</p>
          <div className="mt-5 flex flex-wrap gap-7">
            {specs.map((spec) => (
              <div key={spec.l}>
                <div className="font-heading text-[26px] font-bold text-amber">{spec.n}</div>
                <div className="font-label text-xs tracking-[0.08em] text-muted uppercase">
                  {spec.l}
                </div>
              </div>
            ))}
          </div>
          {leadVehicle && (
            <div className="mt-6 rounded-[12px] border border-line bg-panel p-4">
              <div className="font-heading text-[18px] font-semibold">
                {leadVehicle.name} {leadVehicle.model}
              </div>
              <p className="mt-1 text-[13.5px] text-muted">{t("customerSeats", { count: leadVehicle.seats })}</p>
            </div>
          )}
          <Link
            href="/flota"
            className="mt-6 inline-flex rounded-md border border-amber px-5 py-3 text-[14px] font-semibold text-amber transition-colors hover:bg-amber/10"
          >
            {t("seeFleet")}
          </Link>
        </div>
        <div className="rounded-[14px] border border-line bg-panel p-3">
          <div className="flex h-[260px] items-center justify-center overflow-hidden rounded-[10px] bg-panel-2">
            {leadPhoto && leadVehicle ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={absoluteImageUrl(leadPhoto)}
                alt={`${leadVehicle.name} ${leadVehicle.model}`}
                className="h-full w-full object-cover"
              />
            ) : (
              <VanIcon />
            )}
          </div>
          {previewPhotos.length > 1 && (
            <div className="mt-3 grid grid-cols-4 gap-2">
              {previewPhotos.map((photo, index) => (
                <div key={`${photo.image}-${index}`} className="aspect-[4/3] overflow-hidden rounded-[7px] bg-panel-2">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={absoluteImageUrl("thumbnail" in photo && photo.thumbnail ? photo.thumbnail : photo.image)}
                    alt={photo.caption || leadVehicle?.name || t("title")}
                    className="h-full w-full object-cover"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      {vehicles.length === 0 && <p className="mt-4 text-[13px] text-muted">{t("empty")}</p>}
    </section>
  );
}
