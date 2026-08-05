import { Ionicons } from "@expo/vector-icons";
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
import { colors, statusTone, type StatusTone } from "@/lib/theme";

// "W drodze do klienta" / "W kursie" are shown for visibility but are never
// manually tappable — they're driven by "Jadę do klienta"/starting a
// booking (see the Harmonogram tab), so this picker can't drift out of
// sync with whichever booking the driver is actually on. While either is
// active, the other three go read-only too — you can't manually go
// OFFLINE mid-ride, you have to finish the booking first.
const STATUS_OPTIONS: {
  value: DriverStatus; label: string; manual: boolean; icon: keyof typeof Ionicons.glyphMap; tone: StatusTone;
}[] = [
  // "flash" rather than a checkmark-style icon — a checkmark here reads as
  // "this option is currently selected" (the actual active-row indicator,
  // rendered separately on the right of whichever row IS active), which
  // made this row look selected even while OFFLINE was the real status.
  { value: "DOSTEPNY", label: "Aktywny (wolny)", manual: true, icon: "flash", tone: "green" },
  { value: "JADACY_PO_KLIENTA", label: "W drodze do klienta", manual: false, icon: "car", tone: "amber" },
  { value: "W_KURSIE", label: "W trakcie kursu", manual: false, icon: "navigate", tone: "amber" },
  { value: "WRACA_DO_BAZY", label: "Wraca do bazy", manual: true, icon: "home", tone: "blue" },
  { value: "OFFLINE", label: "Poza służbą / przerwa", manual: true, icon: "moon", tone: "muted" },
];

const BOOKING_DRIVEN_STATUSES: DriverStatus[] = ["JADACY_PO_KLIENTA", "W_KURSIE"];

function statusOptionFor(status: DriverStatus) {
  return STATUS_OPTIONS.find((o) => o.value === status) ?? STATUS_OPTIONS[0];
}

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

  const isBookingDriven = BOOKING_DRIVEN_STATUSES.includes(driver.status);
  const current = statusOptionFor(driver.status);
  const currentTone = statusTone[current.tone];

  return (
    <SafeAreaView style={styles.screen} edges={["bottom"]}>
      <View style={styles.content}>
        <View style={styles.headerRow}>
          <View style={styles.flex1}>
            <Text style={styles.greeting}>Cześć, {driver.name}</Text>
            <Text style={styles.vehicle}>
              {driver.vehicle_name ? `${driver.vehicle_name}${driver.vehicle_plate ? ` · ${driver.vehicle_plate}` : ""}` : "Brak przypisanego pojazdu"}
            </Text>
          </View>
          {/* Persistent chip — the current status is always visible here,
              even after scrolling past the picker below. */}
          <View style={[styles.statusChip, { backgroundColor: currentTone.bg, borderColor: currentTone.fg }]}>
            <Ionicons name={current.icon} size={14} color={currentTone.fg} />
            <Text style={[styles.statusChipText, { color: currentTone.fg }]}>{current.label}</Text>
          </View>
        </View>

        <View style={styles.trackingCard}>
          <View style={[styles.trackingDot, { backgroundColor: tracking ? colors.green : colors.muted }]} />
          <Text style={styles.trackingText}>
            {tracking ? "Pozycja jest udostępniana" : "Pozycja nie jest udostępniana"}
          </Text>
        </View>

        {isBookingDriven && (
          <View style={styles.bookingNotice}>
            <Ionicons name="information-circle" size={16} color={colors.amber} />
            <Text style={styles.bookingNoticeText}>
              Masz aktywny kurs — zakończ go w zakładce „Harmonogram”, żeby znowu móc zmienić status ręcznie.
            </Text>
          </View>
        )}

        <Text style={styles.label}>STATUS</Text>
        <View style={styles.statusList}>
          {STATUS_OPTIONS.map((option) => {
            const active = driver.status === option.value;
            const disabled = busy || !option.manual || isBookingDriven;
            const tone = statusTone[option.tone];
            return (
              <Pressable
                key={option.value}
                disabled={disabled}
                onPress={() => handleStatusChange(option.value)}
                style={({ pressed }) => [
                  styles.statusOption,
                  active
                    ? { backgroundColor: tone.bg, borderColor: tone.fg }
                    : disabled && styles.statusOptionDisabled,
                  !disabled && pressed && { opacity: 0.85 },
                ]}
              >
                <View style={styles.statusOptionLeft}>
                  <Ionicons name={option.icon} size={19} color={active ? tone.fg : colors.muted} />
                  <Text style={[styles.statusOptionText, active && { color: tone.fg, fontWeight: "800" }]}>
                    {option.label}
                  </Text>
                </View>
                {busy && active ? (
                  <ActivityIndicator size="small" color={tone.fg} />
                ) : active ? (
                  <Ionicons name="checkmark-circle" size={20} color={tone.fg} />
                ) : !option.manual ? (
                  <Text style={styles.autoLabel}>auto</Text>
                ) : null}
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
  headerRow: { flexDirection: "row", alignItems: "flex-start", gap: 10, marginBottom: 20 },
  flex1: { flex: 1 },
  greeting: { color: colors.text, fontSize: 22, fontWeight: "700" },
  vehicle: { color: colors.muted, fontSize: 13.5, marginTop: 4 },
  statusChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    borderRadius: 20,
    borderWidth: 1,
    paddingHorizontal: 11,
    paddingVertical: 7,
    maxWidth: 150,
  },
  statusChipText: { fontSize: 11.5, fontWeight: "700", flexShrink: 1 },
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
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    backgroundColor: colors.amberSoft,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.amber,
    paddingHorizontal: 14,
    paddingVertical: 12,
    marginBottom: 16,
  },
  bookingNoticeText: { color: colors.amber, fontSize: 13, fontWeight: "600", flex: 1 },
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
    paddingVertical: 14,
  },
  statusOptionLeft: { flexDirection: "row", alignItems: "center", gap: 12 },
  statusOptionDisabled: { opacity: 0.5 },
  statusOptionText: { color: colors.text, fontSize: 14.5, fontWeight: "600" },
  autoLabel: {
    color: colors.muted,
    fontSize: 10.5,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 3,
  },
  error: { color: colors.red, fontSize: 13, marginTop: 16, textAlign: "center" },
  logout: { marginTop: "auto", alignItems: "center", paddingVertical: 12 },
  logoutText: { color: colors.muted, fontSize: 13, fontWeight: "600", textDecorationLine: "underline" },
});
