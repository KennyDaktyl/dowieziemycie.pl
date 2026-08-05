// Registers the background location task at module load — must happen
// before anything else so a cold start triggered by the OS delivering a
// background location update still has the task defined.
import "@/lib/location-task";

import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

import { AuthProvider } from "@/lib/auth-context";
import { colors } from "@/lib/theme";

export default function RootLayout() {
  return (
    <AuthProvider>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="login" />
        <Stack.Screen name="(app)" />
        <Stack.Screen
          name="booking/[id]"
          options={{
            headerShown: true,
            headerStyle: { backgroundColor: colors.panel },
            headerTintColor: colors.text,
            headerTitleStyle: { fontSize: 15 },
            headerBackTitle: "Wstecz",
          }}
        />
      </Stack>
    </AuthProvider>
  );
}
