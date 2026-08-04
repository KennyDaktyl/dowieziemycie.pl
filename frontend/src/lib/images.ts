import { publicApiBaseUrl } from "./api";

export function absoluteImageUrl(path: string): string {
  return path.startsWith("http") ? path : `${publicApiBaseUrl()}${path}`;
}
