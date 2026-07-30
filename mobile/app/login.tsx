import { Redirect } from "expo-router";
import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { colors } from "@/lib/theme";

export default function LoginScreen() {
  const { driver, login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (driver) {
    return <Redirect href="/(app)/dashboard" />;
  }

  async function handleSubmit() {
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Nie udało się połączyć z serwerem.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.screen}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.flex}
      >
        <View style={styles.content}>
          <View style={styles.brand}>
            <View style={styles.dot} />
            <Text style={styles.brandText}>
              dowieziemycie<Text style={{ color: colors.amber }}>.pl</Text>
            </Text>
          </View>
          <Text style={styles.subtitle}>Panel kierowcy</Text>

          <View style={styles.card}>
            <Text style={styles.label}>LOGIN</Text>
            <TextInput
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              autoCorrect={false}
              style={styles.input}
              placeholderTextColor={colors.muted}
            />
            <Text style={[styles.label, { marginTop: 14 }]}>HASŁO</Text>
            <TextInput
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              style={styles.input}
              placeholderTextColor={colors.muted}
            />

            {error && <Text style={styles.error}>{error}</Text>}

            <Pressable
              onPress={handleSubmit}
              disabled={loading || !username || !password}
              style={({ pressed }) => [
                styles.button,
                (loading || !username || !password) && styles.buttonDisabled,
                pressed && { opacity: 0.85 },
              ]}
            >
              {loading ? <ActivityIndicator color="#1A1305" /> : <Text style={styles.buttonText}>Zaloguj się</Text>}
            </Pressable>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.bg },
  flex: { flex: 1 },
  content: { flex: 1, justifyContent: "center", paddingHorizontal: 24 },
  brand: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, marginBottom: 4 },
  dot: { width: 9, height: 9, borderRadius: 5, backgroundColor: colors.amber },
  brandText: { color: colors.text, fontSize: 22, fontWeight: "700" },
  subtitle: { color: colors.muted, textAlign: "center", marginBottom: 32, fontSize: 13, letterSpacing: 1 },
  card: { backgroundColor: colors.panel, borderRadius: 14, borderWidth: 1, borderColor: colors.line, padding: 22 },
  label: { color: colors.muted, fontSize: 11, fontWeight: "600", letterSpacing: 1, marginBottom: 6 },
  input: {
    backgroundColor: colors.panel2,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.line,
    color: colors.text,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
  },
  error: { color: colors.red, fontSize: 13, marginTop: 14, textAlign: "center" },
  button: {
    backgroundColor: colors.amber,
    borderRadius: 9,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 22,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: "#1A1305", fontWeight: "700", fontSize: 15 },
});
