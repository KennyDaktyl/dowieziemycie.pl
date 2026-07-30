"use client";

import { COUNTRIES, DEFAULT_COUNTRY, type Country } from "@/lib/countries";

/** Country-code select (flag + dial code, Poland default) + local-number
 * input, composed into a single E.164-ish string via onChange. */
export function PhoneInput({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (phone: string) => void;
  placeholder?: string;
}) {
  const country = COUNTRIES.find((c) => value.startsWith(c.dial)) ?? DEFAULT_COUNTRY;
  const localNumber = value.startsWith(country.dial) ? value.slice(country.dial.length) : value;

  function handleCountryChange(nextDial: string) {
    onChange(`${nextDial}${localNumber}`);
  }

  function handleNumberChange(next: string) {
    const digitsOnly = next.replace(/[^0-9]/g, "");
    onChange(`${country.dial}${digitsOnly}`);
  }

  return (
    <div className="flex gap-2">
      <select
        value={country.dial}
        onChange={(e) => handleCountryChange(e.target.value)}
        aria-label="Kod kraju"
        className="w-[104px] shrink-0 rounded-lg border border-line bg-panel-2 px-2 text-[14.5px] text-text outline-none focus:border-amber"
      >
        {COUNTRIES.map((c: Country) => (
          <option key={c.code} value={c.dial}>
            {c.flag} {c.dial}
          </option>
        ))}
      </select>
      <input
        type="tel"
        inputMode="tel"
        value={localNumber}
        onChange={(e) => handleNumberChange(e.target.value)}
        placeholder={placeholder}
        className="min-w-0 flex-1 rounded-lg border border-line bg-panel-2 px-3 py-[11px] text-[14.5px] text-text outline-none focus:border-amber"
      />
    </div>
  );
}
