import { NextRequest, NextResponse } from "next/server";

import { apiBaseUrl } from "@/lib/api";
import { ACCESS_COOKIE, REFRESH_COOKIE, cookieOptions } from "@/lib/auth";

const ACCESS_MAX_AGE = 60 * 60 * 24 * 14; // 14 days, mirrors backend SIMPLE_JWT.ACCESS_TOKEN_LIFETIME
const REFRESH_MAX_AGE = 60 * 60 * 24 * 30; // 30 days

export async function POST(request: NextRequest) {
  const body = await request.json();
  const res = await fetch(`${apiBaseUrl()}/api/auth/verify-otp/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) {
    return NextResponse.json(data, { status: res.status });
  }

  const response = NextResponse.json({ customer: data.customer });
  response.cookies.set(ACCESS_COOKIE, data.access, { ...cookieOptions, maxAge: ACCESS_MAX_AGE });
  response.cookies.set(REFRESH_COOKIE, data.refresh, { ...cookieOptions, maxAge: REFRESH_MAX_AGE });
  return response;
}
