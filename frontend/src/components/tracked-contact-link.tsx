"use client";

import type { ReactNode } from "react";

import { trackEvent } from "@/lib/analytics";

/** tel:/WhatsApp link that reports click_call / click_whatsapp (with the
 * page slug, no personal data) — Enhanced Measurement never sees these. */
export function TrackedContactLink({
  kind,
  href,
  pageSlug,
  className,
  children,
}: {
  kind: "call" | "whatsapp";
  href: string;
  pageSlug: string;
  className?: string;
  children: ReactNode;
}) {
  const external = kind === "whatsapp";
  return (
    <a
      href={href}
      onClick={() => trackEvent(kind === "call" ? "click_call" : "click_whatsapp", { page_slug: pageSlug })}
      className={className}
      {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
    >
      {children}
    </a>
  );
}
