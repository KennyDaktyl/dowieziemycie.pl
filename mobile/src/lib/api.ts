export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "https://api.dowieziemycie.pl";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export const SESSION_EXPIRED_MESSAGE = "Sesja wygasła. Zaloguj się ponownie.";

export interface AuthHandlers {
  /** A call with `failedToken` got a 401 — return a working token (renewed
   * or already renewed by someone else), or null if the session is over.
   * Throws when it can't be told (offline) — the session is kept then. */
  renew: (failedToken: string) => Promise<string | null>;
  /** The session is really over: sign the driver out and show the login. */
  onExpired: () => void;
}

let authHandlers: AuthHandlers | null = null;

/** Registered once by AuthProvider, so every apiFetch in the app gets the
 * same recovery from an expired token without each screen handling it. */
export function setAuthHandlers(handlers: AuthHandlers | null) {
  authHandlers = handlers;
}

async function request(path: string, token: string | null, init?: RequestInit): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
}

export async function apiFetch<T>(path: string, token: string | null, init?: RequestInit): Promise<T> {
  let res = await request(path, token, init);

  // 401 on an authenticated call = expired/invalid token (they last 14 days
  // and used to be silently kept forever, so the app looked logged in while
  // every request failed). Renew once and retry; if the session is truly
  // over, sign out and ask for a new login.
  if (res.status === 401 && token && authHandlers) {
    const fresh = await authHandlers.renew(token);
    if (!fresh) {
      authHandlers.onExpired();
      throw new ApiError(401, SESSION_EXPIRED_MESSAGE);
    }
    res = await request(path, fresh, init);
    if (res.status === 401) {
      authHandlers.onExpired();
      throw new ApiError(401, SESSION_EXPIRED_MESSAGE);
    }
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new ApiError(res.status, data?.detail ?? "Wystąpił błąd. Spróbuj ponownie.");
  }
  return data as T;
}
