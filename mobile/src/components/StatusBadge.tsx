import { StyleSheet, Text, View } from "react-native";

import { statusTone, type StatusTone } from "@/lib/theme";

/** Filled, colored pill — the "wyraźne, wypełnione kolorem badge'e" the
 * redesign asked for, replacing the old outlined-in-amber-regardless-of-
 * status badge used everywhere before. */
export function StatusBadge({ label, tone, size = "md" }: { label: string; tone: StatusTone; size?: "sm" | "md" }) {
  const { fg, bg } = statusTone[tone];
  return (
    <View style={[styles.badge, size === "sm" && styles.badgeSm, { backgroundColor: bg }]}>
      <View style={[styles.dot, { backgroundColor: fg }]} />
      <Text style={[styles.text, size === "sm" && styles.textSm, { color: fg }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 5,
    alignSelf: "flex-start",
  },
  badgeSm: { paddingHorizontal: 8, paddingVertical: 4 },
  dot: { width: 6, height: 6, borderRadius: 3 },
  text: { fontSize: 12, fontWeight: "700" },
  textSm: { fontSize: 11 },
});
