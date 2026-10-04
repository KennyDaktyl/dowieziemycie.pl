import { NextResponse } from "next/server";

import { getSession } from "@/lib/auth";

/** Whether the visitor is logged in — read by the header in the browser
 * (useLoggedIn), so the header itself never touches cookies. A cookie read
 * in a component shared by every page made every page dynamic: rendered
 * per request, never served from Next's full-page cache. */
export async function GET() {
  const { customer } = await getSession();
  return NextResponse.json({ loggedIn: Boolean(customer) }, { headers: { "Cache-Control": "private, no-store" } });
}
