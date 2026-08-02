"use client";

import { useState } from "react";

import { publicApiBaseUrl, withSiteHeader } from "@/lib/api";

import { BookingTracker } from "./booking-tracker";

type TrackResult = {
  booking_id: number;
  driver_name: string | null;
  vehicle_name: string | null;
};

export function TrackByCode() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState<TrackResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${publicApiBaseUrl()}/api/tracking/track-by-code/`, {
        method: "POST",
        headers: withSiteHeader({ "Content-Type": "application/json" }),
        body: JSON.stringify({ code }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => null);
        throw new Error(data?.detail ?? "Nieprawidłowy lub wygasły kod.");
      }
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nie udało się sprawdzić kodu.");
    } finally {
      setLoading(false);
    }
  }

  if (result) {
    return (
      <BookingTracker
        bookingId={result.booking_id}
        code={code}
        driverName={result.driver_name}
        driverVehicle={result.vehicle_name}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-[360px]">
      <label className="mb-2 block text-[13px] font-semibold tracking-wide text-muted uppercase">
        Kod kursu (4 cyfry)
      </label>
      <input
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 4))}
        inputMode="numeric"
        maxLength={4}
        placeholder="0000"
        className="w-full rounded-md border border-line bg-panel px-4 py-3 text-center text-[24px] font-bold tracking-[0.3em] text-text outline-none focus:border-amber"
      />
      {error && <p className="mt-3 text-center text-[13px] text-red">{error}</p>}
      <button
        type="submit"
        disabled={code.length !== 4 || loading}
        className="mt-4 w-full rounded-md bg-amber py-3 text-[14px] font-semibold text-[#1a1305] transition-opacity disabled:opacity-50"
      >
        {loading ? "Sprawdzam…" : "Śledź kierowcę"}
      </button>
    </form>
  );
}
