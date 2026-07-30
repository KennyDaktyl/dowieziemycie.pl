import { NextRequest, NextResponse } from "next/server";

import { apiBaseUrl, withSiteHeader } from "@/lib/api";
import { ACCESS_COOKIE, REFRESH_COOKIE, cookieOptions } from "@/lib/auth";

const ACCESS_MAX_AGE = 60 * 60 * 24 * 14; // 14 days, mirrors backend SIMPLE_JWT.ACCESS_TOKEN_LIFETIME
const REFRESH_MAX_AGE = 60 * 60 * 24 * 30; // 30 days

export async function POST(request: NextRequest) {
  const body = await request.json();
  const res = await fetch(`${apiBaseUrl()}/api/auth/verify-otp/`, {
    method: "POST",
    headers: withSiteHeader({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }

  if (data.role === "driver") {
    // Drivers need the raw token client-side (sessionStorage) — their
    // WebSocket connection has to attach it directly, which an httpOnly
    // cookie can't do. Handled entirely by the client after this responds.
    return NextResponse.json({ role: "driver", access: data.access, refresh: data.refresh, driver: data.driver });
  }

  const response = NextResponse.json({ role: "customer", customer: data.customer });
  response.cookies.set(ACCESS_COOKIE, data.access, { ...cookieOptions, maxAge: ACCESS_MAX_AGE });
  response.cookies.set(REFRESH_COOKIE, data.refresh, { ...cookieOptions, maxAge: REFRESH_MAX_AGE });
  return response;
}
