/** Shared van glyph for favicon/apple-icon — a minimal flat pictograph
 * (rounded body + cab + two wheels) matching the "Twój sąsiad z busem"
 * brand, built from plain CSS shapes since Satori (next/og) can't render
 * arbitrary raster art. */
export function VanGlyph({ scale }: { scale: number }) {
  const bodyW = 20 * scale;
  const bodyH = 11 * scale;
  const cabW = 7 * scale;
  const wheel = 4.6 * scale;

  return (
    <div style={{ display: "flex", alignItems: "flex-end", position: "relative" }}>
      <div
        style={{
          display: "flex",
          width: bodyW,
          height: bodyH,
          background: "#edeef2",
          borderRadius: 2.5 * scale,
        }}
      />
      <div
        style={{
          display: "flex",
          position: "absolute",
          right: 1.5 * scale,
          top: -3 * scale,
          width: cabW,
          height: bodyH * 0.62,
          background: "#edeef2",
          borderTopLeftRadius: 1.5 * scale,
          borderTopRightRadius: 2.5 * scale,
        }}
      />
      <div
        style={{
          display: "flex",
          position: "absolute",
          left: 3 * scale,
          bottom: -2.4 * scale,
          width: wheel,
          height: wheel,
          borderRadius: wheel,
          background: "#0b0f16",
        }}
      />
      <div
        style={{
          display: "flex",
          position: "absolute",
          right: 3 * scale,
          bottom: -2.4 * scale,
          width: wheel,
          height: wheel,
          borderRadius: wheel,
          background: "#0b0f16",
        }}
      />
    </div>
  );
}
