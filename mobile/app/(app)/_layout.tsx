import { Ionicons } from "@expo/vector-icons";
import { Redirect, Tabs } from "expo-router";
import type { ColorValue } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { TopTabBar, TOP_TAB_BAR_CONTENT_HEIGHT } from "@/components/TopTabBar";
import { useAuth } from "@/lib/auth-context";

type IconName = keyof typeof Ionicons.glyphMap;

function TabIcon({ name, color, focused }: { name: IconName; color: ColorValue; focused: boolean }) {
  return <Ionicons name={focused ? name : (`${name}-outline` as IconName)} size={24} color={color as string} />;
}

export default function AppLayout() {
  const { driver, loading } = useAuth();
  const insets = useSafeAreaInsets();

  if (loading) return null;
  if (!driver) return <Redirect href="/login" />;

  return (
    <Tabs
      tabBar={(props) => <TopTabBar {...props} />}
      screenOptions={{
        // The native per-screen header used to show the screen title above
        // a bottom tab bar — now that TopTabBar itself sits at the top and
        // already highlights the active tab's own label, a separate header
        // would just duplicate that (and stacking both would need exact
        // native header height math to avoid overlapping TopTabBar).
        headerShown: false,
        // Reserves space at the top of every screen for the absolutely-
        // positioned TopTabBar (see that file) instead of content rendering
        // underneath it.
        sceneStyle: { paddingTop: insets.top + TOP_TAB_BAR_CONTENT_HEIGHT },
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: "Panel",
          tabBarIcon: ({ color, focused }) => <TabIcon name="home" color={color} focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="bookings"
        options={{
          title: "Wolne kursy",
          tabBarIcon: ({ color, focused }) => <TabIcon name="list" color={color} focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="schedule"
        options={{
          title: "Moje kursy",
          tabBarIcon: ({ color, focused }) => <TabIcon name="briefcase" color={color} focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="history"
        options={{
          title: "Historia",
          tabBarIcon: ({ color, focused }) => <TabIcon name="time" color={color} focused={focused} />,
        }}
      />
      <Tabs.Screen
        name="all-bookings"
        options={{
          title: "Szef",
          href: driver.is_dispatcher ? undefined : null,
          tabBarIcon: ({ color, focused }) => <TabIcon name="star" color={color} focused={focused} />,
        }}
      />
    </Tabs>
  );
}
