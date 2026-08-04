"use client";

import { useEffect, useState } from "react";

import { publicApiBaseUrl, withSiteHeader } from "./api";
import type { RouteEstimate } from "./types";

const POLL_INTERVAL_MS = 20000;

// Raw browser geolocation floats carry far more precision than the
// backend's DecimalField(max_digits=9, decimal_places=6) accepts — sending
// them as-is gets the whole request rejected with a 400.
function round6(value: number): number {
  return Math.round(value * 1e6) / 1e6;
}

/** Live distance/ETA between the driver and the customer, shown right on
 * the booking card — a lightweight REST poll (driver position + the
 * customer's own geolocation, fed into the same public route-estimate
 * endpoint the booking forms use) rather than opening the full tracker
 * page's WebSocket just for a summary line. Silently returns null if the
 * customer never grants location access. */
export function useDriverEta(bookingId: number, enabled: boolean): RouteEstimate | null {
  const [estimate, setEstimate] = useState<RouteEstimate | null>(null);

  useEffect(() => {
    if (!enabled) {
      setEstimate(null);
      return;
    }
    let cancelled = false;

    async function tick() {
      try {
        const posRes = await fetch(`/api/bookings/${bookingId}/driver-position`, { cache: "no-store" });
        if (!posRes.ok) return;
        const pos: { lat: string | null; lng: string | null } = await posRes.json();
        if (pos.lat == null || pos.lng == null) return;

        const myPos = await new Promise<GeolocationPosition | null>((resolve) => {
          if (!("geolocation" in navigator)) {
            resolve(null);
            return;
          }
          navigator.geolocation.getCurrentPosition(resolve, () => resolve(null), {
            enableHighAccuracy: true,
            timeout: 8000,
            maximumAge: 15000,
          });
        });
        if (!myPos || cancelled) return;

        const params = new URLSearchParams({
          pickup_lat: pos.lat,
          pickup_lng: pos.lng,
          dropoff_lat: String(round6(myPos.coords.latitude)),
          dropoff_lng: String(round6(myPos.coords.longitude)),
          scheduled_at: new Date().toISOString(),
        });
        const res = await fetch(`${publicApiBaseUrl()}/api/route-estimate/?${params}`, {
          headers: withSiteHeader(),
        });
        if (res.ok && !cancelled) setEstimate(await res.json());
      } catch {
        // ignore — transient network hiccup, next tick tries again
      }
    }

    tick();
    const interval = setInterval(tick, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [bookingId, enabled]);

  return estimate;
}
