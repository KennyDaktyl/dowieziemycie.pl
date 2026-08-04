import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { apiFetch } from "./api";
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

  useEffect(() => {
    (async () => {
      const [token, profile] = await Promise.all([getAccessToken(), getDriverProfile()]);
      setAccessToken(token);
      setDriver(profile);
      setLoading(false);
    })();
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
    setAccessToken(data.access);
    setDriver(data.driver);
  }

  async function logout() {
    await clearSession();
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
