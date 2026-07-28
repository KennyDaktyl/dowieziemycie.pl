import { getTranslations } from "next-intl/server";

export async function StatusLegendSection() {
  const t = await getTranslations("StatusLegend");

  const statuses = [
    { label: t("offline"), color: "#8B96A3", description: t("offlineDesc") },
    { label: t("available"), color: "#3ECF8E", description: t("availableDesc") },
    { label: t("enRoute"), color: "#F5A623", description: t("enRouteDesc") },
    { label: t("busy"), color: "#E5484D", description: t("busyDesc") },
  ];

  return (
    <section id="customer-panel" className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[600px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
          <p className="mt-3 text-[15.5px] leading-relaxed text-muted">{t("description")}</p>
        </div>
        <div className="flex flex-wrap gap-4">
          {statuses.map((status) => (
            <div
              key={status.label}
              className="min-w-[190px] rounded-md border border-line bg-panel p-[14px_18px]"
              style={{ borderLeft: `4px solid ${status.color}` }}
            >
              <div className="font-heading text-[15px] font-bold">{status.label}</div>
              <div className="mt-[3px] text-[13px]" style={{ color: status.color }}>
                {status.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
