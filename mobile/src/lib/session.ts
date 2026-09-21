import * as SecureStore from "expo-secure-store";

const ACCESS_KEY = "driver_access_token";
const REFRESH_KEY = "driver_refresh_token";
const PROFILE_KEY = "driver_profile";
const CRED_USER_KEY = "driver_saved_username";
const CRED_PASS_KEY = "driver_saved_password";

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

export async function getRefreshToken(): Promise<string | null> {
  return SecureStore.getItemAsync(REFRESH_KEY);
}

/** Replaces just the tokens (after a refresh/silent re-login), leaving the
 * cached profile alone. */
export async function saveTokens(access: string, refresh: string) {
  await SecureStore.setItemAsync(ACCESS_KEY, access);
  await SecureStore.setItemAsync(REFRESH_KEY, refresh);
}

export interface SavedCredentials {
  username: string;
  password: string;
}

/** "Remember me": the login + password live in the OS-encrypted store
 * (Android Keystore via expo-secure-store), so an expired session can
 * sign back in by itself and the login form comes pre-filled. Deliberately
 * NOT cleared by clearSession()/logout — remembering them is the point. */
export async function saveCredentials(username: string, password: string) {
  await SecureStore.setItemAsync(CRED_USER_KEY, username);
  await SecureStore.setItemAsync(CRED_PASS_KEY, password);
}

export async function getCredentials(): Promise<SavedCredentials | null> {
  const [username, password] = await Promise.all([
    SecureStore.getItemAsync(CRED_USER_KEY),
    SecureStore.getItemAsync(CRED_PASS_KEY),
  ]);
  return username && password ? { username, password } : null;
}

export async function clearCredentials() {
  await SecureStore.deleteItemAsync(CRED_USER_KEY);
  await SecureStore.deleteItemAsync(CRED_PASS_KEY);
}
