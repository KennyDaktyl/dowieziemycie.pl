import { ImageResponse } from "next/og";

import { BrandOgImage, OG_SIZE } from "@/lib/site-og";

export const size = OG_SIZE;
export const contentType = "image/png";

export default function TwitterImage() {
  return new ImageResponse(<BrandOgImage />, { ...size });
}
