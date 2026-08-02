import { Redirect, Tabs } from "expo-router";

import { useAuth } from "@/lib/auth-context";
import { colors } from "@/lib/theme";

export default function AppLayout() {
  const { driver, loading } = useAuth();

  if (loading) return null;
  if (!driver) return <Redirect href="/login" />;

  return (
    <Tabs
      screenOptions={{
        headerStyle: { backgroundColor: colors.panel },
        headerTintColor: colors.text,
        tabBarStyle: { backgroundColor: colors.panel, borderTopColor: colors.line },
        tabBarActiveTintColor: colors.amber,
        tabBarInactiveTintColor: colors.muted,
      }}
    >
      <Tabs.Screen name="dashboard" options={{ title: "Panel" }} />
      <Tabs.Screen name="bookings" options={{ title: "Kursy" }} />
      <Tabs.Screen name="schedule" options={{ title: "Harmonogram" }} />
      <Tabs.Screen name="history" options={{ title: "Historia" }} />
    </Tabs>
  );
}
