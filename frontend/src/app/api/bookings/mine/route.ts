import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { apiBaseUrl } from "@/lib/api";
import { ACCESS_COOKIE } from "@/lib/auth";

export async function GET() {
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) {
    return NextResponse.json([], { status: 200 });
  }

  const res = await fetch(`${apiBaseUrl()}/api/bookings/mine/`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
