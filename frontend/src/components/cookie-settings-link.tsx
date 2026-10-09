"use client";

import { reopenConsentBanner } from "@/lib/analytics";

/** Reopens the cookie banner so a visitor can change an earlier decision
 * (GDPR) — a button, since it dispatches an event rather than navigating. */
export function CookieSettingsLink({ label, className }: { label: string; className?: string }) {
  return (
    <button type="button" onClick={reopenConsentBanner} className={className}>
      {label}
    </button>
  );
}
