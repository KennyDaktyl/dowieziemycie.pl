import type { ReactNode } from "react";
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { bookingRef } from "@/lib/booking-ref";
import { openNavigation } from "@/lib/navigation";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

import { BookingMap } from "./BookingMap";

function formatDateTime(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("pl-PL", {
    day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

export function formatDuration(startedAt: string | null, completedAt: string | null): string | null {
  if (!startedAt || !completedAt) return null;
  const minutes = Math.round((new Date(completedAt).getTime() - new Date(startedAt).getTime()) / 60000);
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h} godz. ${m} min` : `${m} min`;
}

export function paymentStatusLabel(booking: DriverBooking): string {
  if (booking.remainder_paid_at) return "Opłacony w całości";
  if (booking.paid_at) return "Zapłacona zaliczka";
  return "Nieopłacony";
}

/** How much has actually landed vs. what's still owed — the driver needs
 * real numbers here, not just a status label, since they're often the one
 * collecting the remainder in person at the end of the ride. */
export function paymentAmounts(booking: DriverBooking): { paid: number; remaining: number } | null {
  if (booking.price == null) return null;
  const price = Number(booking.price);
  if (booking.remainder_paid_at) return { paid: price, remaining: 0 };
  if (booking.paid_at && booking.deposit_amount != null) {
    const deposit = Number(booking.deposit_amount);
    return { paid: deposit, remaining: Math.max(price - deposit, 0) };
  }
  return { paid: 0, remaining: price };
}

interface Row {
  label: string;
  value: string;
}

/** Full-detail read view for a booking — the "wejście w szczegóły" the
 * Harmonogram/Historia tabs were missing entirely (cards weren't even
 * tappable before). Shows the same road-route map as the websites, plus
 * everything a driver needs about a specific ride. `children` is for the
 * caller's own action buttons (start/finish/etc.), since which actions make
 * sense depends on which tab opened this. */
export function BookingDetailModal({
  booking,
  onClose,
  children,
}: {
  booking: DriverBooking | null;
  onClose: () => void;
  children?: ReactNode;
}) {
  if (!booking) return null;

  const pickup =
    booking.pickup_lat && booking.pickup_lng
      ? { lat: Number(booking.pickup_lat), lng: Number(booking.pickup_lng) }
      : null;
  const dropoff =
    booking.dropoff_lat && booking.dropoff_lng
      ? { lat: Number(booking.dropoff_lat), lng: Number(booking.dropoff_lng) }
      : null;

  const actualDuration = formatDuration(booking.started_at, booking.completed_at);
  const amounts = paymentAmounts(booking);

  const rows: Row[] = [
    { label: "Klient", value: booking.customer_name || "—" },
    { label: "Telefon", value: booking.customer_phone },
    { label: "Termin", value: formatDateTime(booking.scheduled_at) },
    { label: "Pasażerowie", value: String(booking.passenger_count) },
    ...(booking.flight_number ? [{ label: "Numer lotu", value: booking.flight_number }] : []),
    { label: "Cena", value: booking.price ? `${Number(booking.price).toFixed(0)} zł` : "Wycena indywidualna" },
    { label: "Płatność", value: paymentStatusLabel(booking) },
  ];
  if (amounts) {
    rows.push({ label: "Zapłacono", value: `${amounts.paid.toFixed(0)} zł` });
    if (amounts.remaining > 0) rows.push({ label: "Pozostało do zapłaty", value: `${amounts.remaining.toFixed(0)} zł` });
  }
  if (booking.distance_km) rows.push({ label: "Dystans (planowany)", value: `${booking.distance_km} km` });
  if (booking.actual_distance_km) rows.push({ label: "Dystans (przejechany)", value: `${booking.actual_distance_km} km` });
  if (booking.duration_minutes) rows.push({ label: "Planowany czas zajętości", value: `${booking.duration_minutes} min` });
  if (actualDuration) rows.push({ label: "Rzeczywisty czas kursu", value: actualDuration });
  if (booking.started_at) rows.push({ label: "Rozpoczęcie", value: formatDateTime(booking.started_at) });
  if (booking.completed_at) rows.push({ label: "Zakończenie", value: formatDateTime(booking.completed_at) });

  return (
    <Modal visible transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.backdrop}>
        <View style={styles.sheet}>
          <View style={styles.header}>
            <View style={{ flex: 1 }}>
              <Text style={styles.ref}>{bookingRef(booking)}</Text>
              <Text style={styles.title}>
                {booking.pickup_address} → {booking.dropoff_address}
              </Text>
            </View>
            <Pressable onPress={onClose} hitSlop={12}>
              <Text style={styles.close}>Zamknij</Text>
            </Pressable>
          </View>
          <ScrollView contentContainerStyle={styles.content}>
            {pickup && <BookingMap pickup={pickup} dropoff={dropoff} height={200} />}
            <View style={styles.navRow}>
              {pickup && (
                <Pressable onPress={() => openNavigation(pickup.lat, pickup.lng)} style={styles.navButton}>
                  <Text style={styles.navButtonIcon}>📍</Text>
                  <Text style={styles.navButtonText}>Nawiguj do odbioru</Text>
                </Pressable>
              )}
              {dropoff && (
                <Pressable onPress={() => openNavigation(dropoff.lat, dropoff.lng)} style={styles.navButton}>
                  <Text style={styles.navButtonIcon}>🏁</Text>
                  <Text style={styles.navButtonText}>Nawiguj do celu</Text>
                </Pressable>
              )}
            </View>
            <View style={styles.rows}>
              {rows.map((row) => (
                <View key={row.label} style={styles.row}>
                  <Text style={styles.label}>{row.label}</Text>
                  <Text style={styles.value}>{row.value}</Text>
                </View>
              ))}
            </View>
            {children}
          </ScrollView>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: "rgba(0,0,0,0.55)", justifyContent: "flex-end" },
  sheet: {
    backgroundColor: colors.bg,
    borderTopLeftRadius: 18,
    borderTopRightRadius: 18,
    maxHeight: "88%",
    borderWidth: 1,
    borderColor: colors.line,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: 12,
    padding: 18,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  ref: { color: colors.amber, fontSize: 11.5, fontWeight: "700", letterSpacing: 0.3, marginBottom: 2 },
  title: { color: colors.text, fontSize: 16, fontWeight: "700" },
  close: { color: colors.amber, fontSize: 14, fontWeight: "700" },
  content: { padding: 18, gap: 14 },
  navRow: { flexDirection: "row", gap: 8, flexWrap: "wrap" },
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
  navButtonText: { color: colors.text, fontWeight: "600", fontSize: 12.5 },
  rows: { gap: 10 },
  row: { flexDirection: "row", justifyContent: "space-between", gap: 8 },
  label: { color: colors.muted, fontSize: 13 },
  value: { color: colors.text, fontSize: 13, fontWeight: "600", flexShrink: 1, textAlign: "right" },
});
