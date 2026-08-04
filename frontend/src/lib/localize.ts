import type { AppLocale } from "@/i18n/routing";

export function localize<T extends object>(obj: T, field: string, locale: AppLocale): string {
  const values = obj as Record<string, unknown>;
  const value = values[`${field}_${locale}`];
  if (typeof value === "string" && value.trim() !== "") return value;
  return String(values[`${field}_pl`] ?? "");
}
