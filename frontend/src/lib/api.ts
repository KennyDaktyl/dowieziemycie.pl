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

export async function apiFetch<T>(
  path: string,
  init?: RequestInit & { next?: { revalidate?: number } },
): Promise<T> {
  const res = await fetch(`${apiBaseUrl()}${path}`, init);
  if (!res.ok) {
    throw new Error(`API ${path} responded with ${res.status}`);
  }
  return res.json() as Promise<T>;
}
