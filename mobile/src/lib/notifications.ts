import Constants from "expo-constants";
import * as Notifications from "expo-notifications";

import { apiFetch } from "./api";
import { getAccessToken } from "./session";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldPlaySound: false,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

/** Requests permission (if needed) and registers the device's Expo push
 * token on the logged-in driver, so new-booking alerts reach this phone. */
export async function registerForPushNotifications(): Promise<void> {
  const existing = await Notifications.getPermissionsAsync();
  let status = existing.status;
  if (status !== "granted") {
    const requested = await Notifications.requestPermissionsAsync();
    status = requested.status;
  }
  if (status !== "granted") return;

  const projectId = Constants.expoConfig?.extra?.eas?.projectId as string | undefined;
  const pushToken = await Notifications.getExpoPushTokenAsync(projectId ? { projectId } : undefined);

  const accessToken = await getAccessToken();
  if (!accessToken) return;

  await apiFetch("/api/fleet/driver/push-token/", accessToken, {
    method: "POST",
    body: JSON.stringify({ expo_push_token: pushToken.data }),
  });
}
