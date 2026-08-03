import * as SecureStore from "expo-secure-store";

const ACCESS_KEY = "driver_access_token";
const REFRESH_KEY = "driver_refresh_token";
const PROFILE_KEY = "driver_profile";

export type DriverStatus = "OFFLINE" | "DOSTEPNY" | "JADACY_PO_KLIENTA" | "W_KURSIE" | "WRACA_DO_BAZY";

export interface DriverProfile {
  id: number;
  name: string;
  status: DriverStatus;
  vehicle_name: string | null;
  vehicle_plate: string | null;
  is_dispatcher: boolean;
}

export async function saveSession(access: string, refresh: string, driver: DriverProfile) {
  await SecureStore.setItemAsync(ACCESS_KEY, access);
  await SecureStore.setItemAsync(REFRESH_KEY, refresh);
  await SecureStore.setItemAsync(PROFILE_KEY, JSON.stringify(driver));
}

export async function getAccessToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_KEY);
}

export async function getDriverProfile(): Promise<DriverProfile | null> {
  const raw = await SecureStore.getItemAsync(PROFILE_KEY);
  return raw ? (JSON.parse(raw) as DriverProfile) : null;
}

export async function saveDriverProfile(driver: DriverProfile) {
  await SecureStore.setItemAsync(PROFILE_KEY, JSON.stringify(driver));
}

export async function clearSession() {
  await SecureStore.deleteItemAsync(ACCESS_KEY);
  await SecureStore.deleteItemAsync(REFRESH_KEY);
  await SecureStore.deleteItemAsync(PROFILE_KEY);
}
