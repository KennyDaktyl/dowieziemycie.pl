import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { AppState, type AppStateStatus } from "react-native";

import { apiFetch, ApiError, setAuthHandlers } from "./api";
import { requestLocationPermissions, startBackgroundTracking } from "./location-task";
import {
  clearCredentials,
  clearSession,
  getAccessToken,
  getCredentials,
  getDriverProfile,
  getRefreshToken,
  saveCredentials,
  saveDriverProfile,
  saveSession,
  saveTokens,
  type DriverProfile,
} from "./session";
import { renewSession } from "./token-refresh";

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
  /** True after the session ended on its own (expired and could not be
   * renewed) — the login screen explains why the driver is looking at it. */
  sessionExpired: boolean;
  dismissSessionExpired: () => void;
  login: (username: string, password: string, rememberMe: boolean) => Promise<void>;
  logout: () => Promise<void>;
  updateStatus: (status: DriverProfile["status"]) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [driver, setDriver] = useState<DriverProfile | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);
  const tokenRef = useRef<string | null>(null);
  // The refresh token and whether this session lives in SecureStore ("remember
  // me") — without it the session (and its refresh token) exists in memory only.
  const refreshRef = useRef<string | null>(null);
  const persistedRef = useRef(false);
  const renewingRef = useRef<Promise<string | null> | null>(null);

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
      // apiFetch already renewed the token (or signed the driver out, if the
      // session was really over) before failing — nothing more to do here for
      // a background reconciliation. Offline errors are equally harmless.
      if (!(err instanceof ApiError)) return;
    }
  }

  /** A call got a 401. Returns a working token: someone already renewed it,
   * or it is renewed here (refresh token first, then a silent re-login with
   * the remembered login and password). Null = the session is really over.
   * Throws when the network/server can't tell — the session is then kept. */
  function renewAccess(failedToken: string): Promise<string | null> {
    if (tokenRef.current && tokenRef.current !== failedToken) return Promise.resolve(tokenRef.current);
    if (renewingRef.current) return renewingRef.current;

    const attempt = (async () => {
      const renewed = await renewSession(refreshRef.current, await getCredentials());
      if (!renewed) return null;
      tokenRef.current = renewed.access;
      refreshRef.current = renewed.refresh;
      setAccessToken(renewed.access);
      if (renewed.driver) setDriver(renewed.driver);
      if (persistedRef.current) {
        await saveTokens(renewed.access, renewed.refresh);
        if (renewed.driver) await saveDriverProfile(renewed.driver);
      }
      return renewed.access;
    })().finally(() => {
      renewingRef.current = null;
    });
    renewingRef.current = attempt;
    return attempt;
  }

  /** The session ended for good (expired, could not be renewed): sign out and
   * let the login screen say why. Saved credentials stay for pre-filling. */
  async function endExpiredSession() {
    await clearSession();
    tokenRef.current = null;
    refreshRef.current = null;
    persistedRef.current = false;
    setAccessToken(null);
    setDriver(null);
    setSessionExpired(true);
  }

  useEffect(() => {
    setAuthHandlers({ renew: renewAccess, onExpired: endExpiredSession });
    return () => setAuthHandlers(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    (async () => {
      const [token, profile, refresh] = await Promise.all([getAccessToken(), getDriverProfile(), getRefreshToken()]);
      tokenRef.current = token;
      refreshRef.current = refresh;
      persistedRef.current = token != null;
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
    // only — nothing goes to SecureStore (and any earlier saved login is
    // forgotten), so a cold start asks to log in again instead of silently
    // staying signed in on a shared device.
    if (rememberMe) {
      await saveSession(data.access, data.refresh, data.driver);
      await saveCredentials(username, password);
    } else {
      await clearSession();
      await clearCredentials();
    }
    persistedRef.current = rememberMe;
    refreshRef.current = data.refresh;
    setSessionExpired(false);
    tokenRef.current = data.access;
    setAccessToken(data.access);
    setDriver(data.driver);
  }

  async function logout() {
    await clearSession();
    tokenRef.current = null;
    refreshRef.current = null;
    persistedRef.current = false;
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
    <AuthContext.Provider
      value={{
        driver,
        accessToken,
        loading,
        sessionExpired,
        dismissSessionExpired: () => setSessionExpired(false),
        login,
        logout,
        updateStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
