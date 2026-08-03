import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { apiFetch } from "./api";
import {
  clearSession,
  getAccessToken,
  getDriverProfile,
  saveDriverProfile,
  saveSession,
  type DriverProfile,
} from "./session";

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
