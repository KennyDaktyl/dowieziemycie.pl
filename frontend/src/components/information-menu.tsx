"use client";

import { useEffect, useRef, useState } from "react";

import { Link } from "@/i18n/navigation";

type InformationMenuItem = {
  href: string;
  label: string;
};

export function InformationMenu({ label, items }: { label: string; items: InformationMenuItem[] }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;

    function handlePointerDown(event: PointerEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  return (
    <div
      ref={containerRef}
      className="relative"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
    >
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-1.5 rounded-md px-1 py-2 text-[14.5px] text-muted transition-colors hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber/70"
      >
        {label}
        <svg width="10" height="10" viewBox="0 0 10 10" fill="none" className={`transition-transform ${open ? "rotate-180" : ""}`}>
          <path d="M2 3.5 5 6.5 8 3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
        </svg>
      </button>

      <div
        className={`absolute top-full left-0 z-50 w-56 pt-2 transition-all duration-200 ${
          open ? "translate-y-0 opacity-100" : "-translate-y-1 pointer-events-none opacity-0"
        }`}
      >
        <div role="menu" className="rounded-[12px] border border-line bg-panel p-2">
          {items.map((item) =>
            item.href.includes("#") ? (
              <a
                key={item.href}
                href={item.href}
                role="menuitem"
                onClick={() => setOpen(false)}
                className="block rounded-[8px] px-3 py-2.5 text-[14px] text-muted transition-colors hover:bg-panel-2 hover:text-text focus:bg-panel-2 focus:text-text focus:outline-none"
              >
                {item.label}
              </a>
            ) : (
              <Link
                key={item.href}
                href={item.href}
                role="menuitem"
                onClick={() => setOpen(false)}
                className="block rounded-[8px] px-3 py-2.5 text-[14px] text-muted transition-colors hover:bg-panel-2 hover:text-text focus:bg-panel-2 focus:text-text focus:outline-none"
              >
                {item.label}
              </Link>
            ),
          )}
        </div>
      </div>
    </div>
  );
}
