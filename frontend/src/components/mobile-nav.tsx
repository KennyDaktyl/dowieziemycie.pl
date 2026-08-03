"use client";

import { useEffect, useState } from "react";

import { Link } from "@/i18n/navigation";

import { LocaleSwitcher } from "./locale-switcher";
import { LogoutButton } from "./logout-button";

export function MobileNav({
  navLinks,
  loginHref,
  loginLabel,
  trackByCodeLabel,
  speaksEnglishLabel,
  isLoggedIn,
  logoutLabel,
}: {
  navLinks: { href: string; label: string }[];
  loginHref: string;
  loginLabel: string;
  trackByCodeLabel: string;
  speaksEnglishLabel: string;
  isLoggedIn: boolean;
  logoutLabel: string;
}) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <div className="xl:hidden">
      <button
        type="button"
        aria-label={open ? "Zamknij menu" : "Otwórz menu"}
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="flex h-9 w-9 shrink-0 flex-col items-center justify-center gap-[5px] rounded-md border border-line"
      >
        <span
          className={`h-[1.5px] w-[18px] bg-text transition-transform ${open ? "translate-y-[6.5px] rotate-45" : ""}`}
        />
        <span className={`h-[1.5px] w-[18px] bg-text transition-opacity ${open ? "opacity-0" : ""}`} />
        <span
          className={`h-[1.5px] w-[18px] bg-text transition-transform ${open ? "-translate-y-[6.5px] -rotate-45" : ""}`}
        />
      </button>

      {open && (
        <div className="absolute inset-x-0 top-full z-40 max-h-[80vh] overflow-y-auto border-t border-line bg-bg px-6 py-6 shadow-xl">
          <nav className="flex flex-col gap-1 text-[16px]">
            {navLinks.map((link) =>
              link.href.includes("#") ? (
                <a
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="rounded-md px-2 py-3 text-text transition-colors hover:bg-panel"
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="rounded-md px-2 py-3 text-text transition-colors hover:bg-panel"
                >
                  {link.label}
                </Link>
              ),
            )}
            <Link
              href={loginHref}
              onClick={() => setOpen(false)}
              className="rounded-md px-2 py-3 text-text transition-colors hover:bg-panel"
            >
              {loginLabel}
            </Link>
            {isLoggedIn && (
              <LogoutButton
                label={logoutLabel}
                className="rounded-md px-2 py-3 text-left text-muted transition-colors hover:bg-panel"
              />
            )}
            <Link
              href="/sledz"
              onClick={() => setOpen(false)}
              className="mt-2 rounded-md border border-amber px-2 py-3 text-center font-semibold text-amber transition-colors hover:bg-amber/10"
            >
              {trackByCodeLabel}
            </Link>
          </nav>

          <div className="mt-6 flex items-center gap-3 border-t border-line pt-6">
            <LocaleSwitcher />
            <span className="font-label rounded-full border border-line px-2.5 py-1 text-[11px] font-semibold tracking-wide text-muted">
              🇬🇧 {speaksEnglishLabel}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
