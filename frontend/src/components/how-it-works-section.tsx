import { getTranslations } from "next-intl/server";

export async function HowItWorksSection() {
  const t = await getTranslations("HowItWorks");

  const steps = [
    { num: "01", title: t("step1Title"), body: t("step1Body") },
    { num: "02", title: t("step2Title"), body: t("step2Body") },
    { num: "03", title: t("step3Title"), body: t("step3Body") },
  ];

  return (
    <section id="how-it-works" className="border-t border-line px-6 py-[70px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="mb-10 max-w-[600px]">
          <span className="font-label text-[13px] font-semibold tracking-[0.16em] text-amber uppercase">
            {t("eyebrow")}
          </span>
          <h2 className="font-heading mt-2.5 text-[32px] font-semibold">{t("title")}</h2>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {steps.map((step) => (
            <div key={step.num} className="rounded-xl border border-line bg-panel p-[26px]">
              <div className="font-heading text-[34px] font-bold text-amber-dim">{step.num}</div>
              <h3 className="my-3.5 text-[17px] font-semibold">{step.title}</h3>
              <p className="text-[14px] leading-relaxed text-muted">{step.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
