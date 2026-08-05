import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { AppState, type AppStateStatus } from "react-native";

import { apiFetch, ApiError } from "./api";
import { requestLocationPermissions, startBackgroundTracking } from "./location-task";
import {
  clearSession,
  getAccessToken,
  getDriverProfile,
  saveDriverProfile,
  saveSession,
  type DriverProfile,
} from "./session";

// Booking actions from Kursy/Szef/Harmonogram move the driver straight into
// one of these statuses without going through Dashboard's own "Aktywny"
// toggle (the only place background tracking used to get started) — so a
// driver could end up marked JADACY_PO_KLIENTA/W_KURSIE while their phone
// was never actually told to start sending GPS pings. Starting it here too
// closes that gap regardless of which tab triggered the status change.
const TRACKING_REQUIRED_STATUSES: DriverProfile["status"][] = ["JADACY_PO_KLIENTA", "W_KURSIE"];

interface AuthContextValue {
  driver: DriverProfile | null;
  accessToken: string | null;
  loading: boolean;
  login: (username: string, password: string, rememberMe: boolean) => Promise<void>;
  logout: () => Promise<void>;
  updateStatus: (status: DriverProfile["status"]) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [driver, setDriver] = useState<DriverProfile | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const tokenRef = useRef<string | null>(null);

  // The cached profile (SecureStore) is what renders instantly on cold
  // start, but it's only ever written at login or by a local optimistic
  // update (updateStatus below) — a status changed elsewhere (Django admin,
  // a dispatcher action) never reaches it on its own. This was a real bug:
  // a driver's status flipped in admin stayed stuck on their phone
  // indefinitely because nothing ever re-asked the backend. Reconciling
  // against /driver/me/ right after the cached profile loads, and again
  // whenever the app comes back to the foreground, closes that gap.
  async function refreshDriver() {
    if (!tokenRef.current) return;
    try {
      const fresh = await apiFetch<DriverProfile>("/api/fleet/driver/me/", tokenRef.current);
      setDriver(fresh);
      await saveDriverProfile(fresh);
    } catch (err) {
      // A stale/expired token here just means the next authenticated call
      // elsewhere in the app will surface the same 401 and route to login —
      // no need to duplicate that handling for a background reconciliation.
      if (!(err instanceof ApiError)) throw err;
    }
  }

  useEffect(() => {
    (async () => {
      const [token, profile] = await Promise.all([getAccessToken(), getDriverProfile()]);
      tokenRef.current = token;
      setAccessToken(token);
      setDriver(profile);
      setLoading(false);
      await refreshDriver();
    })();
  }, []);

  useEffect(() => {
    function onAppStateChange(next: AppStateStatus) {
      if (next === "active") refreshDriver();
    }
    const sub = AppState.addEventListener("change", onAppStateChange);
    return () => sub.remove();
  }, []);

  async function login(username: string, password: string, rememberMe: boolean) {
    const data = await apiFetch<{ access: string; refresh: string; driver: DriverProfile }>(
      "/api/fleet/driver/login/",
      null,
      { method: "POST", body: JSON.stringify({ username, password }) },
    );
    // Unchecking "remember me" keeps the session in memory for this app run
    // only — nothing goes to SecureStore, so a cold start asks to log in
    // again instead of silently staying signed in on a shared device.
    if (rememberMe) {
      await saveSession(data.access, data.refresh, data.driver);
    }
    tokenRef.current = data.access;
    setAccessToken(data.access);
    setDriver(data.driver);
  }

  async function logout() {
    await clearSession();
    tokenRef.current = null;
    setAccessToken(null);
    setDriver(null);
  }

  function updateStatus(status: DriverProfile["status"]) {
    setDriver((prev) => {
      if (!prev) return prev;
      const next = { ...prev, status };
      saveDriverProfile(next);
      return next;
    });

    if (TRACKING_REQUIRED_STATUSES.includes(status)) {
      requestLocationPermissions()
        .then(startBackgroundTracking)
        .catch(() => {
          // Best effort — if permissions were never granted, the driver
          // still sees "Pozycja nie jest udostępniana" on the Panel tab
          // and can grant them from there.
        });
    }
  }

  return (
    <AuthContext.Provider value={{ driver, accessToken, loading, login, logout, updateStatus }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
