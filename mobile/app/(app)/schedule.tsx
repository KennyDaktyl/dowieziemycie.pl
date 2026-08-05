import { Ionicons } from "@expo/vector-icons";
import { useCallback, useState } from "react";
import { useFocusEffect, useRouter } from "expo-router";
import { ActivityIndicator, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BookingCard } from "@/components/BookingCard";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

// A booking lands in "my schedule" as soon as it's assigned to me (accept
// only claims it), so the visible action covers the whole lifecycle from
// there: OPLACONA -> KIEROWCA_W_DRODZE ("Jadę do klienta") -> W_TRAKCIE
// ("Rozpocznij kurs") -> ZAKONCZONA ("Zakończ kurs", drops off this list).
// Kept as a quick-action right on the card (not just inside the detail
// screen) since it's the single most frequent thing a driver taps all day.
const NEXT_ACTION: Record<string, { endpoint: string; label: string; icon: keyof typeof Ionicons.glyphMap } | undefined> = {
  OPLACONA: { endpoint: "head-to-customer", label: "Jadę do klienta", icon: "car" },
  KIEROWCA_W_DRODZE: { endpoint: "start", label: "Rozpocznij kurs", icon: "play" },
  W_TRAKCIE: { endpoint: "finish", label: "Zakończ kurs", icon: "checkmark-done" },
};

const RESULTING_DRIVER_STATUS: Record<string, "JADACY_PO_KLIENTA" | "W_KURSIE" | "DOSTEPNY"> = {
  "head-to-customer": "JADACY_PO_KLIENTA",
  start: "W_KURSIE",
  finish: "DOSTEPNY",
};

export default function ScheduleScreen() {
  const { accessToken, updateStatus } = useAuth();
  const router = useRouter();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [actingId, setActingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<DriverBooking[]>("/api/fleet/driver/schedule/", accessToken);
      setBookings(data);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  async function handleAction(booking: DriverBooking) {
    const action = NEXT_ACTION[booking.status];
    if (!action) return;
    setActingId(booking.id);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/${action.endpoint}/`, accessToken, { method: "POST" });
      updateStatus(RESULTING_DRIVER_STATUS[action.endpoint as keyof typeof RESULTING_DRIVER_STATUS]);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zaktualizować kursu.");
    } finally {
      setActingId(null);
    }
  }

  return (
    <SafeAreaView style={styles.screen} edges={["bottom"]}>
      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color={colors.amber} />
        </View>
      ) : (
        <FlatList
          data={bookings}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={false} onRefresh={load} tintColor={colors.amber} />}
          ListEmptyComponent={
            <View style={styles.center}>
              <Text style={styles.emptyText}>Brak zaplanowanych kursów.</Text>
            </View>
          }
          renderItem={({ item }) => {
            const action = NEXT_ACTION[item.status];
            return (
              <BookingCard
                booking={item}
                onPress={() =>
                  router.push({
                    pathname: "/booking/[id]",
                    params: { id: String(item.id), source: "schedule", booking: JSON.stringify(item) },
                  })
                }
                footer={
                  action ? (
                    <Pressable
                      onPress={() => handleAction(item)}
                      disabled={actingId === item.id}
                      style={({ pressed }) => [
                        styles.actionButton,
                        actingId === item.id && styles.actionButtonDisabled,
                        pressed && { opacity: 0.85 },
                      ]}
                    >
                      {actingId === item.id ? (
                        <ActivityIndicator size="small" color="#1A1305" />
                      ) : (
                        <>
                          <Ionicons name={action.icon} size={16} color="#1A1305" />
                          <Text style={styles.actionButtonText}>{action.label}</Text>
                        </>
                      )}
                    </Pressable>
                  ) : null
                }
              />
            );
          }}
        />
      )}
      {error && (
        <View style={styles.errorBar}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  center: { flex: 1, alignItems: "center", justifyContent: "center", paddingTop: 60 },
  emptyText: { color: colors.muted, fontSize: 14 },
  list: { padding: 16, gap: 12 },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 7,
    backgroundColor: colors.amber,
    borderRadius: 9,
    paddingVertical: 12,
    marginTop: 10,
  },
  actionButtonDisabled: { opacity: 0.6 },
  actionButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 14 },
  errorBar: { padding: 12, backgroundColor: colors.panel2 },
  errorText: { color: colors.red, fontSize: 13, textAlign: "center" },
});
