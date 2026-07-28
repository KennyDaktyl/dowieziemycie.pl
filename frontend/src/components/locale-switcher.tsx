"use client";

import { useLocale } from "next-intl";
import { useTransition } from "react";

import { usePathname, useRouter } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";

export function LocaleSwitcher() {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function switchTo(nextLocale: string) {
    startTransition(() => {
      router.replace(pathname, { locale: nextLocale });
    });
  }

  return (
    <div className="flex items-center gap-1 rounded-md border border-line p-0.5 text-xs font-semibold">
      {routing.locales.map((loc) => (
        <button
          key={loc}
          type="button"
          disabled={isPending}
          onClick={() => switchTo(loc)}
          className={`rounded px-2 py-1 uppercase transition-colors ${
            loc === locale ? "bg-amber text-[#1a1305]" : "text-muted hover:text-text"
          }`}
        >
          {loc}
        </button>
      ))}
    </div>
  );
}
