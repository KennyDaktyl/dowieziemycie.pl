/** sessionStorage-backed driver session — survives a refresh but not closing
 * the tab. Only ever called from client components/event handlers. */

const ACCESS_KEY = "driver_access_token";
const REFRESH_KEY = "driver_refresh_token";
const PROFILE_KEY = "driver_profile";

export interface DriverProfile {
  id: number;
  name: string;
  status: "OFFLINE" | "DOSTEPNY" | "JADACY_PO_KLIENTA" | "W_KURSIE" | "WRACA_DO_BAZY";
  vehicle_name: string | null;
  vehicle_plate: string | null;
}

export function saveDriverSession(access: string, refresh: string, driver: DriverProfile) {
  sessionStorage.setItem(ACCESS_KEY, access);
  sessionStorage.setItem(REFRESH_KEY, refresh);
  sessionStorage.setItem(PROFILE_KEY, JSON.stringify(driver));
}

export function getDriverAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_KEY);
}

export function getDriverProfile(): DriverProfile | null {
  const raw = sessionStorage.getItem(PROFILE_KEY);
  return raw ? (JSON.parse(raw) as DriverProfile) : null;
}

export function clearDriverSession() {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
  sessionStorage.removeItem(PROFILE_KEY);
}
