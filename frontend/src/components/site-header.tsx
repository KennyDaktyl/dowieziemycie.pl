import { getLocale, getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { getSession } from "@/lib/auth";

import { CustomerMenu } from "./customer-menu";
import { InformationMenu } from "./information-menu";
import { LocaleSwitcher } from "./locale-switcher";
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
  const primaryLinks = [
    { href: `/${locale}#coverage`, label: tNav("coverage") },
    { href: `/${locale}#routes`, label: tNav("routes") },
  ];
  const informationLinks = [
    { href: `/${locale}#how-it-works`, label: tNav("howItWorks") },
    { href: "/na-zywo", label: tNav("tracking") },
    { href: "/cennik", label: tNav("pricing") },
    { href: "/blog", label: tNav("blog") },
    { href: "/regulamin", label: tNav("terms") },
  ];
  const mobileNavLinks = [
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
        <div className="mx-auto flex max-w-[1360px] items-center gap-3 px-4 py-4 sm:px-6">
          <Link href="/" className="min-w-[218px] shrink-0 xl:min-w-[238px]">
            <div className="font-heading flex items-center gap-2 text-[17px] font-bold tracking-tight sm:text-[19px]">
              <span className="h-[9px] w-[9px] shrink-0 rounded-full bg-amber shadow-[0_0_12px_2px_var(--color-amber)]" />
              <span className="whitespace-nowrap">
                dowieziemycie<span className="text-amber">.pl</span>
              </span>
            </div>
            <div className="font-label ml-[17px] -mt-0.5 whitespace-nowrap text-[10.5px] tracking-[0.08em] text-muted sm:text-[11.5px]">
              {t("subtitle")}
            </div>
          </Link>

          <nav className="hidden min-w-0 flex-1 items-center gap-5 text-[14.5px] whitespace-nowrap text-muted xl:flex">
            {primaryLinks.map((link) =>
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
            <InformationMenu label={tNav("information")} items={informationLinks} />
          </nav>

          <div className="ml-auto flex shrink-0 items-center gap-2 sm:gap-3">
            <div className="hidden xl:block">
              <LocaleSwitcher />
            </div>
            <div className="hidden xl:block">
              {customer ? (
                <CustomerMenu myTripsLabel={t("myTrips")} logoutLabel={t("logout")} />
              ) : (
                <Link
                  href="/logowanie"
                  className="flex shrink-0 items-center gap-1.5 text-[14.5px] font-semibold whitespace-nowrap text-muted transition-colors hover:text-text"
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" className="shrink-0">
                    <circle cx="12" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.8" />
                    <path d="M4.5 20c1.4-4 4.4-6 7.5-6s6.1 2 7.5 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                  </svg>
                  {t("myTrips")}
                </Link>
              )}
            </div>
            <Link
              href="/sledz"
              className="hidden rounded-md border border-amber px-[14px] py-[9px] text-sm font-semibold whitespace-nowrap text-amber transition-colors hover:bg-amber/10 sm:inline-block"
            >
              {tNav("trackByCode")}
            </Link>
            <a
              href="tel:+48506029980"
              className="hidden rounded-md bg-amber px-[18px] py-[9px] text-sm font-semibold whitespace-nowrap text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_4px_20px_rgba(245,166,35,0.35)] sm:inline-block"
            >
              {t("call")}
            </a>
            <MobileNav
              navLinks={mobileNavLinks}
              loginHref={customer ? "/moje-kursy" : "/logowanie"}
              loginLabel={customer ? t("myTrips") : t("login")}
              trackByCodeLabel={tNav("trackByCode")}
              bookNowLabel={tNav("bookNow")}
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
