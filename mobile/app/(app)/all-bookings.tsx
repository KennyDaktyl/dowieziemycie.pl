import { useCallback, useState } from "react";
import { useFocusEffect, useRouter } from "expo-router";
import { ActivityIndicator, FlatList, Pressable, RefreshControl, StyleSheet, Text, TextInput, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BookingCard } from "@/components/BookingCard";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { bookingRef } from "@/lib/booking-ref";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

type SortMode = "newest" | "upcoming";

const TERMINAL_STATUSES = ["ZAKONCZONA", "ANULOWANA"];

export default function AllBookingsScreen() {
  const { accessToken } = useAuth();
  const router = useRouter();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("newest");
  const [showArchived, setShowArchived] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<DriverBooking[]>("/api/fleet/driver/bookings/all/", accessToken);
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

  // Archived (finished/cancelled) kursy stay out of the default view — this
  // list otherwise mixes everything, unlike Kursy/Harmonogram which are
  // already scoped to open/active bookings. Search matches the short
  // reference code (see lib/booking-ref) or the raw numeric id, since
  // that's what a dispatcher would actually have written down or been told
  // over the phone.
  const query = searchQuery.trim().toLowerCase();
  const visibleBookings = bookings
    .filter((b) => showArchived || !TERMINAL_STATUSES.includes(b.status))
    .filter((b) => !query || bookingRef(b).toLowerCase().includes(query) || String(b.id).includes(query))
    .sort((a, b) =>
      sortMode === "newest" ? b.id - a.id : new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime(),
    );

  return (
    <SafeAreaView style={styles.screen} edges={["bottom"]}>
      <View style={styles.toolbar}>
        <TextInput
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Szukaj po ID (np. Ry6Sk)"
          placeholderTextColor={colors.muted}
          style={styles.searchInput}
          autoCapitalize="none"
        />
        <View style={styles.toolbarRow}>
          <Pressable onPress={() => setSortMode((m) => (m === "newest" ? "upcoming" : "newest"))} style={styles.toolbarButton}>
            <Text style={styles.toolbarButtonText}>{sortMode === "newest" ? "Sortuj: najnowsze" : "Sortuj: nadchodzące"}</Text>
          </Pressable>
          <Pressable
            onPress={() => setShowArchived((v) => !v)}
            style={[styles.toolbarButton, showArchived && styles.toolbarButtonActive]}
          >
            <Text style={[styles.toolbarButtonText, showArchived && styles.toolbarButtonTextActive]}>
              {showArchived ? "Ukryj archiwalne" : "Pokaż archiwalne"}
            </Text>
          </Pressable>
        </View>
      </View>
      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator color={colors.amber} />
        </View>
      ) : (
        <FlatList
          data={visibleBookings}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={styles.list}
          refreshControl={<RefreshControl refreshing={false} onRefresh={load} tintColor={colors.amber} />}
          ListEmptyComponent={
            <View style={styles.center}>
              <Text style={styles.emptyText}>Brak kursów.</Text>
            </View>
          }
          renderItem={({ item }) => (
            <BookingCard
              booking={item}
              onPress={() =>
                router.push({
                  pathname: "/booking/[id]",
                  params: { id: String(item.id), source: "all-bookings", booking: JSON.stringify(item) },
                })
              }
            />
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
  toolbar: {
    gap: 8,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 4,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  searchInput: {
    backgroundColor: colors.panel2,
    borderRadius: 9,
    borderWidth: 1,
    borderColor: colors.line,
    color: colors.text,
    paddingHorizontal: 12,
    paddingVertical: 9,
    fontSize: 13.5,
  },
  toolbarRow: { flexDirection: "row", gap: 8, marginBottom: 8 },
  toolbarButton: {
    flex: 1,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: "center",
  },
  toolbarButtonActive: { borderColor: colors.amber, backgroundColor: colors.panel2 },
  toolbarButtonText: { color: colors.muted, fontSize: 12, fontWeight: "600" },
  toolbarButtonTextActive: { color: colors.amber },
});
