"use client";

import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { CustomQuoteCta } from "@/components/custom-quote-cta";
import { ToastStack } from "@/components/toast";
import { Link } from "@/i18n/navigation";
import { publicApiBaseUrl, withSiteHeader } from "@/lib/api";
import type { AddressSuggestion } from "@/lib/geocode";
import { reverseGeocode } from "@/lib/geocode";
import { absoluteImageUrl } from "@/lib/images";
import type { ContactInfo, DriverEta, RouteEstimate, Vehicle } from "@/lib/types";
import { useToasts } from "@/lib/use-toasts";

import { AddressSearchField } from "./address-search-field";
import { PhoneVerifyStep } from "./phone-verify-step";
import { PriceMeter } from "./price-meter";

const BookingMap = dynamic(() => import("./booking-map").then((m) => m.BookingMap), {
  ssr: false,
  loading: () => <div className="h-[240px] w-full animate-pulse rounded-lg bg-panel-2 lg:h-full" />,
});

const DEFAULT_MAX_PASSENGERS = 4;
const FORM_STORAGE_KEY = "dowieziemycie:booking-form-draft";

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

export function BookingCard({ contact }: { contact: ContactInfo }) {
  const t = useTranslations("BookingForm");
  const tTiers = useTranslations("PricingTiers");
  const tEta = useTranslations("DriverEta");
  const router = useRouter();
  const { toasts, pushToast, dismissToast } = useToasts();

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
  const [couponStatus, setCouponStatus] = useState<"idle" | "checking" | "valid" | "invalid">("idle");
  const [couponDiscount, setCouponDiscount] = useState<{ discount_type: "PERCENT" | "FIXED"; value: number } | null>(
    null,
  );
  const [touched, setTouched] = useState<Record<string, boolean>>({});
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
  const [formHydrated, setFormHydrated] = useState(false);

  const dropoffInputRef = useRef<HTMLInputElement>(null);
  const dateInputRef = useRef<HTMLInputElement>(null);
  const mapSectionRef = useRef<HTMLDivElement>(null);

  function markTouched(field: string) {
    setTouched((prev) => ({ ...prev, [field]: true }));
  }

  function armMapField(field: "pickup" | "dropoff") {
    setActiveField(field);
    mapSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Restores whatever the customer had already typed if they navigate away
  // (e.g. to check /flota) and come back — sessionStorage rather than
  // localStorage since this is a working draft, not something that should
  // outlive the tab. Only ever read once, right after mount.
  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        const raw = sessionStorage.getItem(FORM_STORAGE_KEY);
        if (raw) {
          const saved = JSON.parse(raw);
          if (saved.pickup) setPickup(saved.pickup);
          if (saved.pickupText) setPickupText(saved.pickupText);
          if (saved.dropoff) setDropoff(saved.dropoff);
          if (saved.dropoffText) setDropoffText(saved.dropoffText);
          if (saved.date) setDateTime((prev) => ({ ...prev, date: saved.date }));
          if (saved.time) setDateTime((prev) => ({ ...prev, time: saved.time }));
          if (saved.passengers) setPassengers(saved.passengers);
          if (saved.childSeatAges) setChildSeatAges(saved.childSeatAges);
          if (saved.bikeCount != null) setBikeCount(saved.bikeCount);
          if (saved.couponCode) setCouponCode(saved.couponCode);
          if (saved.customerName) setCustomerName(saved.customerName);
          if (saved.customerEmail) setCustomerEmail(saved.customerEmail);
          if (saved.phone) setPhone(saved.phone);
        }
      } catch {
        // Corrupt or blocked storage — just start from a blank form.
      }
      setFormHydrated(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  // Waits for the restore above to finish (formHydrated) so this doesn't
  // immediately overwrite a just-restored draft with the pre-restore blank
  // values from that same first render.
  useEffect(() => {
    if (!formHydrated) return;
    try {
      sessionStorage.setItem(
        FORM_STORAGE_KEY,
        JSON.stringify({
          pickup, pickupText, dropoff, dropoffText, date, time,
          passengers, childSeatAges, bikeCount, couponCode,
          customerName, customerEmail, phone,
        }),
      );
    } catch {
      // Storage full/blocked (private browsing) — losing the draft on
      // navigation is an acceptable degradation, not worth surfacing.
    }
  }, [
    formHydrated, pickup, pickupText, dropoff, dropoffText, date, time,
    passengers, childSeatAges, bikeCount, couponCode, customerName, customerEmail, phone,
  ]);

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

  const maxPassengers = vehicles[0]?.seats ?? DEFAULT_MAX_PASSENGERS;
  const previewVehicle = vehicles[0] ?? null;
  const previewVehiclePhoto = previewVehicle?.cover_photo ?? previewVehicle?.photos[0]?.thumbnail ?? previewVehicle?.photos[0]?.image;
  const discountedPrice =
    estimate?.price != null && couponDiscount
      ? Math.max(
          couponDiscount.discount_type === "PERCENT"
            ? estimate.price * (1 - couponDiscount.value / 100)
            : estimate.price - couponDiscount.value,
          0,
        )
      : null;

  useEffect(() => {
    if (!pickup) {
      const timer = setTimeout(() => setDriverEta(null), 0);
      return () => clearTimeout(timer);
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
        if (res.ok) {
          setDriverEta(await res.json());
        } else {
          pushToast("error", t("etaFetchError"));
        }
      } catch (err) {
        if ((err as Error)?.name !== "AbortError") pushToast("error", t("etaFetchError"));
      } finally {
        setEtaLoading(false);
      }
    }, 500);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pickup]);

  useEffect(() => {
    if (!pickup || !dropoff || !date) {
      // Clears the stale route line/price/summary card instead of leaving
      // them stuck on-screen after the customer clears an address field.
      const timer = setTimeout(() => setEstimate(null), 0);
      return () => clearTimeout(timer);
    }
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
        if (res.ok) {
          setEstimate(await res.json());
        } else {
          pushToast("error", t("estimateFetchError"));
        }
      } catch (err) {
        if ((err as Error)?.name !== "AbortError") pushToast("error", t("estimateFetchError"));
      } finally {
        setEstimating(false);
      }
    }, 500);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pickup, dropoff, date, time]);

  async function handleUseMyLocation() {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const coords = { lat: roundCoord(pos.coords.latitude), lng: roundCoord(pos.coords.longitude) };
        setPickup(coords);
        markTouched("pickup");
        // Next step is picking the destination — either by typing or by
        // tapping the map, so just arm it rather than forcing keyboard focus.
        setActiveField("dropoff");
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
      markTouched("pickup");
      // Picked by typing — the customer is already in "keyboard mode", so
      // carry that momentum straight into the next field instead of making
      // them reach for it themselves.
      setActiveField("dropoff");
      dropoffInputRef.current?.focus();
    } else {
      setDropoff(coords);
      setDropoffText(s.label);
      markTouched("dropoff");
      dateInputRef.current?.focus();
    }
  }

  async function handleMapChange(field: "pickup" | "dropoff", pos: LatLng) {
    if (field === "pickup") {
      setPickup(pos);
      markTouched("pickup");
      // Guide the next tap straight to the destination — placing two pins
      // is meant to feel like consecutive steps on the same map, not a
      // detour back to the keyboard.
      setActiveField("dropoff");
    } else {
      setDropoff(pos);
      markTouched("dropoff");
    }
    const address = await reverseGeocode(pos.lat, pos.lng);
    if (address) {
      if (field === "pickup") setPickupText(address);
      else setDropoffText(address);
    }
  }

  async function handleApplyCoupon() {
    if (!couponCode) return;
    setCouponStatus("checking");
    try {
      const res = await fetch(
        `${publicApiBaseUrl()}/api/coupons/validate/?code=${encodeURIComponent(couponCode)}`,
        { headers: withSiteHeader() },
      );
      const data = await res.json();
      if (data.valid) {
        setCouponDiscount({ discount_type: data.discount_type, value: Number(data.value) });
        setCouponStatus("valid");
      } else {
        setCouponDiscount(null);
        setCouponStatus("invalid");
      }
    } catch {
      setCouponDiscount(null);
      setCouponStatus("invalid");
      pushToast("error", t("couponFetchError"));
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
      pushToast(res.ok ? "success" : "error", res.ok ? t("submitSuccessToast") : t("submitErrorToast"));
      if (res.ok) {
        try {
          sessionStorage.removeItem(FORM_STORAGE_KEY);
        } catch {
          // Nothing to clean up if storage was blocked in the first place.
        }
      }
      return res.ok;
    } catch {
      setStatus("error");
      pushToast("error", t("submitErrorToast"));
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

  // Rendered twice: once right under the trip summary (so the price is
  // visible without scrolling all the way to the submit button) and once
  // in its original spot further down, right where the customer expects it
  // just before booking.
  const priceBox = (
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
            {discountedPrice != null ? (
              <>
                <div className="text-right font-heading text-[15px] font-semibold text-muted line-through">
                  {estimate.price} zł
                </div>
                <PriceMeter target={discountedPrice} />
              </>
            ) : (
              <PriceMeter target={estimate.price} />
            )}
            <div className="mt-0.5 text-right text-[11px] text-muted">{t("vatNote")}</div>
          </div>
        ) : (
          <CustomQuoteCta
            phone={contact.phone}
            phoneDisplay={contact.phone_display}
            email={contact.email}
            className="text-right"
          />
        )}
      </div>
      {pickup && dropoff && estimate && estimate.price != null && (
        <div className="mt-2 flex flex-col gap-1 border-t border-line pt-2 text-[11.5px] text-muted">
          <span>
            {estimate.pricing_mode === "local"
              ? t("localFare")
              : estimate.is_reserved
                ? tTiers("reserved")
                : tTiers("onDemand")}
          </span>
          <span>
            {t("negotiateHint")}{" "}
            <a href={`tel:${contact.phone}`} className="font-semibold text-amber hover:underline">
              {contact.phone_display}
            </a>
          </span>
        </div>
      )}
    </div>
  );

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
                onBlur={() => markTouched("pickup")}
                onSelect={(s) => handleSelectSuggestion("pickup", s)}
                onClear={() => setPickup(null)}
                required
                error={(touched.pickup || attemptedSubmit) && !pickup}
                valid={!!pickup}
              />
              <div className="flex flex-wrap gap-x-4 gap-y-1">
                <button
                  type="button"
                  onClick={handleUseMyLocation}
                  disabled={locating}
                  className="text-left text-[12.5px] font-semibold text-amber transition-opacity hover:opacity-80 disabled:opacity-50"
                >
                  📍 {locating ? t("locating") : t("useMyLocation")}
                </button>
                <button
                  type="button"
                  onClick={() => armMapField("pickup")}
                  className="text-left text-[12.5px] font-semibold text-amber transition-opacity hover:opacity-80"
                >
                  🗺️ {t("pickOnMapFrom")}
                </button>
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <AddressSearchField
                ref={dropoffInputRef}
                label={t("to")}
                placeholder={t("toPlaceholder")}
                value={dropoffText}
                onTextChange={setDropoffText}
                onFocus={() => setActiveField("dropoff")}
                onBlur={() => markTouched("dropoff")}
                onSelect={(s) => handleSelectSuggestion("dropoff", s)}
                onClear={() => setDropoff(null)}
                required
                error={(touched.dropoff || attemptedSubmit) && !dropoff}
                valid={!!dropoff}
              />
              <button
                type="button"
                onClick={() => armMapField("dropoff")}
                className="text-left text-[12.5px] font-semibold text-amber transition-opacity hover:opacity-80"
              >
                🗺️ {t("pickOnMapTo")}
              </button>
            </div>
          </div>
        </div>

        <div ref={mapSectionRef} className="flex flex-col lg:sticky lg:top-6 lg:row-span-2 lg:self-start">
          <p className="mb-1.5 text-[11.5px] font-semibold text-amber">
            {activeField === "pickup" ? t("mapCaptionPickup") : t("mapCaptionDropoff")}
          </p>
          <div className="h-[240px] overflow-hidden rounded-lg border border-line md:h-[340px] lg:h-[min(480px,calc(100vh-140px))]">
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
            <div className="rounded-[10px] border border-line bg-panel-2 p-4">
              <div className="font-label mb-2.5 text-xs font-semibold tracking-[0.1em] text-muted uppercase">
                {t("summaryTitle")}
              </div>
              <div className="grid grid-cols-2 gap-x-3 gap-y-3 text-[13px]">
                <div className="col-span-2 sm:col-span-1">
                  <div className="text-[11px] tracking-wide text-muted uppercase">{t("summaryFrom")}</div>
                  <div className="mt-0.5 truncate font-semibold text-text" title={pickupText}>
                    {pickupText}
                  </div>
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <div className="text-[11px] tracking-wide text-muted uppercase">{t("summaryTo")}</div>
                  <div className="mt-0.5 truncate font-semibold text-text" title={dropoffText}>
                    {dropoffText}
                  </div>
                </div>
                <div>
                  <div className="text-[11px] tracking-wide text-muted uppercase">{t("summaryDistance")}</div>
                  <div className="font-heading mt-0.5 text-[19px] font-bold text-text">
                    {estimate.distance_km} {t("km")}
                  </div>
                </div>
                <div>
                  <div className="text-[11px] tracking-wide text-muted uppercase">{t("summaryDuration")}</div>
                  <div className="font-heading mt-0.5 text-[19px] font-bold text-text">
                    {Math.round(estimate.duration_min)} {t("min")}
                  </div>
                </div>
              </div>
            </div>
          )}

          {pickup && dropoff && estimate && priceBox}

          {pickup && (etaLoading || driverEta) && (
            <div className="rounded-[10px] border border-line bg-panel-2 px-4 py-3">
              <div className="font-label text-xs font-semibold tracking-[0.1em] text-muted uppercase">
                {tEta("title")}
              </div>
              {etaLoading && !driverEta ? (
                <div className="mt-1 text-[13px] text-muted">{tEta("estimating")}</div>
              ) : driverEta?.available && driverEta.eta_minutes != null ? (
                <>
                  <div className="mt-1 flex flex-wrap items-baseline gap-x-2">
                    <span className="font-heading text-[16px] font-bold text-green">
                      {tEta("eta", { min: driverEta.eta_minutes })}
                    </span>
                    {driverEta.legs && driverEta.legs.length > 0 && (
                      <span className="text-[12.5px] font-semibold text-muted">
                        · {driverEta.legs.reduce((sum, leg) => sum + leg.distance_km, 0).toFixed(1)} {t("km")}
                      </span>
                    )}
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
                  {driverEta.basis === "base" && (
                    <p className="mt-1 text-[11.5px] text-muted">{tEta("fromBase")}</p>
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
                ref={dateInputRef}
                type="date"
                value={date}
                onChange={(e) => setDateTime((prev) => ({ ...prev, date: e.target.value }))}
                onBlur={() => markTouched("date")}
                className={`rounded-lg border bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber ${
                  (touched.date || attemptedSubmit) && !date ? "border-red" : date ? "border-green" : "border-line"
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
                      alt={`${previewVehicle.name} ${previewVehicle.model}`}
                      className="h-full w-full object-cover"
                    />
                  ) : null}
                </div>
                <div className="min-w-0">
                  <div className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
                    {t("vehiclePreviewTitle")}
                  </div>
                  <div className="mt-1 font-heading text-[16px] font-semibold text-text">
                    {previewVehicle.name} {previewVehicle.model}
                  </div>
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

          <div className="flex max-w-[220px] flex-col gap-1.5">
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
                onBlur={() => markTouched("name")}
                placeholder={t("namePlaceholder")}
                className={`rounded-lg border bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber ${
                  (touched.name || attemptedSubmit) && !customerName
                    ? "border-red"
                    : customerName
                      ? "border-green"
                      : "border-line"
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

          {priceBox}

          <div className="rounded-[10px] border border-line bg-panel-2 p-4">
            <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
              {t("couponCode")}
            </label>
            <div className="mt-1.5 flex gap-2">
              <input
                type="text"
                value={couponCode}
                onChange={(e) => {
                  setCouponCode(e.target.value.toUpperCase());
                  setCouponStatus("idle");
                  setCouponDiscount(null);
                }}
                placeholder={t("couponPlaceholder")}
                className="min-w-0 flex-1 rounded-lg border border-line bg-panel px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
              />
              <button
                type="button"
                onClick={handleApplyCoupon}
                disabled={!couponCode || couponStatus === "checking"}
                className="shrink-0 rounded-lg border border-amber px-4 py-[11px] text-[13.5px] font-semibold text-amber transition-colors hover:bg-amber/10 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {couponStatus === "checking" ? t("couponChecking") : t("couponApply")}
              </button>
            </div>
            {couponStatus === "valid" && couponDiscount && (
              <p className="mt-1.5 text-[12.5px] font-semibold text-green">
                {couponDiscount.discount_type === "PERCENT"
                  ? t("couponValidPercent", { value: couponDiscount.value })
                  : t("couponValidFixed", { value: couponDiscount.value })}
              </p>
            )}
            {couponStatus === "invalid" && (
              <p className="mt-1.5 text-[12.5px] font-semibold text-red">{t("couponInvalid")}</p>
            )}
          </div>

          {status !== "unauthenticated" && (
            <>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={status === "submitting"}
                className="w-full rounded-[9px] bg-amber py-[15px] text-[15.5px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:opacity-60"
              >
                {t("submit")}
              </button>
              {attemptedSubmit && (!pickup || !dropoff || !date || !customerName) && (
                <p className="text-center text-[12.5px] font-semibold text-red">{t("missingFields")}</p>
              )}
            </>
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
      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
