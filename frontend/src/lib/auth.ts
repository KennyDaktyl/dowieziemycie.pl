import "server-only";

import { cookies } from "next/headers";

import { apiBaseUrl } from "./api";
import type { Customer } from "./types";

export const ACCESS_COOKIE = "dwm_access";
export const REFRESH_COOKIE = "dwm_refresh";

export const cookieOptions = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production",
  path: "/",
};

/** Server-side session lookup — used by layouts/pages to render auth state. */
export async function getSession(): Promise<{ customer: Customer | null; accessToken: string | null }> {
  const jar = await cookies();
  const accessToken = jar.get(ACCESS_COOKIE)?.value ?? null;
  if (!accessToken) {
    return { customer: null, accessToken: null };
  }

  const res = await fetch(`${apiBaseUrl()}/api/auth/me/`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!res.ok) {
    return { customer: null, accessToken: null };
  }
  return { customer: (await res.json()) as Customer, accessToken };
}
