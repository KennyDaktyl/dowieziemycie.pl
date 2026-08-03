import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import { ActivityIndicator, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { siteLabel } from "@/lib/site";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

export default function BookingsScreen() {
  const { accessToken, updateStatus } = useAuth();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [acceptingId, setAcceptingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const data = await apiFetch<DriverBooking[]>("/api/fleet/driver/bookings/open/", accessToken);
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

  async function handleAccept(booking: DriverBooking) {
    setAcceptingId(booking.id);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/accept/`, accessToken, { method: "POST" });
      // Mirrors AcceptBookingView's side effect (driver.status -> JADACY_PO_KLIENTA)
      // so the Panel tab doesn't keep showing "Aktywny (wolny)" after accepting.
      updateStatus("JADACY_PO_KLIENTA");
      setBookings((prev) => prev.filter((b) => b.id !== booking.id));
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się przyjąć kursu.");
    } finally {
      setAcceptingId(null);
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
              <Text style={styles.emptyText}>Brak wolnych kursów do przyjęcia.</Text>
              <Text style={styles.emptyHint}>
                To lista kursów opłaconych przez klienta, które nie ma jeszcze przypisanego kierowcy. Kursy już
                przypisane do Ciebie (także te czekające na potwierdzenie lub zaliczkę) zobaczysz w zakładce „Moje
                kursy”.
              </Text>
            </View>
          }
          renderItem={({ item }) => (
            <View style={styles.card}>
              <Text style={styles.site}>{siteLabel(item.site)}</Text>
              <Text style={styles.route}>
                {item.pickup_address} → {item.dropoff_address}
              </Text>
              <Text style={styles.meta}>
                {new Date(item.scheduled_at).toLocaleString("pl-PL")} · {item.passenger_count} os.
                {item.distance_km ? ` · ${item.distance_km} km` : ""}
              </Text>
              <Text style={styles.price}>{item.price ? `${Number(item.price).toFixed(0)} zł` : "Wycena indywidualna"}</Text>
              <Pressable
                onPress={() => handleAccept(item)}
                disabled={acceptingId === item.id}
                style={({ pressed }) => [
                  styles.acceptButton,
                  acceptingId === item.id && styles.acceptButtonDisabled,
                  pressed && { opacity: 0.85 },
                ]}
              >
                {acceptingId === item.id ? (
                  <ActivityIndicator size="small" color="#1A1305" />
                ) : (
                  <Text style={styles.acceptButtonText}>Przyjmuję kurs</Text>
                )}
              </Pressable>
            </View>
          )}
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
  emptyText: { color: colors.muted, fontSize: 14, textAlign: "center" },
  emptyHint: { color: colors.muted, fontSize: 12.5, textAlign: "center", marginTop: 8, paddingHorizontal: 24 },
  list: { padding: 16, gap: 12 },
  card: {
    backgroundColor: colors.panel,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 16,
  },
  site: { color: colors.muted, fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.5 },
  route: { color: colors.text, fontSize: 15, fontWeight: "700", marginTop: 6 },
  meta: { color: colors.muted, fontSize: 13, marginTop: 6 },
  price: { color: colors.green, fontSize: 16, fontWeight: "700", marginTop: 8 },
  acceptButton: { backgroundColor: colors.amber, borderRadius: 9, paddingVertical: 12, alignItems: "center", marginTop: 12 },
  acceptButtonDisabled: { opacity: 0.6 },
  acceptButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 14 },
  errorBar: { padding: 12, backgroundColor: colors.panel2 },
  errorText: { color: colors.red, fontSize: 13, textAlign: "center" },
});
