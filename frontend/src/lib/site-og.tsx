import { VanGlyph } from "./site-icon";

export const OG_SIZE = { width: 1200, height: 630 };

export function BrandOgImage() {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        padding: "80px 96px",
        background: "linear-gradient(135deg, #0b0f16 0%, #1a2530 100%)",
        color: "#edeef2",
        fontFamily: "sans-serif",
      }}
    >
      <div style={{ display: "flex", fontSize: 30, fontWeight: 600, color: "#f5a623", letterSpacing: 2 }}>
        KRAKÓW I OKOLICE
      </div>
      <div style={{ display: "flex", fontSize: 92, fontWeight: 700, marginTop: 18, lineHeight: 1 }}>
        dowieziemycie.pl
      </div>
      <div style={{ display: "flex", fontSize: 34, marginTop: 26, opacity: 0.85 }}>
        Twój sąsiad z busem — dowóz, gdy go potrzebujesz
      </div>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginTop: 68,
          width: 132,
          height: 132,
          borderRadius: 28,
          background: "#f5a623",
        }}
      >
        <VanGlyph scale={3.2} />
      </div>
    </div>
  );
}
