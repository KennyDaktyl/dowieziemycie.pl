import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { formatDuration, paymentAmounts, paymentStatusLabel } from "@/components/BookingDetailModal";
import { BookingMap } from "@/components/BookingMap";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { openNavigation } from "@/lib/navigation";
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

const TERMINAL_STATUSES = ["ZAKONCZONA", "ANULOWANA"];
const DEFAULT_DEPOSIT_RATIO = 0.3;

interface PriceEditState {
  price: string;
  deposit: string;
  depositManual: boolean;
}

interface DetailEditState {
  pickupAddress: string;
  dropoffAddress: string;
  passengerCount: string;
  dateText: string;
  timeText: string;
}

function formatDateTime(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("pl-PL", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function toDateEditFields(iso: string): { dateText: string; timeText: string } {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return {
    dateText: `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`,
    timeText: `${pad(d.getHours())}:${pad(d.getMinutes())}`,
  };
}

function parseDateEditFields(dateText: string, timeText: string): string | null {
  const dateMatch = dateText.trim().match(/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/);
  const timeMatch = timeText.trim().match(/^(\d{1,2}):(\d{2})$/);
  if (!dateMatch || !timeMatch) return null;
  const [, day, month, year] = dateMatch;
  const [, hour, minute] = timeMatch;
  const d = new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute));
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString();
}

export default function AllBookingsScreen() {
  const { accessToken, driver, updateStatus } = useAuth();
  const [bookings, setBookings] = useState<DriverBooking[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [priceEdits, setPriceEdits] = useState<Record<number, PriceEditState>>({});
  const [editingDetailsId, setEditingDetailsId] = useState<number | null>(null);
  const [editingPriceId, setEditingPriceId] = useState<number | null>(null);
  const [detailEdits, setDetailEdits] = useState<Record<number, DetailEditState>>({});
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
      setEditingDetailsId(null);
      setEditingPriceId(null);
      return;
    }
    setExpandedId(booking.id);
    setEditingDetailsId(null);
    setEditingPriceId(null);
    if (!priceEdits[booking.id]) {
      const suggestedPrice = booking.price ?? "";
      const suggestedDeposit =
        booking.deposit_amount ??
        (booking.price ? String(Math.round(Number(booking.price) * DEFAULT_DEPOSIT_RATIO)) : "");
      setPriceEdits((prev) => ({
        ...prev,
        [booking.id]: { price: suggestedPrice, deposit: suggestedDeposit, depositManual: false },
      }));
    }
  }

  function startEditingDetails(booking: DriverBooking) {
    setEditingDetailsId(booking.id);
    setDetailEdits((prev) => ({
      ...prev,
      [booking.id]: {
        pickupAddress: booking.pickup_address,
        dropoffAddress: booking.dropoff_address,
        passengerCount: String(booking.passenger_count),
        ...toDateEditFields(booking.scheduled_at),
      },
    }));
  }

  function onChangePrice(bookingId: number, text: string) {
    setPriceEdits((prev) => {
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
    setPriceEdits((prev) => {
      const current = prev[bookingId] ?? { price: "", deposit: "", depositManual: false };
      return { ...prev, [bookingId]: { ...current, deposit: text, depositManual: true } };
    });
  }

  async function handleConfirm(booking: DriverBooking) {
    const edit = priceEdits[booking.id];
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

  async function handleUpdatePrice(booking: DriverBooking) {
    const edit = priceEdits[booking.id];
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
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/update/`, accessToken, {
        method: "PATCH",
        body: JSON.stringify({ price, deposit_amount: deposit }),
      });
      setEditingPriceId(null);
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zapisać ceny.");
    } finally {
      setSavingId(null);
    }
  }

  async function handleSaveDetails(booking: DriverBooking) {
    const edit = detailEdits[booking.id];
    if (!edit) return;
    const passengerCount = parseInt(edit.passengerCount, 10);
    const scheduledAt = parseDateEditFields(edit.dateText, edit.timeText);
    if (!scheduledAt) {
      setError("Podaj poprawną datę (DD.MM.RRRR) i godzinę (GG:MM).");
      return;
    }
    if (!Number.isFinite(passengerCount) || passengerCount < 1) {
      setError("Podaj poprawną liczbę pasażerów.");
      return;
    }
    setSavingId(booking.id);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/update/`, accessToken, {
        method: "PATCH",
        body: JSON.stringify({
          pickup_address: edit.pickupAddress,
          dropoff_address: edit.dropoffAddress,
          passenger_count: passengerCount,
          scheduled_at: scheduledAt,
        }),
      });
      setEditingDetailsId(null);
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zapisać zmian.");
    } finally {
      setSavingId(null);
    }
  }

  async function handleAssign(booking: DriverBooking, driverId: number | null) {
    setSavingId(booking.id);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/update/`, accessToken, {
        method: "PATCH",
        body: JSON.stringify({ assigned_driver_id: driverId }),
      });
      // Mirrors UpdateBookingView's side effect: assigning yourself to a
      // still-OPLACONA booking claims it exactly like AcceptBookingView does
      // (status -> KIEROWCA_W_DRODZE, driver.status -> JADACY_PO_KLIENTA) —
      // without this the Panel tab would keep showing stale status.
      if (driverId != null && driverId === driver?.id && booking.status === "OPLACONA") {
        updateStatus("JADACY_PO_KLIENTA");
      }
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zmienić przypisania kierowcy.");
    } finally {
      setSavingId(null);
    }
  }

  async function handleLifecycleAction(booking: DriverBooking, endpoint: string) {
    setSavingId(booking.id);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/${endpoint}/`, accessToken, { method: "POST" });
      const resultingStatus = { accept: "JADACY_PO_KLIENTA", start: "W_KURSIE", finish: "DOSTEPNY" } as const;
      if (endpoint in resultingStatus) updateStatus(resultingStatus[endpoint as keyof typeof resultingStatus]);
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zaktualizować kursu.");
    } finally {
      setSavingId(null);
    }
  }

  function handleCancel(booking: DriverBooking) {
    Alert.alert(
      "Anulować kurs?",
      `${booking.pickup_address} → ${booking.dropoff_address}, ${formatDateTime(booking.scheduled_at)}. Klient dostanie SMS/e-mail o anulowaniu.`,
      [
        { text: "Nie", style: "cancel" },
        { text: "Tak, anuluj", style: "destructive", onPress: () => handleLifecycleAction(booking, "cancel") },
      ],
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
              <Text style={styles.emptyText}>Brak kursów.</Text>
            </View>
          }
          renderItem={({ item }) => {
            const expanded = expandedId === item.id;
            const editingDetails = editingDetailsId === item.id;
            const priceEdit = priceEdits[item.id];
            const detailEdit = detailEdits[item.id];
            const canEdit = !TERMINAL_STATUSES.includes(item.status);
            const isMine = driver != null && item.assigned_driver_id === driver.id;
            const remainder =
              priceEdit && Number.isFinite(parseFloat(priceEdit.price)) && Number.isFinite(parseFloat(priceEdit.deposit))
                ? (
                    parseFloat(priceEdit.price.replace(",", ".")) - parseFloat(priceEdit.deposit.replace(",", "."))
                  ).toFixed(0)
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
                    {item.pickup_lat && item.pickup_lng ? (
                      <BookingMap
                        pickup={{ lat: Number(item.pickup_lat), lng: Number(item.pickup_lng) }}
                        dropoff={
                          item.dropoff_lat && item.dropoff_lng
                            ? { lat: Number(item.dropoff_lat), lng: Number(item.dropoff_lng) }
                            : null
                        }
                      />
                    ) : null}
                    <View style={styles.assignRow}>
                      {item.pickup_lat && item.pickup_lng && (
                        <Pressable
                          onPress={() => openNavigation(Number(item.pickup_lat), Number(item.pickup_lng))}
                          style={styles.navButton}
                        >
                          <Text style={styles.navButtonIcon}>📍</Text>
                          <Text style={styles.smallButtonOutlineText}>Nawiguj do odbioru</Text>
                        </Pressable>
                      )}
                      {item.dropoff_lat && item.dropoff_lng && (
                        <Pressable
                          onPress={() => openNavigation(Number(item.dropoff_lat), Number(item.dropoff_lng))}
                          style={styles.navButton}
                        >
                          <Text style={styles.navButtonIcon}>🏁</Text>
                          <Text style={styles.smallButtonOutlineText}>Nawiguj do celu</Text>
                        </Pressable>
                      )}
                    </View>
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Klient</Text>
                      <Text style={styles.detailValue}>{item.customer_name || "—"}</Text>
                    </View>
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Telefon</Text>
                      <Text style={styles.detailValue}>{item.customer_phone}</Text>
                    </View>
                    {item.flight_number ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Numer lotu</Text>
                        <Text style={styles.detailValue}>{item.flight_number}</Text>
                      </View>
                    ) : null}
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Płatność</Text>
                      <Text style={styles.detailValue}>{paymentStatusLabel(item)}</Text>
                    </View>
                    {(() => {
                      const amounts = paymentAmounts(item);
                      if (!amounts) return null;
                      return (
                        <>
                          <View style={styles.detailRow}>
                            <Text style={styles.detailLabel}>Zapłacono</Text>
                            <Text style={styles.detailValue}>{amounts.paid.toFixed(0)} zł</Text>
                          </View>
                          {amounts.remaining > 0 && (
                            <View style={styles.detailRow}>
                              <Text style={styles.detailLabel}>Pozostało do zapłaty</Text>
                              <Text style={styles.detailValue}>{amounts.remaining.toFixed(0)} zł</Text>
                            </View>
                          )}
                        </>
                      );
                    })()}
                    {item.distance_km ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Dystans (planowany)</Text>
                        <Text style={styles.detailValue}>{item.distance_km} km</Text>
                      </View>
                    ) : null}
                    {item.actual_distance_km ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Dystans (przejechany)</Text>
                        <Text style={styles.detailValue}>{item.actual_distance_km} km</Text>
                      </View>
                    ) : null}
                    {item.duration_minutes ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Planowany czas zajętości</Text>
                        <Text style={styles.detailValue}>{item.duration_minutes} min</Text>
                      </View>
                    ) : null}
                    {item.started_at ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Start kursu</Text>
                        <Text style={styles.detailValue}>{formatDateTime(item.started_at)}</Text>
                      </View>
                    ) : null}
                    {item.completed_at ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Koniec kursu</Text>
                        <Text style={styles.detailValue}>{formatDateTime(item.completed_at)}</Text>
                      </View>
                    ) : null}
                    {formatDuration(item.started_at, item.completed_at) ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Rzeczywisty czas kursu</Text>
                        <Text style={styles.detailValue}>{formatDuration(item.started_at, item.completed_at)}</Text>
                      </View>
                    ) : null}
                    {item.tracking_code ? (
                      <View style={styles.detailRow}>
                        <Text style={styles.detailLabel}>Kod śledzenia</Text>
                        <Text style={styles.detailValue}>
                          {item.tracking_code} · aktywny {formatDateTime(item.tracking_code_valid_from)} –{" "}
                          {formatDateTime(item.tracking_code_expires_at)}
                        </Text>
                      </View>
                    ) : null}
                    <View style={styles.detailRow}>
                      <Text style={styles.detailLabel}>Kierowca</Text>
                      <Text style={styles.detailValue}>{item.assigned_driver_name || "Nieprzypisany"}</Text>
                    </View>

                    {canEdit && (
                      <View style={styles.assignRow}>
                        {!isMine && (
                          <Pressable
                            onPress={() => handleAssign(item, driver?.id ?? null)}
                            disabled={savingId === item.id}
                            style={styles.smallButton}
                          >
                            <Text style={styles.smallButtonText}>Przypisz do mnie</Text>
                          </Pressable>
                        )}
                        {item.assigned_driver_id != null && (
                          <Pressable
                            onPress={() => handleAssign(item, null)}
                            disabled={savingId === item.id}
                            style={styles.smallButtonOutline}
                          >
                            <Text style={styles.smallButtonOutlineText}>Odepnij kierowcę</Text>
                          </Pressable>
                        )}
                      </View>
                    )}

                    {canEdit && !editingDetails && (
                      <Pressable onPress={() => startEditingDetails(item)} style={styles.smallButtonOutline}>
                        <Text style={styles.smallButtonOutlineText}>Edytuj szczegóły kursu</Text>
                      </Pressable>
                    )}

                    {editingDetails && detailEdit && (
                      <View style={styles.editForm}>
                        <Text style={styles.editLabel}>Skąd</Text>
                        <TextInput
                          value={detailEdit.pickupAddress}
                          onChangeText={(text) =>
                            setDetailEdits((prev) => ({ ...prev, [item.id]: { ...prev[item.id], pickupAddress: text } }))
                          }
                          style={styles.input}
                          placeholderTextColor={colors.muted}
                        />
                        <Text style={styles.editLabel}>Dokąd</Text>
                        <TextInput
                          value={detailEdit.dropoffAddress}
                          onChangeText={(text) =>
                            setDetailEdits((prev) => ({ ...prev, [item.id]: { ...prev[item.id], dropoffAddress: text } }))
                          }
                          style={styles.input}
                          placeholderTextColor={colors.muted}
                        />
                        <View style={styles.row}>
                          <View style={styles.flex1}>
                            <Text style={styles.editLabel}>Data (DD.MM.RRRR)</Text>
                            <TextInput
                              value={detailEdit.dateText}
                              onChangeText={(text) =>
                                setDetailEdits((prev) => ({ ...prev, [item.id]: { ...prev[item.id], dateText: text } }))
                              }
                              placeholder="15.08.2026"
                              style={styles.input}
                              placeholderTextColor={colors.muted}
                            />
                          </View>
                          <View style={styles.flex1}>
                            <Text style={styles.editLabel}>Godzina (GG:MM)</Text>
                            <TextInput
                              value={detailEdit.timeText}
                              onChangeText={(text) =>
                                setDetailEdits((prev) => ({ ...prev, [item.id]: { ...prev[item.id], timeText: text } }))
                              }
                              placeholder="20:00"
                              style={styles.input}
                              placeholderTextColor={colors.muted}
                            />
                          </View>
                        </View>
                        <Text style={styles.editLabel}>Liczba pasażerów</Text>
                        <TextInput
                          value={detailEdit.passengerCount}
                          onChangeText={(text) =>
                            setDetailEdits((prev) => ({ ...prev, [item.id]: { ...prev[item.id], passengerCount: text } }))
                          }
                          keyboardType="numeric"
                          style={styles.input}
                          placeholderTextColor={colors.muted}
                        />
                        <View style={styles.row}>
                          <Pressable
                            onPress={() => setEditingDetailsId(null)}
                            style={[styles.smallButtonOutline, styles.flex1]}
                          >
                            <Text style={styles.smallButtonOutlineText}>Anuluj</Text>
                          </Pressable>
                          <Pressable
                            onPress={() => handleSaveDetails(item)}
                            disabled={savingId === item.id}
                            style={[styles.smallButton, styles.flex1]}
                          >
                            {savingId === item.id ? (
                              <ActivityIndicator size="small" color="#1A1305" />
                            ) : (
                              <Text style={styles.smallButtonText}>Zapisz zmiany</Text>
                            )}
                          </Pressable>
                        </View>
                      </View>
                    )}

                    {item.status === "NOWA" && priceEdit ? (
                      <View style={styles.editForm}>
                        <Text style={styles.editLabel}>Cena kursu (zł)</Text>
                        <TextInput
                          value={priceEdit.price}
                          onChangeText={(text) => onChangePrice(item.id, text)}
                          keyboardType="numeric"
                          placeholder="np. 150"
                          placeholderTextColor={colors.muted}
                          style={styles.input}
                        />
                        <Text style={styles.editLabel}>Zaliczka (zł)</Text>
                        <TextInput
                          value={priceEdit.deposit}
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
                    ) : editingPriceId === item.id && priceEdit ? (
                      <View style={styles.editForm}>
                        <Text style={styles.editLabel}>Cena kursu (zł)</Text>
                        <TextInput
                          value={priceEdit.price}
                          onChangeText={(text) => onChangePrice(item.id, text)}
                          keyboardType="numeric"
                          placeholder="np. 150"
                          placeholderTextColor={colors.muted}
                          style={styles.input}
                        />
                        <Text style={styles.editLabel}>Zaliczka (zł)</Text>
                        <TextInput
                          value={priceEdit.deposit}
                          onChangeText={(text) => onChangeDeposit(item.id, text)}
                          keyboardType="numeric"
                          placeholder="np. 45"
                          placeholderTextColor={colors.muted}
                          style={styles.input}
                        />
                        <View style={styles.row}>
                          <Pressable
                            onPress={() => setEditingPriceId(null)}
                            style={[styles.smallButtonOutline, styles.flex1]}
                          >
                            <Text style={styles.smallButtonOutlineText}>Anuluj</Text>
                          </Pressable>
                          <Pressable
                            onPress={() => handleUpdatePrice(item)}
                            disabled={savingId === item.id}
                            style={[styles.smallButton, styles.flex1]}
                          >
                            {savingId === item.id ? (
                              <ActivityIndicator size="small" color="#1A1305" />
                            ) : (
                              <Text style={styles.smallButtonText}>Zapisz cenę</Text>
                            )}
                          </Pressable>
                        </View>
                      </View>
                    ) : (
                      <>
                        <View style={styles.detailRow}>
                          <Text style={styles.detailLabel}>Zaliczka</Text>
                          <Text style={styles.detailValue}>
                            {item.deposit_amount ? `${Number(item.deposit_amount).toFixed(0)} zł` : "—"}
                          </Text>
                        </View>
                        {canEdit && (
                          <Pressable onPress={() => setEditingPriceId(item.id)} style={styles.smallButtonOutline}>
                            <Text style={styles.smallButtonOutlineText}>Edytuj cenę i zaliczkę</Text>
                          </Pressable>
                        )}
                      </>
                    )}

                    {item.status === "OPLACONA" && item.assigned_driver_id == null && (
                      <Pressable
                        onPress={() => handleLifecycleAction(item, "accept")}
                        disabled={savingId === item.id}
                        style={styles.confirmButton}
                      >
                        {savingId === item.id ? (
                          <ActivityIndicator size="small" color="#1A1305" />
                        ) : (
                          <Text style={styles.confirmButtonText}>Przyjmij kurs (ja)</Text>
                        )}
                      </Pressable>
                    )}
                    {item.status === "KIEROWCA_W_DRODZE" && isMine && (
                      <Pressable
                        onPress={() => handleLifecycleAction(item, "start")}
                        disabled={savingId === item.id}
                        style={styles.confirmButton}
                      >
                        {savingId === item.id ? (
                          <ActivityIndicator size="small" color="#1A1305" />
                        ) : (
                          <Text style={styles.confirmButtonText}>Rozpocznij kurs</Text>
                        )}
                      </Pressable>
                    )}
                    {item.status === "W_TRAKCIE" && isMine && (
                      <Pressable
                        onPress={() => handleLifecycleAction(item, "finish")}
                        disabled={savingId === item.id}
                        style={styles.confirmButton}
                      >
                        {savingId === item.id ? (
                          <ActivityIndicator size="small" color="#1A1305" />
                        ) : (
                          <Text style={styles.confirmButtonText}>Zakończ kurs</Text>
                        )}
                      </Pressable>
                    )}

                    {canEdit && (
                      <Pressable
                        onPress={() => handleCancel(item)}
                        disabled={savingId === item.id}
                        style={styles.cancelButton}
                      >
                        <Text style={styles.cancelButtonText}>Anuluj kurs</Text>
                      </Pressable>
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
  assignRow: { flexDirection: "row", gap: 8, flexWrap: "wrap" },
  row: { flexDirection: "row", gap: 8 },
  flex1: { flex: 1 },
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
  cancelButton: {
    borderWidth: 1,
    borderColor: colors.red,
    borderRadius: 9,
    paddingVertical: 12,
    alignItems: "center",
    marginTop: 8,
  },
  cancelButtonText: { color: colors.red, fontWeight: "700", fontSize: 14 },
  smallButton: {
    backgroundColor: colors.amber,
    borderRadius: 8,
    paddingVertical: 9,
    paddingHorizontal: 12,
    alignItems: "center",
  },
  smallButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 12.5 },
  smallButtonOutline: {
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 8,
    paddingVertical: 9,
    paddingHorizontal: 12,
    alignItems: "center",
  },
  smallButtonOutlineText: { color: colors.text, fontWeight: "600", fontSize: 12.5 },
  navButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 8,
    paddingVertical: 9,
    paddingHorizontal: 12,
  },
  navButtonIcon: { fontSize: 14 },
  errorBar: { padding: 12, backgroundColor: colors.panel2 },
  errorText: { color: colors.red, fontSize: 13, textAlign: "center" },
});
