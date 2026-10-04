"use client";

import { Link } from "@/i18n/navigation";
import { useLoggedIn } from "@/lib/use-logged-in";

import { CustomerMenu } from "./customer-menu";

/** Desktop header's account slot: the "my trips" login link by default, the
 * customer menu once the browser confirms a session (see useLoggedIn). */
export function HeaderAccount({ myTripsLabel, logoutLabel }: { myTripsLabel: string; logoutLabel: string }) {
  const loggedIn = useLoggedIn();

  if (loggedIn) return <CustomerMenu myTripsLabel={myTripsLabel} logoutLabel={logoutLabel} />;

  return (
    <Link
      href="/logowanie"
      className="flex shrink-0 items-center gap-1.5 text-[14.5px] font-semibold whitespace-nowrap text-muted transition-colors hover:text-text"
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" className="shrink-0">
        <circle cx="12" cy="8" r="3.5" stroke="currentColor" strokeWidth="1.8" />
        <path d="M4.5 20c1.4-4 4.4-6 7.5-6s6.1 2 7.5 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
      {myTripsLabel}
    </Link>
  );
}
