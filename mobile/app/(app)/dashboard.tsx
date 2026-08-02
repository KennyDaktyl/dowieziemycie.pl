import * as Location from "expo-location";
import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import {
  isTrackingActive,
  requestLocationPermissions,
  round6,
  startBackgroundTracking,
  stopBackgroundTracking,
} from "@/lib/location-task";
import { registerForPushNotifications } from "@/lib/notifications";
import type { DriverStatus } from "@/lib/session";
import { colors } from "@/lib/theme";

// "W drodze do klienta" / "W kursie" are deliberately not manually
// selectable here — they're driven by accepting/starting a booking (see
// the Kursy/Harmonogram tabs), so this picker can't drift out of sync with
// whichever booking the driver is actually on.
const STATUS_OPTIONS: { value: DriverStatus; label: string }[] = [
  { value: "DOSTEPNY", label: "Aktywny (wolny)" },
  { value: "WRACA_DO_BAZY", label: "Wraca do bazy" },
  { value: "OFFLINE", label: "Poza służbą / przerwa" },
];

const BOOKING_DRIVEN_STATUSES: DriverStatus[] = ["JADACY_PO_KLIENTA", "W_KURSIE"];

export default function DashboardScreen() {
  const { driver, accessToken, updateStatus, logout } = useAuth();
  const [tracking, setTracking] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    isTrackingActive().then(setTracking);
    registerForPushNotifications().catch(() => {
      // Non-fatal — the driver just won't get push alerts for new bookings
      // until permissions are granted from device settings.
    });
  }, []);

  async function pushCurrentPosition(status: DriverStatus) {
    const position = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
    await apiFetch("/api/fleet/driver/position/", accessToken, {
      method: "POST",
      body: JSON.stringify({ lat: round6(position.coords.latitude), lng: round6(position.coords.longitude), status }),
    });
  }

  async function handleStatusChange(status: DriverStatus) {
    if (!driver || status === driver.status) return;
    setBusy(true);
    setError(null);
    try {
      if (status === "OFFLINE") {
        await stopBackgroundTracking();
        setTracking(false);
        // Still report the OFFLINE status itself with a last-known fix if we can.
        try {
          await pushCurrentPosition(status);
        } catch {
          // Best effort — going offline shouldn't be blocked by a GPS hiccup.
        }
      } else {
        await requestLocationPermissions();
        await pushCurrentPosition(status);
        await startBackgroundTracking();
        setTracking(true);
      }
      updateStatus(status);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Nie udało się zmienić statusu.");
    } finally {
      setBusy(false);
    }
  }

  if (!driver) return null;

  return (
    <SafeAreaView style={styles.screen} edges={["bottom"]}>
      <View style={styles.content}>
        <Text style={styles.greeting}>Cześć, {driver.name}</Text>
        <Text style={styles.vehicle}>
          {driver.vehicle_name ? `${driver.vehicle_name}${driver.vehicle_plate ? ` · ${driver.vehicle_plate}` : ""}` : "Brak przypisanego pojazdu"}
        </Text>

        <View style={styles.trackingCard}>
          <View style={[styles.trackingDot, { backgroundColor: tracking ? colors.green : colors.muted }]} />
          <Text style={styles.trackingText}>
            {tracking ? "Pozycja jest udostępniana" : "Pozycja nie jest udostępniana"}
          </Text>
        </View>

        {BOOKING_DRIVEN_STATUSES.includes(driver.status) && (
          <View style={styles.bookingNotice}>
            <Text style={styles.bookingNoticeText}>
              Masz aktywny kurs — status steruje się z zakładki „Harmonogram”, nie stąd.
            </Text>
          </View>
        )}

        <Text style={styles.label}>STATUS</Text>
        <View style={styles.statusList}>
          {STATUS_OPTIONS.map((option) => {
            const active = driver.status === option.value;
            return (
              <Pressable
                key={option.value}
                disabled={busy}
                onPress={() => handleStatusChange(option.value)}
                style={({ pressed }) => [
                  styles.statusOption,
                  active && styles.statusOptionActive,
                  pressed && { opacity: 0.85 },
                ]}
              >
                <Text style={[styles.statusOptionText, active && styles.statusOptionTextActive]}>
                  {option.label}
                </Text>
                {busy && active && <ActivityIndicator size="small" color={colors.amber} />}
              </Pressable>
            );
          })}
        </View>

        {error && <Text style={styles.error}>{error}</Text>}

        <Pressable onPress={logout} style={styles.logout}>
          <Text style={styles.logoutText}>Wyloguj się</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  content: { flex: 1, padding: 20 },
  greeting: { color: colors.text, fontSize: 22, fontWeight: "700" },
  vehicle: { color: colors.muted, fontSize: 13.5, marginTop: 4, marginBottom: 20 },
  trackingCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: colors.panel2,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.line,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 22,
  },
  trackingDot: { width: 9, height: 9, borderRadius: 5 },
  trackingText: { color: colors.text, fontSize: 13.5, fontWeight: "600" },
  bookingNotice: {
    backgroundColor: colors.panel2,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.amber,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 16,
  },
  bookingNoticeText: { color: colors.amber, fontSize: 13, fontWeight: "600" },
  label: { color: colors.muted, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 8 },
  statusList: { gap: 8 },
  statusOption: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.panel,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.line,
    paddingHorizontal: 14,
    paddingVertical: 13,
  },
  statusOptionActive: { borderColor: colors.amber, backgroundColor: colors.panel2 },
  statusOptionText: { color: colors.muted, fontSize: 14.5, fontWeight: "600" },
  statusOptionTextActive: { color: colors.text },
  error: { color: colors.red, fontSize: 13, marginTop: 16, textAlign: "center" },
  logout: { marginTop: "auto", alignItems: "center", paddingVertical: 12 },
  logoutText: { color: colors.muted, fontSize: 13, fontWeight: "600", textDecorationLine: "underline" },
});
