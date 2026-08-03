import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { siteLabel } from "@/lib/site";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

const STATUS_LABELS: Record<string, string> = {
  NOWA: "Nowa",
  POTWIERDZONA: "Potwierdzona",
  OPLACONA: "Opłacona",
  KIEROWCA_W_DRODZE: "Kierowca w drodze",
  W_TRAKCIE: "W trakcie kursu",
  ZAKONCZONA: "Zakończona",
  ANULOWANA: "Anulowana",
};

const DEFAULT_DEPOSIT_RATIO = 0.3;

interface EditState {
  price: string;
  deposit: string;
  depositManual: boolean;
}

function formatDateTime(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("pl-PL", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export default function AllBookingsScreen() {
  const { accessToken } = useAuth();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [edits, setEdits] = useState<Record<number, EditState>>({});
  const [savingId, setSavingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const data = await apiFetch<DriverBooking[]>("/api/fleet/driver/bookings/all/", accessToken);
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

  function toggleExpand(booking: DriverBooking) {
    if (expandedId === booking.id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(booking.id);
    if (!edits[booking.id]) {
      const suggestedPrice = booking.price ?? "";
      const suggestedDeposit =
        booking.deposit_amount ??
        (booking.price ? String(Math.round(Number(booking.price) * DEFAULT_DEPOSIT_RATIO)) : "");
      setEdits((prev) => ({
        ...prev,
        [booking.id]: { price: suggestedPrice, deposit: suggestedDeposit, depositManual: false },
      }));
    }
  }

  function onChangePrice(bookingId: number, text: string) {
    setEdits((prev) => {
      const current = prev[bookingId] ?? { price: "", deposit: "", depositManual: false };
      const price = parseFloat(text.replace(",", "."));
      const deposit = current.depositManual
        ? current.deposit
        : Number.isFinite(price)
          ? String(Math.round(price * DEFAULT_DEPOSIT_RATIO))
          : current.deposit;
      return { ...prev, [bookingId]: { ...current, price: text, deposit } };
    });
  }

  function onChangeDeposit(bookingId: number, text: string) {
    setEdits((prev) => {
      const current = prev[bookingId] ?? { price: "", deposit: "", depositManual: false };
      return { ...prev, [bookingId]: { ...current, deposit: text, depositManual: true } };
    });
  }

  async function handleConfirm(booking: DriverBooking) {
    const edit = edits[booking.id];
    if (!edit) return;
    const price = parseFloat(edit.price.replace(",", "."));
    const deposit = parseFloat(edit.deposit.replace(",", "."));
    if (!Number.isFinite(price) || !Number.isFinite(deposit)) {
      setError("Podaj poprawną cenę i zaliczkę.");
      return;
    }
    setSavingId(booking.id);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/confirm/`, accessToken, {
        method: "POST",
        body: JSON.stringify({ price, deposit_amount: deposit }),
      });
      setExpandedId(null);
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się potwierdzić kursu.");
    } finally {
      setSavingId(null);
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
              <Text style={styles.emptyText}>Brak kursów.</Text>
            </View>
          }
          renderItem={({ item }) => {
            const expanded = expandedId === item.id;
            const edit = edits[item.id];
            const remainder =
              edit && Number.isFinite(parseFloat(edit.price)) && Number.isFinite(parseFloat(edit.deposit))
                ? (parseFloat(edit.price.replace(",", ".")) - parseFloat(edit.deposit.replace(",", "."))).toFixed(0)
                : null;
            return (
              <Pressable onPress={() => toggleExpand(item)} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.site}>{siteLabel(item.site)}</Text>
                  <Text style={styles.badge}>{STATUS_LABELS[item.status] ?? item.status}</Text>
                </View>
                <Text style={styles.route}>
                  {item.pickup_address} → {item.dropoff_address}
                </Text>
                <Text style={styles.meta}>
                  {formatDateTime(item.scheduled_at)} · {item.customer_name || item.customer_phone} · {item.passenger_count} os.
                </Text>
                <Text style={styles.price}>{item.price ? `${Number(item.price).toFixed(0)} zł` : "Wycena indywidualna"}</Text>

                {expanded && (
                  <View style={styles.detail}>
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Klient</Text>
                      <Text style={styles.detailValue}>{item.customer_name || "—"}</Text>
                    </View>
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Telefon</Text>
                      <Text style={styles.detailValue}>{item.customer_phone}</Text>
                    </View>
                    {item.tracking_code ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Kod śledzenia</Text>
                        <Text style={styles.detailValue}>
                          {item.tracking_code} · aktywny {formatDateTime(item.tracking_code_valid_from)} –{" "}
                          {formatDateTime(item.tracking_code_expires_at)}
                        </Text>
                      </View>
                    ) : null}

                    {item.status === "NOWA" && edit ? (
                      <View style={styles.editForm}>
                        <Text style={styles.editLabel}>Cena kursu (zł)</Text>
                        <TextInput
                          value={edit.price}
                          onChangeText={(text) => onChangePrice(item.id, text)}
                          keyboardType="numeric"
                          placeholder="np. 150"
                          placeholderTextColor={colors.muted}
                          style={styles.input}
                        />
                        <Text style={styles.editLabel}>Zaliczka (zł)</Text>
                        <TextInput
                          value={edit.deposit}
                          onChangeText={(text) => onChangeDeposit(item.id, text)}
                          keyboardType="numeric"
                          placeholder="np. 45"
                          placeholderTextColor={colors.muted}
                          style={styles.input}
                        />
                        <Text style={styles.remainder}>
                          Reszta do zapłaty po zaliczce: {remainder !== null ? `${remainder} zł` : "—"}
                        </Text>
                        <Pressable
                          onPress={() => handleConfirm(item)}
                          disabled={savingId === item.id}
                          style={({ pressed }) => [
                            styles.confirmButton,
                            savingId === item.id && styles.confirmButtonDisabled,
                            pressed && { opacity: 0.85 },
                          ]}
                        >
                          {savingId === item.id ? (
                            <ActivityIndicator size="small" color="#1A1305" />
                          ) : (
                            <Text style={styles.confirmButtonText}>Potwierdź kurs</Text>
                          )}
                        </Pressable>
                      </View>
                    ) : (
                      <View style={styles.editForm}>
                        <View style={styles.detailRow}>
                          <Text style={styles.detailLabel}>Zaliczka</Text>
                          <Text style={styles.detailValue}>
                            {item.deposit_amount ? `${Number(item.deposit_amount).toFixed(0)} zł` : "—"}
                          </Text>
                        </View>
                      </View>
                    )}
                  </View>
                )}
              </Pressable>
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
  card: {
    backgroundColor: colors.panel,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 16,
  },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 8 },
  site: { color: colors.muted, fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.5 },
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
  route: { color: colors.text, fontSize: 15, fontWeight: "700", marginTop: 6 },
  meta: { color: colors.muted, fontSize: 13, marginTop: 6 },
  price: { color: colors.green, fontSize: 16, fontWeight: "700", marginTop: 8 },
  detail: { marginTop: 14, paddingTop: 14, borderTopWidth: 1, borderTopColor: colors.line, gap: 8 },
  detailRow: { flexDirection: "row", justifyContent: "space-between", gap: 8 },
  detailLabel: { color: colors.muted, fontSize: 13 },
  detailValue: { color: colors.text, fontSize: 13, fontWeight: "600", flexShrink: 1, textAlign: "right" },
  editForm: { marginTop: 6, gap: 8 },
  editLabel: { color: colors.muted, fontSize: 12, fontWeight: "600", marginTop: 4 },
  input: {
    backgroundColor: colors.panel2,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.line,
    color: colors.text,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
  },
  remainder: { color: colors.text, fontSize: 13, fontWeight: "600", marginTop: 4 },
  confirmButton: { backgroundColor: colors.amber, borderRadius: 9, paddingVertical: 12, alignItems: "center", marginTop: 8 },
  confirmButtonDisabled: { opacity: 0.6 },
  confirmButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 14 },
  errorBar: { padding: 12, backgroundColor: colors.panel2 },
  errorText: { color: colors.red, fontSize: 13, textAlign: "center" },
});
