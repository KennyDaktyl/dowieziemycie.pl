import { Redirect } from "expo-router";
import { ActivityIndicator, View } from "react-native";

import { useAuth } from "@/lib/auth-context";

export default function Index() {
  const { driver, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#0B0F16" }}>
        <ActivityIndicator color="#F5A623" />
      </View>
    );
  }

  return <Redirect href={driver ? "/(app)/dashboard" : "/login"} />;
}
