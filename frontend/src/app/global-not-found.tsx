import type { Metadata } from "next";

// Bypasses app/[locale]/layout.tsx entirely (root layout uses a top-level
// dynamic segment, so it can't compose a global 404 — see next.config.ts),
// hence no next-intl context here: plain Polish copy, no next/font (keeps
// this page light per Next's own guidance for global-not-found.tsx).
import "./[locale]/globals.css";

export const metadata: Metadata = {
  title: "Nie znaleziono strony | dowieziemycie.pl",
};

export default function GlobalNotFound() {
  return (
    <html lang="pl">
      <body className="bg-bg text-text flex min-h-screen items-center justify-center">
        <div className="mx-auto max-w-[480px] px-4 text-center">
          <div className="text-amber text-[64px] font-bold">404</div>
          <h1 className="mt-2 text-[24px] font-semibold">Nie znaleziono strony</h1>
          <p className="text-muted mt-3 text-[15px]">
            Strona, której szukasz, nie istnieje albo została przeniesiona.
          </p>
          {/* eslint-disable-next-line @next/next/no-html-link-for-pages -- this page bypasses [locale]/layout.tsx entirely, no next-intl Link context is available here */}
          <a
            href="/pl"
            className="bg-amber mt-8 inline-block rounded-md px-6 py-3 text-[14px] font-semibold text-[#1a1305]"
          >
            Strona główna
          </a>
        </div>
      </body>
    </html>
  );
}
