import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { apiBaseUrl, withSiteHeader } from "@/lib/api";
import { ACCESS_COOKIE } from "@/lib/auth";

export async function POST(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const accessToken = (await cookies()).get(ACCESS_COOKIE)?.value;
  if (!accessToken) {
    return NextResponse.json({ detail: "Zaloguj się, aby anulować rezerwację." }, { status: 401 });
  }

  const res = await fetch(`${apiBaseUrl()}/api/bookings/${id}/cancel/`, {
    method: "POST",
    headers: withSiteHeader({ Authorization: `Bearer ${accessToken}` }),
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
