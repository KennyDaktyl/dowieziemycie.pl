// Mirrors the website's palette (frontend/src/app/[locale]/globals.css).
export const colors = {
  bg: "#0B0F16",
  panel: "#121A24",
  panel2: "#1A2530",
  amber: "#F5A623",
  green: "#3ECF8E",
  red: "#E5484D",
  blue: "#4EA1F5",
  text: "#EDEEF2",
  muted: "#8B96A3",
  line: "rgba(237, 238, 242, 0.14)",
  // Soft, low-opacity tints of the status colors above — used as a filled
  // badge/chip background so the badge reads as a solid shape at a glance
  // instead of just colored text sitting on the same panel background as
  // everything else (the "everything looks the same" flatness this
  // redesign is fixing).
  amberSoft: "rgba(245, 166, 35, 0.16)",
  greenSoft: "rgba(62, 207, 142, 0.16)",
  redSoft: "rgba(229, 72, 77, 0.16)",
  blueSoft: "rgba(78, 161, 245, 0.16)",
};

/** Status color families used across booking status badges, payment status
 * cards, and the driver status picker — green = paid/ready, amber =
 * pending/in progress, red = problem/unpaid, blue = informational. Central
 * so every screen picks the same color for the same meaning. */
export const statusTone = {
  green: { fg: colors.green, bg: colors.greenSoft },
  amber: { fg: colors.amber, bg: colors.amberSoft },
  red: { fg: colors.red, bg: colors.redSoft },
  blue: { fg: colors.blue, bg: colors.blueSoft },
  muted: { fg: colors.muted, bg: colors.panel2 },
};
export type StatusTone = keyof typeof statusTone;
