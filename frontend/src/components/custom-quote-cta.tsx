"use client";

import { useTranslations } from "next-intl";

import { ObfuscatedEmail } from "@/components/obfuscated-email";

// Whenever the pricing engine can't return an automatic price (route too
// long, too far from base, etc.), the customer needs an obvious next step —
// not just a "custom quote" label with nothing to click. A client component
// (not async/server) so it also works inside booking-card.tsx, which is
// itself client-rendered. Not usable inside anything that's already an
// <a>/<Link> (nested anchors are invalid HTML) — the route/event card grids
// stay plain text and rely on their detail page carrying this instead.
export function CustomQuoteCta({
  phone,
  phoneDisplay,
  email,
  className,
}: {
  phone: string;
  phoneDisplay: string;
  email: string;
  className?: string;
}) {
  const t = useTranslations("CustomQuote");
  const [emailUser, emailDomain] = email.split("@");

  return (
    <div className={className}>
      <div className="font-heading text-lg font-semibold text-muted">{t("label")}</div>
      <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[12.5px] text-muted">
        <a href={`tel:${phone}`} className="font-semibold text-amber hover:underline">
          {phoneDisplay}
        </a>
        <span>{t("or")}</span>
        <ObfuscatedEmail user={emailUser} domain={emailDomain} className="font-semibold text-amber hover:underline" />
      </div>
    </div>
  );
}
