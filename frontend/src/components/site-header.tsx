import { getLocale, getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { getSession } from "@/lib/auth";

import { LocaleSwitcher } from "./locale-switcher";

export async function SiteHeader() {
  const [t, tNav, locale, { customer }] = await Promise.all([
    getTranslations("Header"),
    getTranslations("Nav"),
    getLocale(),
    getSession(),
  ]);

  // Anchor ids are language-neutral on purpose (same on /pl and /en) — prefixed
  // with the current locale's home path so nav works from any page, not just "/".
  const navLinks = [
    { href: `/${locale}#coverage`, label: tNav("coverage") },
    { href: `/${locale}#how-it-works`, label: tNav("howItWorks") },
    { href: `/${locale}#routes`, label: tNav("routes") },
    { href: "/na-zywo", label: tNav("tracking") },
    { href: "/blog", label: tNav("blog") },
    { href: "/cennik", label: tNav("pricing") },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-bg/82 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1360px] items-center justify-between gap-4 px-6 py-4">
        <div>
          <div className="font-heading flex items-center gap-2 text-[19px] font-bold tracking-tight">
            <span className="h-[9px] w-[9px] rounded-full bg-amber shadow-[0_0_12px_2px_var(--color-amber)]" />
            dowiezmy<span className="text-amber">cię</span>
          </div>
          <div className="font-label ml-[17px] -mt-0.5 text-[11.5px] tracking-[0.08em] text-muted">
            {t("subtitle")}
          </div>
        </div>

        <nav className="hidden shrink-0 gap-6 text-[14.5px] whitespace-nowrap text-muted xl:flex">
          {navLinks.map((link) =>
            link.href.includes("#") ? (
              <a key={link.href} href={link.href} className="transition-colors hover:text-text">
                {link.label}
              </a>
            ) : (
              <Link key={link.href} href={link.href} className="transition-colors hover:text-text">
                {link.label}
              </Link>
            ),
          )}
        </nav>

        <div className="flex items-center gap-3">
          <span className="font-label hidden rounded-full border border-line px-2.5 py-1 text-[11px] font-semibold tracking-wide text-muted sm:inline">
            🇬🇧 {t("speaksEnglish")}
          </span>
          <LocaleSwitcher />
          <Link
            href={customer ? "/panel" : "/logowanie"}
            className="hidden text-[14.5px] font-semibold text-muted transition-colors hover:text-text sm:inline"
          >
            {customer ? t("myTrips") : t("login")}
          </Link>
          <a
            href="tel:+48000000000"
            className="rounded-md bg-amber px-[18px] py-[9px] text-sm font-semibold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)]"
          >
            {t("call")}
          </a>
        </div>
      </div>
    </header>
  );
}
