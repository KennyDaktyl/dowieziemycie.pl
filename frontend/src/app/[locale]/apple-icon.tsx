import { ImageResponse } from "next/og";

import { VanGlyph } from "@/lib/site-icon";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f5a623",
        }}
      >
        <VanGlyph scale={4.6} />
      </div>
    ),
    { ...size },
  );
}
