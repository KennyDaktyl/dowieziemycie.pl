import { Ionicons } from "@expo/vector-icons";
import { Stack, useLocalSearchParams, useRouter } from "expo-router";
import { useEffect, useState, type ReactNode } from "react";
import {
  ActivityIndicator,
  Alert,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { BookingMap } from "@/components/BookingMap";
import { StatusBadge } from "@/components/StatusBadge";
import { apiFetch, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { bookingRef } from "@/lib/booking-ref";
import { bookingStatusInfo } from "@/lib/booking-status";
import { shortAddress } from "@/lib/format";
import { openNavigation } from "@/lib/navigation";
import { formatDateTime, formatDuration, paymentAmounts, paymentStatus } from "@/lib/payment";
import { siteLabel } from "@/lib/site";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

const DEFAULT_DEPOSIT_RATIO = 0.3;
const TERMINAL_STATUSES = ["ZAKONCZONA", "ANULOWANA"];

// Where to re-fetch this booking from after an action, or on a manual pull
// — matches whichever tab the driver came from, since a plain driver can't
// hit /bookings/all/ (dispatcher-only) but always has schedule/history.
const SOURCE_ENDPOINT: Record<string, string> = {
  "all-bookings": "/api/fleet/driver/bookings/all/",
  schedule: "/api/fleet/driver/schedule/",
  history: "/api/fleet/driver/bookings/history/",
};

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
  return Number.isNaN(d.getTime()) ? null : d.toISOString();
}

function Section({ title, icon, children }: { title: string; icon: keyof typeof Ionicons.glyphMap; children: ReactNode }) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Ionicons name={icon} size={15} color={colors.muted} />
        <Text style={styles.sectionTitle}>{title}</Text>
      </View>
      <View style={styles.sectionBody}>{children}</View>
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

export default function BookingDetailScreen() {
  const params = useLocalSearchParams<{ id: string; source: string; booking?: string }>();
  const router = useRouter();
  const { accessToken, driver, updateStatus } = useAuth();

  const [booking, setBooking] = useState<DriverBooking | null>(() => {
    try {
      return params.booking ? (JSON.parse(params.booking) as DriverBooking) : null;
    } catch {
      return null;
    }
  });
  const [showFullAddress, setShowFullAddress] = useState(false);
  const [editingDetails, setEditingDetails] = useState(false);
  const [editingPrice, setEditingPrice] = useState(false);
  const [priceText, setPriceText] = useState("");
  const [depositText, setDepositText] = useState("");
  const [depositManual, setDepositManual] = useState(false);
  const [detailEdit, setDetailEdit] = useState<{
    pickupAddress: string; dropoffAddress: string; passengerCount: string; dateText: string; timeText: string;
  } | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const endpoint = SOURCE_ENDPOINT[params.source] ?? SOURCE_ENDPOINT["all-bookings"];

  async function refetch() {
    try {
      const list = await apiFetch<DriverBooking[]>(endpoint, accessToken);
      const fresh = list.find((b) => String(b.id) === params.id);
      if (fresh) setBooking(fresh);
    } catch {
      // Keep showing whatever we already have — the initial params.booking
      // (or the last successful fetch) is still a reasonable read.
    }
  }

  useEffect(() => {
    refetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  // A brand-new booking always needs its price set before anything else
  // (confirm/lifecycle actions), so the price form pre-fills itself instead
  // of the dispatcher having to tap "Edytuj cenę" first.
  useEffect(() => {
    if (booking?.status === "NOWA" && !editingPrice) {
      setPriceText(booking.price ?? "");
      setDepositText(
        booking.deposit_amount ??
          (booking.price ? String(Math.round(Number(booking.price) * DEFAULT_DEPOSIT_RATIO)) : ""),
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [booking?.id, booking?.status]);

  if (!booking) {
    return (
      <SafeAreaView style={styles.screen}>
        <View style={styles.center}>
          <ActivityIndicator color={colors.amber} />
        </View>
      </SafeAreaView>
    );
  }

  const pickup =
    booking.pickup_lat && booking.pickup_lng
      ? { lat: Number(booking.pickup_lat), lng: Number(booking.pickup_lng) }
      : null;
  const dropoff =
    booking.dropoff_lat && booking.dropoff_lng
      ? { lat: Number(booking.dropoff_lat), lng: Number(booking.dropoff_lng) }
      : null;

  const status = bookingStatusInfo(booking.status);
  const payment = paymentStatus(booking);
  const amounts = paymentAmounts(booking);
  const actualDuration = formatDuration(booking.started_at, booking.completed_at);
  const canEdit = !TERMINAL_STATUSES.includes(booking.status);
  const isMine = driver != null && booking.assigned_driver_id === driver.id;
  const nextAction = NEXT_ACTION[booking.status];

  function startEditingDetails() {
    if (!booking) return;
    setDetailEdit({
      pickupAddress: booking.pickup_address,
      dropoffAddress: booking.dropoff_address,
      passengerCount: String(booking.passenger_count),
      ...toDateEditFields(booking.scheduled_at),
    });
    setEditingDetails(true);
  }

  function startEditingPrice() {
    if (!booking) return;
    setPriceText(booking.price ?? "");
    setDepositText(
      booking.deposit_amount ??
        (booking.price ? String(Math.round(Number(booking.price) * DEFAULT_DEPOSIT_RATIO)) : ""),
    );
    setDepositManual(false);
    setEditingPrice(true);
  }

  function onChangePrice(text: string) {
    setPriceText(text);
    if (depositManual) return;
    const price = parseFloat(text.replace(",", "."));
    if (Number.isFinite(price)) setDepositText(String(Math.round(price * DEFAULT_DEPOSIT_RATIO)));
  }

  async function handleConfirmOrSavePrice() {
    if (!booking) return;
    const price = parseFloat(priceText.replace(",", "."));
    const deposit = parseFloat(depositText.replace(",", "."));
    if (!Number.isFinite(price) || !Number.isFinite(deposit)) {
      setError("Podaj poprawną cenę i zaliczkę.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const isInitialConfirm = booking.status === "NOWA";
      await apiFetch(
        `/api/fleet/driver/bookings/${booking.id}/${isInitialConfirm ? "confirm" : "update"}/`,
        accessToken,
        { method: isInitialConfirm ? "POST" : "PATCH", body: JSON.stringify({ price, deposit_amount: deposit }) },
      );
      setEditingPrice(false);
      await refetch();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zapisać ceny.");
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveDetails() {
    if (!booking || !detailEdit) return;
    const passengerCount = parseInt(detailEdit.passengerCount, 10);
    const scheduledAt = parseDateEditFields(detailEdit.dateText, detailEdit.timeText);
    if (!scheduledAt) {
      setError("Podaj poprawną datę (DD.MM.RRRR) i godzinę (GG:MM).");
      return;
    }
    if (!Number.isFinite(passengerCount) || passengerCount < 1) {
      setError("Podaj poprawną liczbę pasażerów.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/update/`, accessToken, {
        method: "PATCH",
        body: JSON.stringify({
          pickup_address: detailEdit.pickupAddress,
          dropoff_address: detailEdit.dropoffAddress,
          passenger_count: passengerCount,
          scheduled_at: scheduledAt,
        }),
      });
      setEditingDetails(false);
      await refetch();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zapisać zmian.");
    } finally {
      setSaving(false);
    }
  }

  async function handleAssign(driverId: number | null) {
    if (!booking) return;
    setSaving(true);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/update/`, accessToken, {
        method: "PATCH",
        body: JSON.stringify({ assigned_driver_id: driverId }),
      });
      await refetch();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zmienić przypisania kierowcy.");
    } finally {
      setSaving(false);
    }
  }

  async function handleLifecycleAction(endpointName: string) {
    if (!booking) return;
    setSaving(true);
    setError(null);
    try {
      await apiFetch(`/api/fleet/driver/bookings/${booking.id}/${endpointName}/`, accessToken, { method: "POST" });
      if (endpointName in RESULTING_DRIVER_STATUS) {
        updateStatus(RESULTING_DRIVER_STATUS[endpointName as keyof typeof RESULTING_DRIVER_STATUS]);
      }
      if (endpointName === "finish") {
        router.back();
        return;
      }
      await refetch();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się zaktualizować kursu.");
    } finally {
      setSaving(false);
    }
  }

  function handleCancel() {
    if (!booking) return;
    Alert.alert(
      "Anulować kurs?",
      `${booking.pickup_address} → ${booking.dropoff_address}, ${formatDateTime(booking.scheduled_at)}. Klient dostanie SMS/e-mail o anulowaniu.`,
      [
        { text: "Nie", style: "cancel" },
        {
          text: "Tak, anuluj",
          style: "destructive",
          onPress: async () => {
            await handleLifecycleAction("cancel");
            router.back();
          },
        },
      ],
    );
  }

  return (
    <SafeAreaView style={styles.screen} edges={["bottom"]}>
      <Stack.Screen options={{ title: bookingRef(booking) }} />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.headerRow}>
          <Text style={styles.site}>{siteLabel(booking.site)}</Text>
          <StatusBadge label={status.label} tone={status.tone} />
        </View>
        <Text style={styles.title}>
          {shortAddress(booking.pickup_address)} → {shortAddress(booking.dropoff_address)}
        </Text>

        {/* Payment status — the single most important thing at a glance,
            always at the top as its own card, never mixed in with the
            lower-priority rows below. */}
        <View style={[styles.paymentCard, { borderColor: colors.line }]}>
          <View style={styles.paymentTop}>
            <Text style={styles.paymentAmount}>
              {booking.price ? `${Number(booking.price).toFixed(0)} zł` : "Wycena indywidualna"}
            </Text>
            <StatusBadge label={payment.label} tone={payment.tone} />
          </View>
          {amounts && (booking.paid_at || booking.remainder_paid_at) && (
            <View style={styles.paymentBreakdown}>
              <Text style={styles.paymentBreakdownText}>Zapłacono: {amounts.paid.toFixed(0)} zł</Text>
              {amounts.remaining > 0 && (
                <Text style={[styles.paymentBreakdownText, { color: colors.amber }]}>
                  Pozostało: {amounts.remaining.toFixed(0)} zł
                </Text>
              )}
            </View>
          )}
        </View>

        {/* Primary action — visible without scrolling on any phone size. */}
        {(pickup || dropoff) && (
          <View style={styles.navRow}>
            {pickup && (
              <Pressable onPress={() => openNavigation(pickup.lat, pickup.lng)} style={styles.navButton}>
                <Ionicons name="navigate" size={16} color="#1A1305" />
                <Text style={styles.navButtonText}>Do odbioru</Text>
              </Pressable>
            )}
            {dropoff && (
              <Pressable onPress={() => openNavigation(dropoff.lat, dropoff.lng)} style={styles.navButtonOutline}>
                <Ionicons name="flag" size={16} color={colors.text} />
                <Text style={styles.navButtonOutlineText}>Do celu</Text>
              </Pressable>
            )}
          </View>
        )}

        {nextAction && isMine && (
          <Pressable
            onPress={() => handleLifecycleAction(nextAction.endpoint)}
            disabled={saving}
            style={[styles.primaryButton, saving && styles.buttonDisabled]}
          >
            {saving ? (
              <ActivityIndicator size="small" color="#1A1305" />
            ) : (
              <>
                <Ionicons name={nextAction.icon} size={17} color="#1A1305" />
                <Text style={styles.primaryButtonText}>{nextAction.label}</Text>
              </>
            )}
          </Pressable>
        )}

        {pickup && <BookingMap pickup={pickup} dropoff={dropoff} height={190} />}

        <Section title="Klient" icon="person">
          <Row label="Imię" value={booking.customer_name || "—"} />
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Telefon</Text>
            <Pressable onPress={() => Linking.openURL(`tel:${booking.customer_phone}`)} style={styles.callButton}>
              <Ionicons name="call" size={14} color={colors.amber} />
              <Text style={styles.callButtonText}>{booking.customer_phone}</Text>
            </Pressable>
          </View>
        </Section>

        <Section title="Trasa" icon="map">
          <Pressable onPress={() => setShowFullAddress((v) => !v)}>
            <Row label="Skąd" value={showFullAddress ? booking.pickup_address : shortAddress(booking.pickup_address)} />
            <Row label="Dokąd" value={showFullAddress ? booking.dropoff_address : shortAddress(booking.dropoff_address)} />
            <Text style={styles.expandHint}>{showFullAddress ? "Pokaż skrócony adres" : "Pokaż pełny adres"}</Text>
          </Pressable>
          {booking.distance_km && <Row label="Dystans (planowany)" value={`${booking.distance_km} km`} />}
          {booking.actual_distance_km && <Row label="Dystans (przejechany)" value={`${booking.actual_distance_km} km`} />}
          {booking.duration_minutes && <Row label="Planowany czas zajętości" value={`${booking.duration_minutes} min`} />}
          {actualDuration && <Row label="Rzeczywisty czas kursu" value={actualDuration} />}
        </Section>

        <Section title="Szczegóły kursu" icon="information-circle">
          <Row label="Termin" value={formatDateTime(booking.scheduled_at)} />
          <Row label="Pasażerowie" value={String(booking.passenger_count)} />
          {booking.flight_number && <Row label="Numer lotu" value={booking.flight_number} />}
          {booking.started_at && <Row label="Rozpoczęcie" value={formatDateTime(booking.started_at)} />}
          {booking.completed_at && <Row label="Zakończenie" value={formatDateTime(booking.completed_at)} />}
          {booking.tracking_code && (
            <Row
              label="Kod śledzenia"
              value={`${booking.tracking_code} · ${formatDateTime(booking.tracking_code_valid_from)}–${formatDateTime(booking.tracking_code_expires_at)}`}
            />
          )}
          {driver?.is_dispatcher && <Row label="Kierowca" value={booking.assigned_driver_name || "Nieprzypisany"} />}
        </Section>

        {driver?.is_dispatcher && (
          <Section title="Narzędzia dyspozytora" icon="construct">
            {canEdit && (
              <View style={styles.buttonRow}>
                {!isMine && (
                  <Pressable onPress={() => handleAssign(driver.id)} disabled={saving} style={styles.smallButton}>
                    <Text style={styles.smallButtonText}>Przypisz do mnie</Text>
                  </Pressable>
                )}
                {booking.assigned_driver_id != null && (
                  <Pressable onPress={() => handleAssign(null)} disabled={saving} style={styles.smallButtonOutline}>
                    <Text style={styles.smallButtonOutlineText}>Odepnij kierowcę</Text>
                  </Pressable>
                )}
              </View>
            )}

            {editingDetails && detailEdit ? (
              <View style={styles.editForm}>
                <Text style={styles.editLabel}>Skąd</Text>
                <TextInput
                  value={detailEdit.pickupAddress}
                  onChangeText={(t) => setDetailEdit((p) => (p ? { ...p, pickupAddress: t } : p))}
                  style={styles.input}
                  placeholderTextColor={colors.muted}
                />
                <Text style={styles.editLabel}>Dokąd</Text>
                <TextInput
                  value={detailEdit.dropoffAddress}
                  onChangeText={(t) => setDetailEdit((p) => (p ? { ...p, dropoffAddress: t } : p))}
                  style={styles.input}
                  placeholderTextColor={colors.muted}
                />
                <View style={styles.editRow}>
                  <View style={styles.flex1}>
                    <Text style={styles.editLabel}>Data (DD.MM.RRRR)</Text>
                    <TextInput
                      value={detailEdit.dateText}
                      onChangeText={(t) => setDetailEdit((p) => (p ? { ...p, dateText: t } : p))}
                      placeholder="15.08.2026"
                      style={styles.input}
                      placeholderTextColor={colors.muted}
                    />
                  </View>
                  <View style={styles.flex1}>
                    <Text style={styles.editLabel}>Godzina (GG:MM)</Text>
                    <TextInput
                      value={detailEdit.timeText}
                      onChangeText={(t) => setDetailEdit((p) => (p ? { ...p, timeText: t } : p))}
                      placeholder="20:00"
                      style={styles.input}
                      placeholderTextColor={colors.muted}
                    />
                  </View>
                </View>
                <Text style={styles.editLabel}>Liczba pasażerów</Text>
                <TextInput
                  value={detailEdit.passengerCount}
                  onChangeText={(t) => setDetailEdit((p) => (p ? { ...p, passengerCount: t } : p))}
                  keyboardType="numeric"
                  style={styles.input}
                  placeholderTextColor={colors.muted}
                />
                <View style={styles.editRow}>
                  <Pressable onPress={() => setEditingDetails(false)} style={[styles.smallButtonOutline, styles.flex1]}>
                    <Text style={styles.smallButtonOutlineText}>Anuluj</Text>
                  </Pressable>
                  <Pressable onPress={handleSaveDetails} disabled={saving} style={[styles.smallButton, styles.flex1]}>
                    {saving ? <ActivityIndicator size="small" color="#1A1305" /> : <Text style={styles.smallButtonText}>Zapisz zmiany</Text>}
                  </Pressable>
                </View>
              </View>
            ) : (
              canEdit && (
                <Pressable onPress={startEditingDetails} style={styles.smallButtonOutline}>
                  <Text style={styles.smallButtonOutlineText}>Edytuj szczegóły kursu</Text>
                </Pressable>
              )
            )}

            {editingPrice || booking.status === "NOWA" ? (
              <View style={styles.editForm}>
                <Text style={styles.editLabel}>Cena kursu (zł)</Text>
                <TextInput
                  value={priceText}
                  onChangeText={onChangePrice}
                  keyboardType="numeric"
                  placeholder="np. 150"
                  placeholderTextColor={colors.muted}
                  style={styles.input}
                />
                <Text style={styles.editLabel}>Zaliczka (zł)</Text>
                <TextInput
                  value={depositText}
                  onChangeText={(t) => {
                    setDepositText(t);
                    setDepositManual(true);
                  }}
                  keyboardType="numeric"
                  placeholder="np. 45"
                  placeholderTextColor={colors.muted}
                  style={styles.input}
                />
                <View style={styles.editRow}>
                  {booking.status !== "NOWA" && (
                    <Pressable onPress={() => setEditingPrice(false)} style={[styles.smallButtonOutline, styles.flex1]}>
                      <Text style={styles.smallButtonOutlineText}>Anuluj</Text>
                    </Pressable>
                  )}
                  <Pressable onPress={handleConfirmOrSavePrice} disabled={saving} style={[styles.smallButton, styles.flex1]}>
                    {saving ? (
                      <ActivityIndicator size="small" color="#1A1305" />
                    ) : (
                      <Text style={styles.smallButtonText}>{booking.status === "NOWA" ? "Potwierdź kurs" : "Zapisz cenę"}</Text>
                    )}
                  </Pressable>
                </View>
              </View>
            ) : (
              <>
                <Row label="Zaliczka" value={booking.deposit_amount ? `${Number(booking.deposit_amount).toFixed(0)} zł` : "—"} />
                {canEdit && (
                  <Pressable onPress={startEditingPrice} style={styles.smallButtonOutline}>
                    <Text style={styles.smallButtonOutlineText}>Edytuj cenę i zaliczkę</Text>
                  </Pressable>
                )}
              </>
            )}

            {booking.status === "OPLACONA" && booking.assigned_driver_id == null && (
              <Pressable onPress={() => handleLifecycleAction("accept")} disabled={saving} style={styles.primaryButton}>
                {saving ? <ActivityIndicator size="small" color="#1A1305" /> : <Text style={styles.primaryButtonText}>Przyjmij kurs (ja)</Text>}
              </Pressable>
            )}

            {canEdit && (
              <Pressable onPress={handleCancel} disabled={saving} style={styles.cancelButton}>
                <Ionicons name="close-circle" size={16} color={colors.red} />
                <Text style={styles.cancelButtonText}>Anuluj kurs</Text>
              </Pressable>
            )}
          </Section>
        )}

        {error && <Text style={styles.error}>{error}</Text>}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  content: { padding: 16, gap: 14, paddingBottom: 40 },
  headerRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  site: { color: colors.muted, fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.5 },
  title: { color: colors.text, fontSize: 17, fontWeight: "700" },
  paymentCard: {
    backgroundColor: colors.panel,
    borderRadius: 14,
    borderWidth: 1,
    padding: 16,
    gap: 10,
  },
  paymentTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 },
  paymentAmount: { color: colors.text, fontSize: 26, fontWeight: "800" },
  paymentBreakdown: { flexDirection: "row", gap: 16, borderTopWidth: 1, borderTopColor: colors.line, paddingTop: 10 },
  paymentBreakdownText: { color: colors.muted, fontSize: 13, fontWeight: "600" },
  navRow: { flexDirection: "row", gap: 8 },
  navButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    backgroundColor: colors.amber,
    borderRadius: 10,
    paddingVertical: 13,
  },
  navButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 14.5 },
  navButtonOutline: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 10,
    paddingVertical: 13,
  },
  navButtonOutlineText: { color: colors.text, fontWeight: "700", fontSize: 14.5 },
  primaryButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    backgroundColor: colors.amber,
    borderRadius: 10,
    paddingVertical: 14,
  },
  primaryButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 15 },
  buttonDisabled: { opacity: 0.6 },
  section: {
    backgroundColor: colors.panel,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.line,
    overflow: "hidden",
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 7,
    paddingHorizontal: 14,
    paddingVertical: 11,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
    backgroundColor: colors.panel2,
  },
  sectionTitle: { color: colors.muted, fontSize: 11.5, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.5 },
  sectionBody: { padding: 14, gap: 10 },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", gap: 8 },
  rowLabel: { color: colors.muted, fontSize: 13 },
  rowValue: { color: colors.text, fontSize: 13.5, fontWeight: "600", flexShrink: 1, textAlign: "right" },
  expandHint: { color: colors.amber, fontSize: 11.5, fontWeight: "600", marginTop: 2 },
  callButton: { flexDirection: "row", alignItems: "center", gap: 5 },
  callButtonText: { color: colors.amber, fontSize: 13.5, fontWeight: "700" },
  buttonRow: { flexDirection: "row", gap: 8, flexWrap: "wrap" },
  editForm: { gap: 8 },
  editRow: { flexDirection: "row", gap: 8 },
  editLabel: { color: colors.muted, fontSize: 12, fontWeight: "600", marginTop: 2 },
  flex1: { flex: 1 },
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
  smallButton: { backgroundColor: colors.amber, borderRadius: 8, paddingVertical: 10, paddingHorizontal: 12, alignItems: "center" },
  smallButtonText: { color: "#1A1305", fontWeight: "700", fontSize: 12.5 },
  smallButtonOutline: { borderWidth: 1, borderColor: colors.line, borderRadius: 8, paddingVertical: 10, paddingHorizontal: 12, alignItems: "center" },
  smallButtonOutlineText: { color: colors.text, fontWeight: "600", fontSize: 12.5 },
  cancelButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 6,
    borderWidth: 1,
    borderColor: colors.red,
    borderRadius: 9,
    paddingVertical: 12,
  },
  cancelButtonText: { color: colors.red, fontWeight: "700", fontSize: 14 },
  error: { color: colors.red, fontSize: 13, textAlign: "center" },
});
