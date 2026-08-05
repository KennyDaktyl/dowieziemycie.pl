import type { BottomTabBarProps } from "expo-router/tabs";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { colors } from "@/lib/theme";

// Standard bottom tab bar sits right where Android's gesture bar / 3-button
// nav lives, so the two fight for the same taps — moving it to the top of
// the screen (below the status bar/notch) avoids that entirely, at the cost
// of not being the platform-conventional position.
export function TopTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.wrap, { paddingTop: insets.top }]}>
      <View style={styles.row}>
        {state.routes.map((route, index) => {
          const { options } = descriptors[route.key];
          // Expo Router hides a tab from the bar via options.href === null
          // (used here so a non-dispatcher driver never sees "Szef") — not
          // part of the plain BottomTabNavigationOptions type this map is
          // typed with, but still present on the actual object at runtime.
          if ((options as { href?: string | null }).href === null) return null;

          const focused = state.index === index;
          const color = focused ? colors.amber : colors.muted;
          const label = options.title ?? route.name;

          function onPress() {
            const event = navigation.emit({ type: "tabPress", target: route.key, canPreventDefault: true });
            if (!focused && !event.defaultPrevented) {
              navigation.navigate(route.name, route.params);
            }
          }

          return (
            <Pressable key={route.key} onPress={onPress} style={styles.tab}>
              {options.tabBarIcon?.({ focused, color, size: 22 })}
              <Text numberOfLines={1} style={[styles.label, { color }]}>
                {label}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

export const TOP_TAB_BAR_CONTENT_HEIGHT = 54;

const styles = StyleSheet.create({
  wrap: {
    // Absolute + pinned to the top, rather than relying on wherever
    // BottomTabView would otherwise place a tabBar child in its own layout
    // (bottom, by default) — this is the one reliable way to guarantee it
    // renders at the top regardless of the navigator's internal ordering.
    // Screens reserve matching top padding via sceneStyle (see
    // app/(app)/_layout.tsx) so content never renders underneath it.
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
    backgroundColor: colors.panel,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  row: {
    flexDirection: "row",
    height: 54,
  },
  tab: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 2,
    paddingHorizontal: 2,
  },
  label: {
    fontSize: 10.5,
    fontWeight: "600",
  },
});
