export interface Country {
  code: string;
  dial: string;
  flag: string;
  name: string;
}

// Poland first (default) — the rest cover neighboring countries and the
// nationalities most likely to book an airport transfer.
export const COUNTRIES: Country[] = [
  { code: "PL", dial: "+48", flag: "🇵🇱", name: "Polska" },
  { code: "GB", dial: "+44", flag: "🇬🇧", name: "Wielka Brytania" },
  { code: "DE", dial: "+49", flag: "🇩🇪", name: "Niemcy" },
  { code: "UA", dial: "+380", flag: "🇺🇦", name: "Ukraina" },
  { code: "CZ", dial: "+420", flag: "🇨🇿", name: "Czechy" },
  { code: "SK", dial: "+421", flag: "🇸🇰", name: "Słowacja" },
  { code: "FR", dial: "+33", flag: "🇫🇷", name: "Francja" },
  { code: "IT", dial: "+39", flag: "🇮🇹", name: "Włochy" },
  { code: "ES", dial: "+34", flag: "🇪🇸", name: "Hiszpania" },
  { code: "NL", dial: "+31", flag: "🇳🇱", name: "Holandia" },
  { code: "IE", dial: "+353", flag: "🇮🇪", name: "Irlandia" },
  { code: "US", dial: "+1", flag: "🇺🇸", name: "USA" },
];

export const DEFAULT_COUNTRY = COUNTRIES[0];
