import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import { ActivityIndicator, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BookingCard } from "@/components/BookingCard";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

export default function BookingsScreen() {
  const { accessToken } = useAuth();
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
      // Just a claim — doesn't mark the driver busy or move the booking
      // forward. "Jadę do klienta" (in "Moje kursy", where this booking
      // shows up next) is the separate, explicit step for that.
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/accept/`, accessToken, { method: "POST" });
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
            <BookingCard
              booking={item}
              footer={
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
              }
            />
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
  acceptButton: { backgroundColor: colors.amber, borderRadius: 9, paddingVertical: 12, alignItems: "center", marginTop: 10 },
  acceptButtonDisabled: { opacity: 0.6 },
  acceptButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 14 },
  errorBar: { padding: 12, backgroundColor: colors.panel2 },
  errorText: { color: colors.red, fontSize: 13, textAlign: "center" },
});
