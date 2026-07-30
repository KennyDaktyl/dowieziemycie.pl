import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

import { apiBaseUrl, withSiteHeader } from "@/lib/api";
import { ACCESS_COOKIE } from "@/lib/auth";

export async function POST(request: NextRequest) {
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) {
    return NextResponse.json({ detail: "Zaloguj się, aby zarezerwować kurs." }, { status: 401 });
  }

  const body = await request.json();
  const res = await fetch(`${apiBaseUrl()}/api/bookings/`, {
    method: "POST",
    headers: withSiteHeader({
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    }),
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
