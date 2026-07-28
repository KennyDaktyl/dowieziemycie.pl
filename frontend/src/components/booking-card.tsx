"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { Link } from "@/i18n/navigation";
import { publicApiBaseUrl } from "@/lib/api";
import type { AddressSuggestion } from "@/lib/geocode";
import { reverseGeocode } from "@/lib/geocode";
import type { RouteEstimate } from "@/lib/types";

import { AddressSearchField } from "./address-search-field";
import { PriceMeter } from "./price-meter";

const BookingMap = dynamic(() => import("./booking-map").then((m) => m.BookingMap), {
  ssr: false,
  loading: () => <div className="h-[240px] w-full animate-pulse rounded-lg bg-panel-2 lg:h-full" />,
});

const MAX_PASSENGERS = 7;

type LatLng = { lat: number; lng: number };

function defaultDateTime() {
  const inThreeHours = new Date(Date.now() + 3 * 60 * 60 * 1000);
  const pad = (n: number) => String(n).padStart(2, "0");
  return {
    date: `${inThreeHours.getFullYear()}-${pad(inThreeHours.getMonth() + 1)}-${pad(inThreeHours.getDate())}`,
    time: `${pad(inThreeHours.getHours())}:${pad(inThreeHours.getMinutes())}`,
  };
}

export function BookingCard() {
  const t = useTranslations("BookingForm");
  const tTiers = useTranslations("PricingTiers");

  const [pickup, setPickup] = useState<LatLng | null>(null);
  const [pickupText, setPickupText] = useState("");
  const [dropoff, setDropoff] = useState<LatLng | null>(null);
  const [dropoffText, setDropoffText] = useState("");
  const [activeField, setActiveField] = useState<"pickup" | "dropoff">("pickup");
  const [locating, setLocating] = useState(false);
  const [{ date, time }, setDateTime] = useState(defaultDateTime);
  const [passengers, setPassengers] = useState(1);
  const [couponCode, setCouponCode] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error" | "unauthenticated">("idle");
  const [estimate, setEstimate] = useState<RouteEstimate | null>(null);
  const [estimating, setEstimating] = useState(false);

  useEffect(() => {
    if (!pickup || !dropoff || !date) return;
    const scheduledAt = new Date(`${date}T${time}:00`).toISOString();
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setEstimating(true);
      try {
        const params = new URLSearchParams({
          pickup_lat: String(pickup.lat),
          pickup_lng: String(pickup.lng),
          dropoff_lat: String(dropoff.lat),
          dropoff_lng: String(dropoff.lng),
          scheduled_at: scheduledAt,
        });
        const res = await fetch(`${publicApiBaseUrl()}/api/route-estimate/?${params}`, {
          signal: controller.signal,
        });
        if (res.ok) setEstimate(await res.json());
      } catch {
        // ignore — stale/aborted request or transient network hiccup
      } finally {
        setEstimating(false);
      }
    }, 500);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [pickup, dropoff, date, time]);

  async function handleUseMyLocation() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        setPickup(coords);
        setActiveField("pickup");
        const address = await reverseGeocode(coords.lat, coords.lng);
        if (address) setPickupText(address);
        setLocating(false);
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }

  function handleSelectSuggestion(field: "pickup" | "dropoff", s: AddressSuggestion) {
    const coords = { lat: s.lat, lng: s.lng };
    if (field === "pickup") {
      setPickup(coords);
      setPickupText(s.label);
    } else {
      setDropoff(coords);
      setDropoffText(s.label);
    }
  }

  async function handleMapChange(field: "pickup" | "dropoff", pos: LatLng) {
    if (field === "pickup") setPickup(pos);
    else setDropoff(pos);
    const address = await reverseGeocode(pos.lat, pos.lng);
    if (address) {
      if (field === "pickup") setPickupText(address);
      else setDropoffText(address);
    }
  }

  async function handleSubmit() {
    if (!pickup || !dropoff || !date) return;
    setStatus("submitting");
    try {
      const scheduledAt = new Date(`${date}T${time}:00`).toISOString();
      const res = await fetch("/api/bookings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pickup_address: pickupText,
          pickup_lat: pickup.lat,
          pickup_lng: pickup.lng,
          dropoff_address: dropoffText,
          dropoff_lat: dropoff.lat,
          dropoff_lng: dropoff.lng,
          scheduled_at: scheduledAt,
          passenger_count: passengers,
          coupon_code: couponCode || undefined,
        }),
      });
      if (res.status === 401) {
        setStatus("unauthenticated");
        return;
      }
      setStatus(res.ok ? "success" : "error");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="rounded-[14px] border border-line bg-panel p-[22px] lg:p-7">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[400px_1fr] lg:gap-8">
        <div className="flex flex-col gap-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-1">
            <AddressSearchField
              label={t("from")}
              placeholder={t("fromPlaceholder")}
              value={pickupText}
              onTextChange={setPickupText}
              onFocus={() => setActiveField("pickup")}
              onSelect={(s) => handleSelectSuggestion("pickup", s)}
            />
            <AddressSearchField
              label={t("to")}
              placeholder={t("toPlaceholder")}
              value={dropoffText}
              onTextChange={setDropoffText}
              onFocus={() => setActiveField("dropoff")}
              onSelect={(s) => handleSelectSuggestion("dropoff", s)}
            />
          </div>

          <button
            type="button"
            onClick={handleUseMyLocation}
            disabled={locating}
            className="text-left text-[12.5px] font-semibold text-amber transition-opacity hover:opacity-80 disabled:opacity-50"
          >
            📍 {locating ? t("locating") : t("useMyLocation")}
          </button>
        </div>

        <div className="flex flex-col lg:row-span-2 lg:h-full">
          <p className="mb-1.5 text-[11.5px] text-muted">{t("mapCaption")}</p>
          <div className="flex-1 overflow-hidden rounded-lg border border-line">
            <BookingMap
              pickup={pickup}
              dropoff={dropoff}
              activeField={activeField}
              onPickupChange={(pos) => handleMapChange("pickup", pos)}
              onDropoffChange={(pos) => handleMapChange("dropoff", pos)}
            />
          </div>
        </div>

        <div className="flex flex-col gap-3">
          {pickup && dropoff && estimate && (
            <div className="my-0.5 flex items-center gap-2">
              <span className="h-[7px] w-[7px] rounded-full bg-muted" />
              <span className="h-px flex-1 bg-[repeating-linear-gradient(90deg,var(--color-muted)_0_4px,transparent_4px_8px)] opacity-50" />
              <span className="font-label text-xs tracking-[0.05em] text-muted">
                {estimate.distance_km} {t("km")}
              </span>
              <span className="h-px flex-1 bg-[repeating-linear-gradient(90deg,var(--color-muted)_0_4px,transparent_4px_8px)] opacity-50" />
              <span className="h-[7px] w-[7px] rounded-full bg-amber" />
            </div>
          )}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("date")}
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDateTime((prev) => ({ ...prev, date: e.target.value }))}
                className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("time")}
              </label>
              <input
                type="time"
                value={time}
                onChange={(e) => setDateTime((prev) => ({ ...prev, time: e.target.value }))}
                className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("passengers")}
              </label>
              <select
                value={passengers}
                onChange={(e) => setPassengers(Number(e.target.value))}
                className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
              >
                {Array.from({ length: MAX_PASSENGERS }, (_, i) => i + 1).map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("couponCode")}
              </label>
              <input
                type="text"
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
              />
            </div>
          </div>

          <div className="rounded-[10px] border border-line bg-panel-2 px-4 py-3.5">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-label text-xs font-semibold tracking-[0.1em] text-muted uppercase">
                  {t("priceLabel")}
                </div>
                <div className="mt-0.5 text-[11.5px] text-muted">{t("priceSub")}</div>
              </div>
              {!pickup || !dropoff ? (
                <div className="font-heading text-lg font-semibold text-muted">{t("customQuote")}</div>
              ) : estimating ? (
                <div className="text-[13px] text-muted">{t("estimating")}</div>
              ) : estimate?.price != null ? (
                <PriceMeter target={estimate.price} />
              ) : (
                <div className="font-heading text-lg font-semibold text-muted">{t("customQuote")}</div>
              )}
            </div>
            {pickup && dropoff && estimate && estimate.price != null && (
              <div className="mt-2 border-t border-line pt-2 text-[11.5px] text-muted">
                {estimate.is_reserved ? tTiers("reserved") : tTiers("onDemand")}
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={status === "submitting" || !date || !pickup || !dropoff}
            className="w-full rounded-[9px] bg-amber py-[15px] text-[15.5px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:opacity-60"
          >
            {t("submit")}
          </button>

          {status === "success" && (
            <div className="text-center text-xs font-semibold text-green">{t("success")}</div>
          )}
          {status === "error" && (
            <div className="text-center text-xs font-semibold text-red">{t("error")}</div>
          )}
          {status === "unauthenticated" && (
            <div className="text-center text-xs font-semibold text-amber">
              <Link href="/logowanie" className="underline">
                {t("submitLoginFirst")}
              </Link>
            </div>
          )}

          <div className="text-center text-xs text-muted">{t("footnote")}</div>
        </div>
      </div>
    </div>
  );
}
