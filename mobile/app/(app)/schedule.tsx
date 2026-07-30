import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import { ActivityIndicator, FlatList, RefreshControl, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = {
  KIEROWCA_W_DRODZE: "W drodze do klienta",
  W_TRAKCIE: "W trakcie kursu",
  POTWIERDZONA: "Potwierdzona",
  NOWA: "Nowa",
};

export default function ScheduleScreen() {
  const { accessToken } = useAuth();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);

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
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.route}>
                  {item.pickup_address} → {item.dropoff_address}
                </Text>
                <Text style={styles.badge}>{STATUS_LABELS[item.status] ?? item.status}</Text>
              </View>
              <Text style={styles.meta}>
                {new Date(item.scheduled_at).toLocaleString("pl-PL")} · {item.customer_name || item.customer_phone}
              </Text>
              <Text style={styles.meta}>{item.customer_phone}</Text>
            </View>
          )}
        />
      )}
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
  route: { color: colors.text, fontSize: 15, fontWeight: "700", flex: 1 },
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
});
