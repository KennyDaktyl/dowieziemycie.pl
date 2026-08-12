"use client";

import { forwardRef, useEffect, useRef, useState } from "react";

import { searchAddress, type AddressSuggestion } from "@/lib/geocode";

export const AddressSearchField = forwardRef<HTMLInputElement, {
  label: string;
  value: string;
  onTextChange: (text: string) => void;
  onSelect: (suggestion: AddressSuggestion) => void;
  onClear?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
  placeholder?: string;
  required?: boolean;
  error?: boolean;
  valid?: boolean;
}>(function AddressSearchField(
  { label, value, onTextChange, onSelect, onClear, onFocus, onBlur, placeholder, required, error, valid },
  inputRef,
) {
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const timer = setTimeout(async () => {
      const results = await searchAddress(value);
      setSuggestions(results);
    }, 400);
    return () => clearTimeout(timer);
  }, [value, open]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative flex flex-col gap-1.5">
      <label className="font-label text-[11.5px] font-semibold tracking-[0.08em] text-muted uppercase">
        {label}
        {required && <span className="text-red"> *</span>}
      </label>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value}
          placeholder={placeholder}
          onFocus={() => {
            setOpen(true);
            onFocus?.();
          }}
          onBlur={onBlur}
          onChange={(e) => {
            onTextChange(e.target.value);
            setOpen(true);
          }}
          className={`w-full rounded-lg border bg-panel-2 px-3 py-[11px] pr-9 text-[14.5px] text-text outline-none focus:border-amber ${
            error ? "border-red" : valid ? "border-green" : "border-line"
          }`}
        />
        {valid && !error && (
          <span aria-hidden className="absolute top-1/2 right-9 -translate-y-1/2 text-[13px] text-green">
            ✓
          </span>
        )}
        {value && (
          <button
            type="button"
            aria-label="Wyczyść"
            onClick={() => {
              onTextChange("");
              onClear?.();
              setSuggestions([]);
              setOpen(false);
            }}
            className="absolute top-1/2 right-2.5 -translate-y-1/2 text-muted transition-colors hover:text-text"
          >
            ✕
          </button>
        )}
      </div>
      {open && suggestions.length > 0 && (
        <ul className="absolute top-full z-20 mt-1 w-full overflow-hidden rounded-lg border border-line bg-panel-2 shadow-lg">
          {suggestions.map((s) => (
            <li key={`${s.lat},${s.lng}`}>
              <button
                type="button"
                onClick={() => {
                  onSelect(s);
                  setOpen(false);
                }}
                className="block w-full px-3 py-2 text-left text-[13px] text-text hover:bg-panel"
              >
                {s.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
});
