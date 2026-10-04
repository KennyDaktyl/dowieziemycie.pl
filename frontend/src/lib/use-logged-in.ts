"use client";

import { useEffect, useState } from "react";

/** The visitor's login state, fetched after the page loads — null until it
 * is known, so the header shows the logged-out default meanwhile. See
 * /api/auth/session for why this isn't read server-side. */
export function useLoggedIn(): boolean | null {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/auth/session", { cache: "no-store" })
      .then((res) => (res.ok ? (res.json() as Promise<{ loggedIn: boolean }>) : { loggedIn: false }))
      .then((data) => {
        if (!cancelled) setLoggedIn(data.loggedIn);
      })
      .catch(() => {
        if (!cancelled) setLoggedIn(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return loggedIn;
}
