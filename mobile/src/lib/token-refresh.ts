import { API_BASE_URL } from "./api";
import { getCredentials, getRefreshToken, saveTokens, type DriverProfile, type SavedCredentials } from "./session";

export interface RenewedSession {
  access: string;
  refresh: string;
  /** Only present after a silent re-login (the refresh endpoint doesn't return it). */
  driver?: DriverProfile;
}

async function post(path: string, body: unknown): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

/** Gets the driver a working access token again, trying in order:
 *  1. the refresh token (valid 30 days, rotates on every use),
 *  2. the remembered login + password (a silent re-login).
 * Returns null only when the server actually REFUSED both — i.e. the
 * session is really over and the driver has to log in by hand.
 * Throws (network error, 5xx) when the answer is unknown: being offline or
 * the server having a bad minute must never log a driver out. Uses fetch
 * directly, not apiFetch, so a 401 here can't trigger another refresh. */
export async function renewSession(
  refreshToken: string | null,
  credentials: SavedCredentials | null,
): Promise<RenewedSession | null> {
  if (refreshToken) {
    const res = await post("/api/fleet/driver/token/refresh/", { refresh: refreshToken });
    if (res.ok) {
      const data = (await res.json()) as { access: string; refresh?: string };
      return { access: data.access, refresh: data.refresh ?? refreshToken };
    }
    if (res.status >= 500) throw new Error(`Serwer odpowiedział ${res.status}`);
  }

  if (credentials) {
    const res = await post("/api/fleet/driver/login/", credentials);
    if (res.ok) {
      const data = (await res.json()) as { access: string; refresh: string; driver: DriverProfile };
      return { access: data.access, refresh: data.refresh, driver: data.driver };
    }
    if (res.status >= 500) throw new Error(`Serwer odpowiedział ${res.status}`);
  }

  return null;
}

/** Same thing for code that runs with no React around it (the background
 * GPS task): renews from what is stored on the device and saves the new
 * tokens back. */
export async function renewStoredSession(): Promise<string | null> {
  const [refresh, credentials] = await Promise.all([getRefreshToken(), getCredentials()]);
  const renewed = await renewSession(refresh, credentials);
  if (!renewed) return null;
  await saveTokens(renewed.access, renewed.refresh);
  return renewed.access;
}
