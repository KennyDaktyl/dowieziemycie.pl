"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { useRouter } from "@/i18n/navigation";
import { isCompletePhoneNumber } from "@/lib/countries";
import { saveDriverSession } from "@/lib/driver-auth";

import { PhoneInput } from "./phone-input";

export function LoginForm() {
  const t = useTranslations("Auth");
  const router = useRouter();

  const [step, setStep] = useState<"phone" | "code">("phone");
  const [phone, setPhone] = useState("+48");
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
        body: JSON.stringify({ phone, code }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error();

      if (data.role === "driver") {
        saveDriverSession(data.access, data.refresh, data.driver);
        router.push("/kierowca/panel");
      } else {
        router.push("/moje-kursy");
        router.refresh();
      }
    } catch {
      setError(t("errorVerify"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm rounded-[14px] border border-line bg-panel p-[22px]">
      <h1 className="font-heading mb-5 text-xl font-semibold">{t("title")}</h1>

      {step === "phone" ? (
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
              {t("phoneLabel")}
            </label>
            <PhoneInput value={phone} onChange={setPhone} placeholder={t("phonePlaceholder")} />
          </div>
          <button
            type="button"
            onClick={requestOtp}
            disabled={loading || !isCompletePhoneNumber(phone)}
            className="w-full rounded-[9px] bg-amber py-[13px] text-[15px] font-bold text-[#1a1305] disabled:opacity-60"
          >
            {t("requestCode")}
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
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
          <button
            type="button"
            onClick={() => setStep("phone")}
            className="text-[12.5px] text-muted underline"
          >
            {t("changePhone")}
          </button>
        </div>
      )}

      {error && <div className="mt-3 text-center text-xs font-semibold text-red">{error}</div>}
      <p className="mt-4 text-center text-[11.5px] leading-relaxed text-muted">{t("sessionNote")}</p>
    </div>
  );
}
