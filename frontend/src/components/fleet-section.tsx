import { getTranslations } from "next-intl/server";

import { apiFetch } from "@/lib/api";
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
  const specs = [
    { n: totalSeats > 0 ? String(totalSeats) : "—", l: t("seats") },
    { n: "24/7", l: t("availability") },
    { n: "25km", l: t("fixedRange") },
  ];

  return (
    <section className="border-t border-line px-6 py-[70px]">
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
          {vehicles.length > 0 && (
            <ul className="mt-6 flex flex-col gap-2">
              {vehicles.map((v) => (
                <li key={v.id} className="text-[14px] text-text">
                  <span className="font-heading font-semibold">{v.name}</span>
                  {v.model && <span className="text-muted"> · {v.model}</span>}
                  <span className="text-muted"> · {v.seats} {t("seats").toLowerCase()}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex h-[260px] items-center justify-center rounded-2xl border border-line bg-gradient-to-br from-panel-2 to-panel">
          {(() => {
            const photo = vehicles[0]?.cover_photo ?? vehicles[0]?.photos[0]?.image;
            return photo ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={photo}
                alt={vehicles[0].name}
                className="h-full w-full rounded-2xl object-cover"
              />
            ) : (
              <VanIcon />
            );
          })()}
        </div>
      </div>
      {vehicles.length === 0 && <p className="mt-4 text-[13px] text-muted">{t("empty")}</p>}
    </section>
  );
}
