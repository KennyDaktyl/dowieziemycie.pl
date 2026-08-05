import { Ionicons } from "@expo/vector-icons";
import { Redirect, Tabs } from "expo-router";
import type { ColorValue } from "react-native";

import { useAuth } from "@/lib/auth-context";
import { colors } from "@/lib/theme";

type IconName = keyof typeof Ionicons.glyphMap;

function TabIcon({ name, color, focused }: { name: IconName; color: ColorValue; focused: boolean }) {
  return <Ionicons name={focused ? name : (`${name}-outline` as IconName)} size={24} color={color as string} />;
}

export default function AppLayout() {
  const { driver, loading } = useAuth();

  if (loading) return null;
  if (!driver) return <Redirect href="/login" />;

  return (
    <Tabs
      screenOptions={{
        headerStyle: { backgroundColor: colors.panel },
        headerTintColor: colors.text,
        tabBarStyle: { backgroundColor: colors.panel, borderTopColor: colors.line, height: 58, paddingBottom: 6, paddingTop: 6 },
        tabBarActiveTintColor: colors.amber,
        tabBarInactiveTintColor: colors.muted,
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
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
