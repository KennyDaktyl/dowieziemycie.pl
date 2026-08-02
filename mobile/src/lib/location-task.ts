import * as Location from "expo-location";
import * as TaskManager from "expo-task-manager";

import { API_BASE_URL } from "./api";
import { getAccessToken } from "./session";

export const LOCATION_TASK_NAME = "dowieziemycie-driver-location";

// GPS coords come back as raw JS floats with full double-precision noise
// (e.g. 50.06139500000001) — the backend's DecimalField(max_digits=9,
// decimal_places=6) rejects that as "too many digits". Round to 6 decimal
// places (~11cm accuracy, already far more precise than needed) before
// sending, matching the backend's own precision.
export function round6(value: number): number {
  return Math.round(value * 1e6) / 1e6;
}

// Must be defined at module top level so it re-registers on a cold start
// triggered by the OS delivering a background location update — this
// module is imported once from app/_layout.tsx specifically to guarantee
// that happens before anything else runs.
TaskManager.defineTask(LOCATION_TASK_NAME, async ({ data, error }) => {
  if (error) return;
  const { locations } = (data ?? {}) as { locations?: Location.LocationObject[] };
  const latest = locations?.[locations.length - 1];
  if (!latest) return;

  const token = await getAccessToken();
  if (!token) return;

  try {
    await fetch(`${API_BASE_URL}/api/fleet/driver/position/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ lat: round6(latest.coords.latitude), lng: round6(latest.coords.longitude) }),
    });
  } catch {
    // Dropped silently — the next tick (in ~10s) reports a fresher position
    // anyway, no point retrying a stale one.
  }
});

export async function requestLocationPermissions(): Promise<void> {
  const fg = await Location.requestForegroundPermissionsAsync();
  if (fg.status !== "granted") {
    throw new Error("Brak zgody na dostęp do lokalizacji.");
  }
  const bg = await Location.requestBackgroundPermissionsAsync();
  if (bg.status !== "granted") {
    throw new Error("Brak zgody na dostęp do lokalizacji w tle — włącz „Zawsze zezwalaj” w ustawieniach.");
  }
}

export async function startBackgroundTracking(): Promise<void> {
  const alreadyRunning = await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK_NAME);
  if (alreadyRunning) return;

  await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
    accuracy: Location.Accuracy.High,
    timeInterval: 10000,
    distanceInterval: 0,
    pausesUpdatesAutomatically: false,
    foregroundService: {
      notificationTitle: "dowieziemycie.pl — kierowca",
      notificationBody: "Udostępniasz swoją pozycję klientom.",
    },
  });
}

export async function stopBackgroundTracking(): Promise<void> {
  const alreadyRunning = await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK_NAME);
  if (alreadyRunning) {
    await Location.stopLocationUpdatesAsync(LOCATION_TASK_NAME);
  }
}

export async function isTrackingActive(): Promise<boolean> {
  return Location.hasStartedLocationUpdatesAsync(LOCATION_TASK_NAME);
}
