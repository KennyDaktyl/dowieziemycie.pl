import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import { ActivityIndicator, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BookingDetailModal } from "@/components/BookingDetailModal";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { siteLabel } from "@/lib/site";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = {
  KIEROWCA_W_DRODZE: "W drodze do klienta",
  W_TRAKCIE: "W trakcie kursu",
  POTWIERDZONA: "Potwierdzona",
  NOWA: "Nowa",
};

// A booking only ever lands in "my schedule" already assigned to me
// (accept sets both at once) — so the only actions are moving it forward
// one step: KIEROWCA_W_DRODZE -> W_TRAKCIE -> ZAKONCZONA (which then drops
// off this list and into Historia).
const NEXT_ACTION: Record<string, { endpoint: string; label: string } | undefined> = {
  KIEROWCA_W_DRODZE: { endpoint: "start", label: "Rozpocznij kurs" },
  W_TRAKCIE: { endpoint: "finish", label: "Zakończ kurs" },
};

export default function ScheduleScreen() {
  const { accessToken } = useAuth();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [actingId, setActingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<DriverBooking | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const data = await apiFetch<DriverBooking[]>("/api/fleet/driver/schedule/", accessToken);
      setBookings(data);
    } catch {
      setError("Nie udało się pobrać listy kursów.");
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
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/${action.endpoint}/`, accessToken, {
        method: "POST",
      });
      setSelected(null);
      load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zaktualizować kursu.");
    } finally {
      setActingId(null);
    }
  }

  function renderActionButton(booking: DriverBooking) {
    const action = NEXT_ACTION[booking.status];
    if (!action) return null;
    return (
      <Pressable
        onPress={() => handleAction(booking)}
        disabled={actingId === booking.id}
        style={({ pressed }) => [
          styles.actionButton,
          actingId === booking.id && styles.actionButtonDisabled,
          pressed && { opacity: 0.85 },
        ]}
      >
        {actingId === booking.id ? (
          <ActivityIndicator size="small" color="#1A1305" />
        ) : (
          <Text style={styles.actionButtonText}>{action.label}</Text>
        )}
      </Pressable>
    );
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
          renderItem={({ item }) => (
            <Pressable onPress={() => setSelected(item)} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.site}>{siteLabel(item.site)}</Text>
                <Text style={styles.badge}>{STATUS_LABELS[item.status] ?? item.status}</Text>
              </View>
              <Text style={styles.route}>
                {item.pickup_address} → {item.dropoff_address}
              </Text>
              <Text style={styles.meta}>
                {new Date(item.scheduled_at).toLocaleString("pl-PL")} · {item.customer_name || item.customer_phone}
              </Text>
              <Text style={styles.meta}>{item.customer_phone}</Text>
              {renderActionButton(item)}
            </Pressable>
          )}
        />
      )}
      {error && (
        <View style={styles.errorBar}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}
      <BookingDetailModal booking={selected} onClose={() => setSelected(null)}>
        {selected && renderActionButton(selected)}
      </BookingDetailModal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  center: { flex: 1, alignItems: "center", justifyContent: "center", paddingTop: 60 },
  emptyText: { color: colors.muted, fontSize: 14 },
  list: { padding: 16, gap: 12 },
  card: {
    backgroundColor: colors.panel,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 16,
  },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 8 },
  site: {
    color: colors.muted,
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  route: { color: colors.text, fontSize: 15, fontWeight: "700", marginTop: 6 },
  badge: {
    color: colors.amber,
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 20,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  meta: { color: colors.muted, fontSize: 13, marginTop: 6 },
  actionButton: {
    backgroundColor: colors.amber,
    borderRadius: 9,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 12,
  },
  actionButtonDisabled: { opacity: 0.6 },
  actionButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 14 },
  errorBar: { padding: 12, backgroundColor: colors.panel2 },
  errorText: { color: colors.red, fontSize: 13, textAlign: "center" },
});
