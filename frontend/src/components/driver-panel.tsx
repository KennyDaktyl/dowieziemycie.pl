"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useRef, useState } from "react";

import { useRouter } from "@/i18n/navigation";
import { wsBaseUrl } from "@/lib/api";
import {
  clearDriverSession,
  getDriverAccessToken,
  getDriverProfile,
  type DriverProfile,
} from "@/lib/driver-auth";

const STATUS_OPTIONS = ["DOSTEPNY", "JADACY_PO_KLIENTA", "W_KURSIE", "WRACA_DO_BAZY", "OFFLINE"] as const;
const POSITION_INTERVAL_MS = 10000;
const RECONNECT_BASE_MS = 2000;
const RECONNECT_MAX_MS = 15000;

type ConnectionState = "connecting" | "open" | "closed";

export function DriverPanel() {
  const t = useTranslations("DriverPanel");
  const router = useRouter();

  const [driver, setDriver] = useState<DriverProfile | null>(null);
  const [status, setStatus] = useState<(typeof STATUS_OPTIONS)[number]>("DOSTEPNY");
  const [connectionState, setConnectionState] = useState<ConnectionState>("connecting");
  const [lastSent, setLastSent] = useState<{ lat: number; lng: number } | null>(null);
  const [geoError, setGeoError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const statusRef = useRef(status);
  const lastSentRef = useRef(lastSent);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    lastSentRef.current = lastSent;
  }, [lastSent]);

  useEffect(() => {
    // Deferred so the setState calls happen inside a callback rather than
    // synchronously in the effect body.
    const timer = setTimeout(() => {
      const profile = getDriverProfile();
      if (!profile || !getDriverAccessToken()) {
        router.replace("/kierowca/logowanie");
        return;
      }
      setDriver(profile);
      setStatus(profile.status);
    }, 0);
    return () => clearTimeout(timer);
  }, [router]);

  const sendPosition = useCallback((coords: { lat: number; lng: number }, statusOverride?: string) => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({ lat: coords.lat, lng: coords.lng, status: statusOverride ?? statusRef.current }));
    setLastSent(coords);
  }, []);

  // WebSocket connection with capped exponential-backoff reconnect — drivers
  // keep this tab open for a whole shift on a mobile connection, so brief
  // drops are the normal case, not the exception.
  useEffect(() => {
    if (!driver) return;
    let cancelled = false;
    let retryDelay = RECONNECT_BASE_MS;
    let retryTimer: ReturnType<typeof setTimeout> | null = null;

    function connect() {
      const token = getDriverAccessToken();
      if (!token || cancelled) return;
      setConnectionState("connecting");
      const socket = new WebSocket(`${wsBaseUrl()}/ws/driver/track/?token=${token}`);
      socketRef.current = socket;

      socket.onopen = () => {
        retryDelay = RECONNECT_BASE_MS;
        setConnectionState("open");
        if (lastSentRef.current) sendPosition(lastSentRef.current);
      };
      socket.onclose = () => {
        setConnectionState("closed");
        if (cancelled) return;
        retryTimer = setTimeout(connect, retryDelay);
        retryDelay = Math.min(retryDelay * 2, RECONNECT_MAX_MS);
      };
      socket.onerror = () => socket.close();
    }

    connect();
    return () => {
      cancelled = true;
      if (retryTimer) clearTimeout(retryTimer);
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [driver, sendPosition]);

  // Position push loop — only runs once the socket is actually open.
  useEffect(() => {
    if (!driver || connectionState !== "open" || !navigator.geolocation) return;

    function pushPosition() {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGeoError(null);
          sendPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        },
        () => setGeoError(t("geoError")),
        { enableHighAccuracy: true, timeout: 9000 },
      );
    }

    pushPosition();
    const timer = setInterval(pushPosition, POSITION_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [driver, connectionState, sendPosition, t]);

  function handleStatusChange(next: (typeof STATUS_OPTIONS)[number]) {
    setStatus(next);
    if (lastSent) sendPosition(lastSent, next);
  }

  function handleLogout() {
    socketRef.current?.close();
    clearDriverSession();
    router.replace("/kierowca/logowanie");
  }

  if (!driver) return null;

  return (
    <div className="mx-auto flex max-w-[480px] flex-col gap-6">
      <div>
        <h1 className="font-heading text-2xl font-semibold">{t("greeting", { name: driver.name })}</h1>
        <p className="mt-1 text-[13.5px] text-muted">
          {driver.vehicle_name
            ? `${driver.vehicle_name}${driver.vehicle_plate ? ` · ${driver.vehicle_plate}` : ""}`
            : t("noVehicle")}
        </p>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
          {t("statusLabel")}
        </label>
        <select
          value={status}
          onChange={(e) => handleStatusChange(e.target.value as (typeof STATUS_OPTIONS)[number])}
          className="rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
        >
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {t(`status.${s}`)}
            </option>
          ))}
        </select>
      </div>

      <div className="rounded-[10px] border border-line bg-panel-2 px-4 py-3.5">
        <div className="flex items-center gap-2">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              connectionState === "open" ? "bg-green" : connectionState === "connecting" ? "bg-amber" : "bg-red"
            }`}
          />
          <span className="text-[13.5px] font-semibold">
            {connectionState === "open"
              ? t("connected")
              : connectionState === "connecting"
                ? t("connecting")
                : t("disconnected")}
          </span>
        </div>
        {lastSent && (
          <div className="mt-1.5 text-[12px] text-muted">
            {t("lastPosition", { lat: lastSent.lat.toFixed(5), lng: lastSent.lng.toFixed(5) })}
          </div>
        )}
        {geoError && <div className="mt-1.5 text-[12px] text-red">{geoError}</div>}
      </div>

      <button
        type="button"
        onClick={handleLogout}
        className="text-left text-[13px] font-semibold text-muted underline transition-colors hover:text-text"
      >
        {t("logout")}
      </button>
    </div>
  );
}
