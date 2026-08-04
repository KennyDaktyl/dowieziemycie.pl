"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { isCompletePhoneNumber } from "@/lib/countries";

import { PhoneInput } from "./phone-input";

/** Inline phone+SMS-code verification, embeddable directly in a form (as
 * opposed to LoginForm, which is the standalone /logowanie page and always
 * redirects to /panel on success). Used by booking-card.tsx so a
 * not-yet-logged-in customer can verify without losing the booking details
 * they already filled in — the caller decides what "verified" means via
 * onVerified, typically re-submitting the booking now that the auth cookie
 * is set. */
export function PhoneVerifyStep({
  phone,
  onPhoneChange,
  onVerified,
}: {
  phone: string;
  onPhoneChange: (phone: string) => void;
  onVerified: () => void;
}) {
  const t = useTranslations("Auth");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function requestOtp() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/request-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone }),
      });
      if (!res.ok) throw new Error();
      setStep("code");
    } catch {
      setError(t("errorRequest"));
    } finally {
      setLoading(false);
    }
  }

  async function verifyOtp() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone, code, intent: "customer" }),
      });
      if (!res.ok) throw new Error();
      onVerified();
    } catch {
      setError(t("errorVerify"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-3 rounded-[12px] border border-line bg-panel-2 p-4">
      {step === "phone" ? (
        <>
          <div className="flex flex-col gap-1.5">
            <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
              {t("phoneLabel")}
            </label>
            <PhoneInput value={phone} onChange={onPhoneChange} placeholder={t("phonePlaceholder")} />
          </div>
          <button
            type="button"
            onClick={requestOtp}
            disabled={loading || !isCompletePhoneNumber(phone)}
            className="w-full rounded-[9px] bg-amber py-[13px] text-[15px] font-bold text-[#1a1305] disabled:opacity-60"
          >
            {t("requestCode")}
          </button>
        </>
      ) : (
        <>
          <p className="text-[13px] text-muted">{t("codeSentTo", { phone })}</p>
          <div className="flex flex-col gap-1.5">
            <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
              {t("codeLabel")}
            </label>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder={t("codePlaceholder")}
              className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] tracking-[0.3em] text-text outline-none focus:border-amber"
            />
          </div>
          <button
            type="button"
            onClick={verifyOtp}
            disabled={loading || code.length !== 6}
            className="w-full rounded-[9px] bg-amber py-[13px] text-[15px] font-bold text-[#1a1305] disabled:opacity-60"
          >
            {t("verifyCode")}
          </button>
          <button type="button" onClick={() => setStep("phone")} className="text-[12.5px] text-muted underline">
            {t("changePhone")}
          </button>
        </>
      )}

      {error && <div className="text-center text-xs font-semibold text-red">{error}</div>}
      <p className="text-center text-[11.5px] leading-relaxed text-muted">{t("sessionNote")}</p>
    </div>
  );
}
