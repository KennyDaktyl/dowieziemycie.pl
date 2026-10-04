import { timingSafeEqual } from "node:crypto";

import { revalidateTag } from "next/cache";
import { NextResponse, type NextRequest } from "next/server";

/** Called by the Django backend (apps/content/revalidation.py) after a
 * content change: expires the cached backend responses with these tags, so
 * every page that used them re-renders on its next visit. Guarded by the
 * shared REVALIDATE_SECRET — without it anyone could flush the cache. */

const TAG_RE = /^[a-z0-9-]{1,64}$/;

function authorized(request: NextRequest): boolean {
  const secret = process.env.REVALIDATE_SECRET;
  if (!secret) return false;
  const given = Buffer.from(request.headers.get("authorization") ?? "");
  const expected = Buffer.from(`Bearer ${secret}`);
  return given.length === expected.length && timingSafeEqual(given, expected);
}

export async function POST(request: NextRequest) {
  if (!authorized(request)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const body = (await request.json().catch(() => null)) as { tags?: unknown } | null;
  const tags = Array.isArray(body?.tags) ? body.tags.filter((tag): tag is string => typeof tag === "string") : [];
  if (tags.length === 0 || !tags.every((tag) => TAG_RE.test(tag))) {
    return NextResponse.json({ error: "tags must be a non-empty list of cache tags" }, { status: 400 });
  }

  // `{ expire: 0 }`, not the stale-while-revalidate "max" profile: an
  // external caller expects the very next visit to show the new content.
  for (const tag of tags) revalidateTag(tag, { expire: 0 });
  return NextResponse.json({ revalidated: tags });
}
