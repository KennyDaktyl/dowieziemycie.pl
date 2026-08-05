import type { ReactNode } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { bookingRef } from "@/lib/booking-ref";
import { bookingStatusInfo } from "@/lib/booking-status";
import { shortAddress } from "@/lib/format";
import { siteLabel } from "@/lib/site";
import { colors } from "@/lib/theme";
import type { DriverBooking } from "@/lib/types";

import { BookingMap } from "./BookingMap";
import { StatusBadge } from "./StatusBadge";

const ACTIVE_STATUSES = ["KIEROWCA_W_DRODZE", "W_TRAKCIE"];

/** One shared card for every booking list (Szef/Moje kursy/Historia/Wolne
 * kursy) — price and status used to be styled identically to every other
 * field on the card (same font size/weight as a "Rzeczywisty czas kursu"
 * row), making it hard to tell at a glance what mattered. Price is now the
 * single largest, boldest thing on the card; status is always a filled,
 * color-coded pill instead of the old uniformly-amber outline. A live map
 * thumbnail only renders for a booking actually in progress (en route/
 * mid-ride) — showing one on every archived card was pure visual noise. */
export function BookingCard({
  booking,
  onPress,
  footer,
}: {
  booking: DriverBooking;
  onPress?: () => void;
  footer?: ReactNode;
}) {
  const status = bookingStatusInfo(booking.status);
  const showMap =
    ACTIVE_STATUSES.includes(booking.status) && booking.pickup_lat != null && booking.pickup_lng != null;

  const content = (
    <>
      <View style={styles.header}>
        <Text style={styles.site}>
          {siteLabel(booking.site)} · {bookingRef(booking)}
        </Text>
        <StatusBadge label={status.label} tone={status.tone} size="sm" />
      </View>
      <Text style={styles.route}>
        {shortAddress(booking.pickup_address)} → {shortAddress(booking.dropoff_address)}
      </Text>
      <Text style={styles.meta}>
        {new Date(booking.scheduled_at).toLocaleString("pl-PL", {
          day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
        })}
        {" · "}
        {booking.customer_name || booking.customer_phone}
        {" · "}
        {booking.passenger_count} os.
      </Text>
      <Text style={styles.price}>{booking.price ? `${Number(booking.price).toFixed(0)} zł` : "Wycena indywidualna"}</Text>
      {showMap && (
        <View style={styles.mapWrap}>
          <BookingMap
            pickup={{ lat: Number(booking.pickup_lat), lng: Number(booking.pickup_lng) }}
            dropoff={
              booking.dropoff_lat && booking.dropoff_lng
                ? { lat: Number(booking.dropoff_lat), lng: Number(booking.dropoff_lng) }
                : null
            }
            height={110}
          />
        </View>
      )}
      {footer}
    </>
  );

  if (!onPress) return <View style={styles.card}>{content}</View>;
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}>
      {content}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.panel,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 16,
    gap: 4,
  },
  cardPressed: { opacity: 0.85 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 8 },
  site: { color: colors.muted, fontSize: 11, fontWeight: "700", textTransform: "uppercase", letterSpacing: 0.5 },
  route: { color: colors.text, fontSize: 15.5, fontWeight: "700", marginTop: 4 },
  meta: { color: colors.muted, fontSize: 12.5, marginTop: 2 },
  price: { color: colors.text, fontSize: 20, fontWeight: "800", marginTop: 8 },
  mapWrap: { marginTop: 10 },
});
