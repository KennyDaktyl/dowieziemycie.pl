import { getLocale, getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { getSession } from "@/lib/auth";

import { LocaleSwitcher } from "./locale-switcher";
import { LogoutButton } from "./logout-button";
import { MobileNav } from "./mobile-nav";

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
    <>
      {/* position: fixed (not sticky) — always pinned to the viewport top,
          never scrolls with content. The spacer below reserves the same
          height in normal flow so page content doesn't start underneath it. */}
      <header className="fixed inset-x-0 top-0 z-50 border-b border-line bg-bg/82 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1360px] items-center justify-between gap-2 px-4 py-4 sm:gap-4 sm:px-6">
          <Link href="/" className="min-w-0">
            <div className="font-heading flex items-center gap-2 text-[17px] font-bold tracking-tight sm:text-[19px]">
              <span className="h-[9px] w-[9px] shrink-0 rounded-full bg-amber shadow-[0_0_12px_2px_var(--color-amber)]" />
              <span className="truncate">
                dowieziemycie<span className="text-amber">.pl</span>
              </span>
            </div>
            <div className="font-label ml-[17px] -mt-0.5 truncate text-[10.5px] tracking-[0.08em] text-muted sm:text-[11.5px]">
              {t("subtitle")}
            </div>
          </Link>

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

          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <span className="font-label hidden rounded-full border border-line px-2.5 py-1 text-[11px] font-semibold tracking-wide text-muted xl:inline">
              🇬🇧 {t("speaksEnglish")}
            </span>
            <div className="hidden xl:block">
              <LocaleSwitcher />
            </div>
            <Link
              href={customer ? "/panel" : "/logowanie"}
              className="hidden text-[14.5px] font-semibold text-muted transition-colors hover:text-text xl:inline"
            >
              {customer ? t("myTrips") : t("login")}
            </Link>
            {customer && (
              <LogoutButton
                label={t("logout")}
                className="hidden text-[13px] font-medium text-muted underline transition-colors hover:text-text xl:inline"
              />
            )}
            <Link
              href="/sledz"
              className="hidden rounded-md border border-amber px-[14px] py-[9px] text-sm font-semibold whitespace-nowrap text-amber transition-colors hover:bg-amber/10 sm:inline-block"
            >
              {tNav("trackByCode")}
            </Link>
            <a
              href="tel:+48506029980"
              className="rounded-md bg-amber px-[14px] py-[9px] text-sm font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)] sm:px-[18px]"
            >
              {t("call")}
            </a>
            <MobileNav
              navLinks={navLinks}
              loginHref={customer ? "/panel" : "/logowanie"}
              loginLabel={customer ? t("myTrips") : t("login")}
              trackByCodeLabel={tNav("trackByCode")}
              speaksEnglishLabel={t("speaksEnglish")}
              isLoggedIn={Boolean(customer)}
              logoutLabel={t("logout")}
            />
          </div>
        </div>
      </header>
      <div aria-hidden className="h-[73px] sm:h-[81px]" />
    </>
  );
}
