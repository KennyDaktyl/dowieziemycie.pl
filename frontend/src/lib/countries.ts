export interface Country {
  code: string;
  dial: string;
  flag: string;
  name: string;
  /** Expected national (local) mobile number digit count, for basic completeness validation. */
  minLength: number;
}

// Poland first (default) — the rest cover neighboring countries and the
// nationalities most likely to book an airport transfer.
export const COUNTRIES: Country[] = [
  { code: "PL", dial: "+48", flag: "🇵🇱", name: "Polska", minLength: 9 },
  { code: "GB", dial: "+44", flag: "🇬🇧", name: "Wielka Brytania", minLength: 10 },
  { code: "DE", dial: "+49", flag: "🇩🇪", name: "Niemcy", minLength: 10 },
  { code: "UA", dial: "+380", flag: "🇺🇦", name: "Ukraina", minLength: 9 },
  { code: "CZ", dial: "+420", flag: "🇨🇿", name: "Czechy", minLength: 9 },
  { code: "SK", dial: "+421", flag: "🇸🇰", name: "Słowacja", minLength: 9 },
  { code: "FR", dial: "+33", flag: "🇫🇷", name: "Francja", minLength: 9 },
  { code: "IT", dial: "+39", flag: "🇮🇹", name: "Włochy", minLength: 9 },
  { code: "ES", dial: "+34", flag: "🇪🇸", name: "Hiszpania", minLength: 9 },
  { code: "NL", dial: "+31", flag: "🇳🇱", name: "Holandia", minLength: 9 },
  { code: "IE", dial: "+353", flag: "🇮🇪", name: "Irlandia", minLength: 9 },
  { code: "US", dial: "+1", flag: "🇺🇸", name: "USA", minLength: 10 },
];

export const DEFAULT_COUNTRY = COUNTRIES[0];

export function findCountry(phone: string): Country {
  return COUNTRIES.find((c) => phone.startsWith(c.dial)) ?? DEFAULT_COUNTRY;
}

/** Local-number length is what actually matters — "+48" alone is 3 characters
 * that a flat phone.length check would otherwise count as real digits. */
export function isCompletePhoneNumber(phone: string): boolean {
  const country = findCountry(phone);
  const localDigits = phone.slice(country.dial.length).replace(/\D/g, "");
  return localDigits.length >= country.minLength;
}
