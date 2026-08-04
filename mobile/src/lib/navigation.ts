import { Alert, Linking } from "react-native";

/** Opens the phone's default navigation app in turn-by-turn mode. Google
 * Maps' Android intent scheme first — that's what's actually installed on
 * the driver's phone — falling back to a plain web maps URL (works
 * everywhere, including iOS) if that app isn't available. */
export function openNavigation(lat: number, lng: number) {
  const fallback = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
  Linking.openURL(`google.navigation:q=${lat},${lng}`).catch(() => {
    Linking.openURL(fallback).catch(() => {
      Alert.alert("Nie udało się otworzyć nawigacji.");
    });
  });
}
