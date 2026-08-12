"use client";

import { useEffect, useState } from "react";

// Keeps "user@domain" out of the server-rendered HTML (and therefore out of
// reach of the simple regex/text scrapers that most spam-address harvesters
// still are) — assembled into a real mailto link only once this runs in an
// actual browser. Search-engine crawlers get their own copy of the address
// through organization-jsonld.tsx, so hiding it here doesn't cost any SEO.
export function ObfuscatedEmail({ user, domain, className }: { user: string; domain: string; className?: string }) {
  const [email, setEmail] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setEmail(`${user}@${domain}`), 0);
    return () => clearTimeout(timer);
  }, [user, domain]);

  if (!email) {
    return (
      <span className={className}>
        {user} (at) {domain}
      </span>
    );
  }

  return (
    <a href={`mailto:${email}`} className={className}>
      {email}
    </a>
  );
}
