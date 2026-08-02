import { ImageResponse } from "next/og";

import { VanGlyph } from "@/lib/site-icon";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default function Icon() {
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
          borderRadius: 7,
        }}
      >
        <VanGlyph scale={0.85} />
      </div>
    ),
    { ...size },
  );
}
