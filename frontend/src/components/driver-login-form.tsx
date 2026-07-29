"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";

import { useRouter } from "@/i18n/navigation";
import { publicApiBaseUrl } from "@/lib/api";
import { saveDriverSession } from "@/lib/driver-auth";

export function DriverLoginForm() {
  const t = useTranslations("DriverLogin");
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${publicApiBaseUrl()}/api/fleet/driver/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? t("error"));
        return;
      }
      saveDriverSession(data.access, data.refresh, data.driver);
      router.push("/kierowca/panel");
    } catch {
      setError(t("error"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-sm rounded-[14px] border border-line bg-panel p-[22px]">
      <h1 className="font-heading mb-5 text-xl font-semibold">{t("title")}</h1>
      <div className="flex flex-col gap-3">
        <div className="flex flex-col gap-1.5">
          <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
            {t("username")}
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
            className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
            {t("password")}
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !username || !password}
          className="w-full rounded-[9px] bg-amber py-[13px] text-[15px] font-bold text-[#1a1305] disabled:opacity-60"
        >
          {loading ? t("loggingIn") : t("submit")}
        </button>
      </div>
      {error && <div className="mt-3 text-center text-xs font-semibold text-red">{error}</div>}
    </form>
  );
}
