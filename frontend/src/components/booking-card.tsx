"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Link } from "@/i18n/navigation";
import { publicApiBaseUrl, withSiteHeader } from "@/lib/api";
import type { AddressSuggestion } from "@/lib/geocode";
import { reverseGeocode } from "@/lib/geocode";
import { absoluteImageUrl } from "@/lib/images";
import type { DriverEta, RouteEstimate, Vehicle } from "@/lib/types";

import { AddressSearchField } from "./address-search-field";
import { PhoneVerifyStep } from "./phone-verify-step";
import { PriceMeter } from "./price-meter";

const BookingMap = dynamic(() => import("./booking-map").then((m) => m.BookingMap), {
  ssr: false,
  loading: () => <div className="h-[240px] w-full animate-pulse rounded-lg bg-panel-2 lg:h-full" />,
});

const DEFAULT_MAX_PASSENGERS = 4;

// "How soon can a driver reach you" only means anything for a ride
// happening soon — it's computed from whichever driver happens to be
// active *right now*, which has no bearing on who ends up assigned to a
// ride booked weeks or months out. Showing it regardless of the picked
// date was confusing a "driver busy" state that's true this instant into
// looking like a reason a September booking couldn't be made.
const DRIVER_ETA_MAX_HOURS_AHEAD = 6;

const LEG_LABEL_KEYS = {
  direct_to_pickup: "legDirectToPickup",
  to_current_dropoff: "legToCurrentDropoff",
  dropoff_to_new_pickup: "legDropoffToNewPickup",
} as const;

type LatLng = { lat: number; lng: number };

// Geocoders (Nominatim) and the browser's Geolocation API can return more than
// 6 decimal places, which the backend's DecimalField(decimal_places=6) rejects
// outright (400, no partial match) — round at the source so every downstream
// fetch (route estimate, driver ETA, the booking itself) always gets a value
// the API will actually accept.
function roundCoord(n: number): number {
  return Math.round(n * 1e6) / 1e6;
}

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
  const tEta = useTranslations("DriverEta");
  const router = useRouter();

  const [pickup, setPickup] = useState<LatLng | null>(null);
  const [pickupText, setPickupText] = useState("");
  const [dropoff, setDropoff] = useState<LatLng | null>(null);
  const [dropoffText, setDropoffText] = useState("");
  const [activeField, setActiveField] = useState<"pickup" | "dropoff">("pickup");
  const [locating, setLocating] = useState(false);
  const [{ date, time }, setDateTime] = useState(defaultDateTime);
  const [passengers, setPassengers] = useState(1);
  const [childSeatAges, setChildSeatAges] = useState<number[]>([]);
  const [bikeCount, setBikeCount] = useState(0);
  const [couponCode, setCouponCode] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerEmail, setCustomerEmail] = useState("");
  const [phone, setPhone] = useState("+48");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error" | "unauthenticated">("idle");
  const [estimate, setEstimate] = useState<RouteEstimate | null>(null);
  const [estimating, setEstimating] = useState(false);
  const [driverEta, setDriverEta] = useState<DriverEta | null>(null);
  const [etaLoading, setEtaLoading] = useState(false);
  const [availability, setAvailability] = useState<"checking" | "available" | "unavailable">("checking");
  const [attemptedSubmit, setAttemptedSubmit] = useState(false);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${publicApiBaseUrl()}/api/fleet/availability/`, {
          signal: controller.signal,
          headers: withSiteHeader(),
        });
        const data = await res.json();
        setAvailability(data.available ? "available" : "unavailable");
      } catch {
        // Fail open — a hiccup on this check shouldn't block the whole form;
        // the backend enforces the same rule again at actual submit time.
        setAvailability("available");
      }
    }, 0);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${publicApiBaseUrl()}/api/fleet/vehicles/`, {
          signal: controller.signal,
          headers: withSiteHeader(),
        });
        if (!res.ok) return;
        const data = (await res.json()) as Vehicle[];
        const activeVehicles = data.sort((a, b) => b.seats - a.seats);
        const maxSeats = activeVehicles[0]?.seats ?? DEFAULT_MAX_PASSENGERS;
        setVehicles(activeVehicles);
        setPassengers((value) => Math.min(value, maxSeats));
        setChildSeatAges((ages) => ages.slice(0, maxSeats));
      } catch {
        // Fleet preview is helpful, but not required to submit the form.
      }
    }, 0);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, []);

  const scheduledSoon =
    !date || new Date(`${date}T${time || "00:00"}:00`).getTime() - Date.now() <= DRIVER_ETA_MAX_HOURS_AHEAD * 3600_000;
  const maxPassengers = vehicles[0]?.seats ?? DEFAULT_MAX_PASSENGERS;
  const previewVehicle = vehicles[0] ?? null;
  const previewVehiclePhoto = previewVehicle?.cover_photo ?? previewVehicle?.photos[0]?.thumbnail ?? previewVehicle?.photos[0]?.image;

  useEffect(() => {
    if (!pickup || !scheduledSoon) {
      setDriverEta(null);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      setEtaLoading(true);
      try {
        const params = new URLSearchParams({
          pickup_lat: String(pickup.lat),
          pickup_lng: String(pickup.lng),
        });
        const res = await fetch(`${publicApiBaseUrl()}/api/fleet/driver-eta/?${params}`, {
          signal: controller.signal,
          headers: withSiteHeader(),
        });
        if (res.ok) setDriverEta(await res.json());
      } catch {
        // ignore — stale/aborted request or transient network hiccup
      } finally {
        setEtaLoading(false);
      }
    }, 500);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [pickup, scheduledSoon]);

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
          headers: withSiteHeader(),
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
        const coords = { lat: roundCoord(pos.coords.latitude), lng: roundCoord(pos.coords.longitude) };
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
    const coords = { lat: roundCoord(s.lat), lng: roundCoord(s.lng) };
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

  function addChildSeat() {
    setChildSeatAges((ages) => {
      if (ages.length >= maxPassengers) return ages;
      const next = [...ages, 3];
      if (next.length > passengers) setPassengers(next.length);
      return next;
    });
  }

  function updateChildSeatAge(index: number, age: number) {
    setChildSeatAges((ages) => ages.map((item, i) => (i === index ? age : item)));
  }

  function removeChildSeat(index: number) {
    setChildSeatAges((ages) => ages.filter((_, i) => i !== index));
  }

  async function handleSubmit(): Promise<boolean> {
    if (!pickup || !dropoff || !date || !customerName) {
      setAttemptedSubmit(true);
      return false;
    }
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
          child_seat_ages: childSeatAges,
          bike_count: bikeCount,
          coupon_code: couponCode || undefined,
          customer_name: customerName,
          customer_email: customerEmail || undefined,
        }),
      });
      if (res.status === 401) {
        setStatus("unauthenticated");
        return false;
      }
      setStatus(res.ok ? "success" : "error");
      return res.ok;
    } catch {
      setStatus("error");
      return false;
    }
  }

  // The customer just proved who they are — land them in the panel where
  // the booking they just made is now visible, instead of leaving them on
  // the same form looking at a small inline success message.
  async function handleVerifiedSubmit() {
    const ok = await handleSubmit();
    if (ok) {
      router.push("/moje-kursy");
      router.refresh();
    }
  }

  if (availability === "unavailable") {
    return (
      <div className="rounded-[14px] border border-line bg-panel p-[22px] text-center lg:p-10">
        <div className="font-heading text-lg font-semibold">{t("unavailableTitle")}</div>
        <p className="mt-2 text-[14px] text-muted">{t("unavailableBody")}</p>
      </div>
    );
  }

  return (
    <div className="rounded-[14px] border border-line bg-panel p-[22px] lg:p-7">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[400px_1fr] lg:gap-8">
        <div className="flex flex-col gap-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-1">
            <div className="flex flex-col gap-1.5">
              <AddressSearchField
                label={t("from")}
                placeholder={t("fromPlaceholder")}
                value={pickupText}
                onTextChange={setPickupText}
                onFocus={() => setActiveField("pickup")}
                onSelect={(s) => handleSelectSuggestion("pickup", s)}
                onClear={() => setPickup(null)}
                required
                error={attemptedSubmit && !pickup}
              />
              <button
                type="button"
                onClick={handleUseMyLocation}
                disabled={locating}
                className="text-left text-[12.5px] font-semibold text-amber transition-opacity hover:opacity-80 disabled:opacity-50"
              >
                📍 {locating ? t("locating") : t("useMyLocation")}
              </button>
            </div>
            <AddressSearchField
              label={t("to")}
              placeholder={t("toPlaceholder")}
              value={dropoffText}
              onTextChange={setDropoffText}
              onFocus={() => setActiveField("dropoff")}
              onSelect={(s) => handleSelectSuggestion("dropoff", s)}
              onClear={() => setDropoff(null)}
              required
              error={attemptedSubmit && !dropoff}
            />
          </div>
        </div>

        <div className="flex flex-col lg:row-span-2 lg:h-full">
          <p className="mb-1.5 text-[11.5px] text-muted">{t("mapCaption")}</p>
          <div className="flex-1 overflow-hidden rounded-lg border border-line">
            <BookingMap
              pickup={pickup}
              dropoff={dropoff}
              activeField={activeField}
              routeGeometry={estimate?.geometry}
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
              <span className="font-label text-xs tracking-[0.05em] text-muted whitespace-nowrap">
                {estimate.distance_km} {t("km")} · {Math.round(estimate.duration_min)} {t("min")}
              </span>
              <span className="h-px flex-1 bg-[repeating-linear-gradient(90deg,var(--color-muted)_0_4px,transparent_4px_8px)] opacity-50" />
              <span className="h-[7px] w-[7px] rounded-full bg-amber" />
            </div>
          )}

          {pickup && (etaLoading || driverEta) && (
            <div className="rounded-[10px] border border-line bg-panel-2 px-4 py-3">
              <div className="font-label text-xs font-semibold tracking-[0.1em] text-muted uppercase">
                {tEta("title")}
              </div>
              {etaLoading && !driverEta ? (
                <div className="mt-1 text-[13px] text-muted">{tEta("estimating")}</div>
              ) : driverEta?.available && driverEta.eta_minutes != null ? (
                <>
                  <div className="mt-1 font-heading text-[16px] font-bold text-green">
                    {tEta("eta", { min: driverEta.eta_minutes })}
                  </div>
                  {driverEta.legs && driverEta.legs.length > 1 && (
                    <ul className="mt-1.5 flex flex-col gap-0.5 text-[12px] text-muted">
                      {driverEta.legs.map((leg, i) => (
                        <li key={i}>
                          {leg.distance_km} {t("km")} — {tEta(LEG_LABEL_KEYS[leg.leg_type])}
                        </li>
                      ))}
                    </ul>
                  )}
                </>
              ) : (
                <div className="mt-1 text-[13px] text-muted">{tEta("unavailable")}</div>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("date")} <span className="text-red">*</span>
              </label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDateTime((prev) => ({ ...prev, date: e.target.value }))}
                className={`rounded-lg border bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber ${
                  attemptedSubmit && !date ? "border-red" : "border-line"
                }`}
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

          <div className="rounded-[10px] border border-line bg-panel-2 p-3">
            {previewVehicle ? (
              <div className="flex gap-3">
                <div className="h-[82px] w-[112px] shrink-0 overflow-hidden rounded-[8px] border border-line bg-panel">
                  {previewVehiclePhoto ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={absoluteImageUrl(previewVehiclePhoto)}
                      alt={previewVehicle.name}
                      className="h-full w-full object-cover"
                    />
                  ) : null}
                </div>
                <div className="min-w-0">
                  <div className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                    {t("vehiclePreviewTitle")}
                  </div>
                  <div className="mt-1 font-heading text-[16px] font-semibold text-text">{previewVehicle.name}</div>
                  <div className="mt-1 text-[12.5px] text-muted">
                    {t("vehiclePreviewSeats", { count: previewVehicle.seats })}
                  </div>
                  <Link href="/flota" className="mt-2 inline-block text-[12.5px] font-semibold text-amber hover:underline">
                    {t("vehiclePreviewLink")}
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-[13px] text-muted">{t("vehiclePreviewEmpty")}</div>
            )}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("passengers")}
              </label>
              <select
                value={passengers}
                onChange={(e) => {
                  const nextPassengers = Number(e.target.value);
                  setPassengers(nextPassengers);
                  setChildSeatAges((ages) => ages.slice(0, nextPassengers));
                }}
                className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
              >
                {Array.from({ length: maxPassengers }, (_, i) => i + 1).map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
              <p className="text-[11.5px] text-muted">{t("passengersHint", { count: maxPassengers })}</p>
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

          <div className="rounded-[10px] border border-line bg-panel-2 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                  {t("childSeats")}
                </div>
                <p className="mt-1 text-[12.5px] leading-relaxed text-muted">{t("childSeatsHint")}</p>
              </div>
              <button
                type="button"
                onClick={addChildSeat}
                disabled={childSeatAges.length >= maxPassengers}
                className="shrink-0 rounded-md border border-amber px-3 py-2 text-[13px] font-semibold text-amber transition-colors hover:bg-amber/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {t("addChild")}
              </button>
            </div>
            {childSeatAges.length > 0 && (
              <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                {childSeatAges.map((age, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <label className="sr-only">{t("childAge", { number: index + 1 })}</label>
                    <select
                      value={age}
                      onChange={(e) => updateChildSeatAge(index, Number(e.target.value))}
                      className="min-w-0 flex-1 rounded-lg border border-line bg-panel px-3 py-2.5 text-[14px] text-text outline-none focus:border-amber"
                      aria-label={t("childAge", { number: index + 1 })}
                    >
                      {Array.from({ length: 13 }, (_, i) => i).map((n) => (
                        <option key={n} value={n}>
                          {t("ageYears", { age: n })}
                        </option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => removeChildSeat(index)}
                      className="rounded-md border border-line px-3 py-2.5 text-[13px] font-semibold text-muted transition-colors hover:bg-panel hover:text-text"
                      aria-label={t("removeChild")}
                    >
                      x
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-[10px] border border-line bg-panel-2 p-4">
            <label className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={bikeCount > 0}
                onChange={(e) => setBikeCount(e.target.checked ? 1 : 0)}
                className="mt-1 h-4 w-4 accent-amber"
              />
              <span>
                <span className="font-label block text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                  {t("bikeTransport")}
                </span>
                <span className="mt-1 block text-[12.5px] leading-relaxed text-muted">{t("bikeTransportHint")}</span>
              </span>
            </label>
            {bikeCount > 0 && (
              <div className="mt-3 flex max-w-[220px] flex-col gap-1.5">
                <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                  {t("bikeCount")}
                </label>
                <select
                  value={bikeCount}
                  onChange={(e) => setBikeCount(Number(e.target.value))}
                  className="rounded-lg border border-line bg-panel px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
                >
                  {[1, 2, 3, 4].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("nameLabel")} <span className="text-red">*</span>
              </label>
              <input
                type="text"
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder={t("namePlaceholder")}
                className={`rounded-lg border bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber ${
                  attemptedSubmit && !customerName ? "border-red" : "border-line"
                }`}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                {t("emailLabel")}
              </label>
              <input
                type="email"
                value={customerEmail}
                onChange={(e) => setCustomerEmail(e.target.value)}
                placeholder={t("emailPlaceholder")}
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
                <div>
                  <PriceMeter target={estimate.price} />
                  <div className="mt-0.5 text-right text-[11px] text-muted">{t("vatNote")}</div>
                </div>
              ) : (
                <div className="font-heading text-lg font-semibold text-muted">{t("customQuote")}</div>
              )}
            </div>
            {pickup && dropoff && estimate && estimate.price != null && (
              <div className="mt-2 border-t border-line pt-2 text-[11.5px] text-muted">
                {estimate.pricing_mode === "local"
                  ? t("localFare")
                  : estimate.is_reserved
                    ? tTiers("reserved")
                    : tTiers("onDemand")}
              </div>
            )}
          </div>

          {status !== "unauthenticated" && (
            <button
              type="button"
              onClick={handleSubmit}
              disabled={status === "submitting" || !date || !pickup || !dropoff || !customerName}
              className="w-full rounded-[9px] bg-amber py-[15px] text-[15.5px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:opacity-60"
            >
              {t("submit")}
            </button>
          )}

          {status === "success" && (
            <div className="text-center text-xs font-semibold text-green">
              {t("success")}{" "}
              <Link href="/moje-kursy" className="underline">
                {t("successPanelLink")}
              </Link>
            </div>
          )}
          {status === "error" && (
            <div className="text-center text-xs font-semibold text-red">{t("error")}</div>
          )}
          {status === "unauthenticated" && (
            <div className="flex flex-col gap-3 rounded-[12px] border border-amber/35 bg-amber/10 p-4">
              <div>
                <div className="font-heading text-[17px] font-semibold">{t("verifyStepTitle")}</div>
                <p className="mt-1 text-[13px] leading-relaxed text-muted">{t("submitVerifyPhone")}</p>
              </div>
              <PhoneVerifyStep phone={phone} onPhoneChange={setPhone} onVerified={handleVerifiedSubmit} />
            </div>
          )}

          <div className="text-center text-xs text-muted">{t("footnote")}</div>
        </div>
      </div>
    </div>
  );
}
