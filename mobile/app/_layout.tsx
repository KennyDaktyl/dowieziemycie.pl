// Registers the background location task at module load — must happen
// before anything else so a cold start triggered by the OS delivering a
// background location update still has the task defined.
import "@/lib/location-task";

import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

import { AuthProvider } from "@/lib/auth-context";

export default function RootLayout() {
  return (
    <AuthProvider>
      <StatusBar style="light" />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="login" />
        <Stack.Screen name="(app)" />
      </Stack>
    </AuthProvider>
  );
}
