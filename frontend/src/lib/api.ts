/** Server-side base URL for calling the Django backend (server components, route handlers). */
export function apiBaseUrl(): string {
  return process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

/** Client-side base URL — used by browser code for public GET endpoints (no cookies needed). */
export function publicApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
}

/** Client-side WebSocket base URL — live driver tracking (apps.tracking). */
export function wsBaseUrl(): string {
  return process.env.NEXT_PUBLIC_WS_BASE_URL ?? "ws://localhost:8000";
}

/** Which brand this frontend is — the backend reads this via the X-Site
 * header (config.middleware.SiteMiddleware) to serve dowieziemycie- vs
 * transfer247-scoped content/bookings from the one shared backend. */
export const SITE_CODE = "dowieziemycie";

/** Merge the X-Site header into a fetch's headers — use for every call to
 * the Django backend, including raw `fetch()` calls that don't go through
 * apiFetch (route handlers, client components). */
export function withSiteHeader(headers?: HeadersInit): HeadersInit {
  return { "X-Site": SITE_CODE, ...(headers ?? {}) };
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { next?: { revalidate?: number } },
): Promise<T> {
  const res = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers: withSiteHeader(init?.headers),
  });
  if (!res.ok) {
    throw new Error(`API ${path} responded with ${res.status}`);
  }
  return res.json() as Promise<T>;
}
