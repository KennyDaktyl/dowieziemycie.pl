import { NextRequest, NextResponse } from "next/server";

import { apiBaseUrl } from "@/lib/api";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const res = await fetch(`${apiBaseUrl()}/api/auth/request-otp/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
