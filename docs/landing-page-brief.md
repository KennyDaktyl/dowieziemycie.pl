# Handoff: dowiezmycie.pl — Landing Page

## Overview
Marketing landing page for **dowiezmycie.pl**, a fixed-price (149 zł) passenger transfer service around Kraków (night/Sunday niche, single VW T6 driver). The page pitches the flat-rate promise, lets a visitor start a booking (Skąd/Dokąd/Data/Godzina), and showcases a live driver-tracking panel (map + status).

## About the Design Files
The file in this bundle (`landing-page-reference.html`) is a **design reference built in plain HTML/CSS/JS** — it shows the intended look, copy, layout, and the driver-status/car-animation behavior. It is **not production code to copy as-is**. The task is to **recreate this design in the target codebase's environment** (React is requested — see below) using the app's own component/state patterns, routing, and data layer.

## Fidelity
**High-fidelity.** Colors, type, spacing, copy, and the animated live-tracking behavior are final for this iteration. Recreate pixel-close using the values below.

## Target stack
React (per request). Suggested: React + TypeScript, CSS-in-JS or CSS modules matching the token list below, React Router for the sitemap. State for the live tracker should eventually be driven by a real backend (driver GPS + status), not the timer-based simulation in the reference file.

> Project decision (see /docs and root plan): target stack finalized as **Next.js (App Router, TS)** for the frontend and **Django + DRF + Channels** for the backend, to get SSR/SSG for SEO. This brief is kept as the original design/copy reference.

## Screens / Views (this bundle covers Home; more pages are planned per the sitemap below)

### Home (`/`)
**Purpose:** Convert visitors into a booking; reassure them the fixed price/night service is real and trackable.

**Layout:** Sticky header (max-width 1180px content, centered). Hero section: 2-column grid (`1.05fr 1fr`, 56px gap, stacks to 1 column under 960px) — left = headline + booking form, right = live map/status panel. Below hero: full-width stacked sections, each `padding:70px 0`, separated by a 1px top border, sharing a 1180px centered content wrapper with 24px side padding.

**Components:**
- **Header** — sticky, `rgba(11,15,22,0.82)` background with 10px backdrop blur, bottom border `1px solid rgba(237,238,242,0.09)`. Logo: 9px amber glow dot + "dowiezmy**cię**" (cię in amber), wordmark 19px Space Grotesk 700. Subtitle "TWÓJ SĄSIAD Z BUSEM" 11.5px Barlow Condensed, tracked. Nav links (Zasięg, Jak to działa, Wycieczki, Blog, Cennik) 14.5px, muted color, hover → text color. CTA button "Zadzwoń" (tel: link), amber bg, dark text, 9px radius, hover lifts 1px + amber glow shadow.
- **Hero headline** — eyebrow "24/7 · NIEDZIELE · DO 25 KM OD KRAKOWA" (amber, Barlow Condensed, uppercase, 0.16em tracking, 13px). H1 52px Space Grotesk 600 "Jedna cena. Każdej **nocy.**" (nocy in amber). Lead paragraph 16.5px muted, max-width 480px.
- **Booking card** — panel bg `#121A24`, 14px radius, 22px padding. Two-field rows (Skąd/Dokąd, Data/Godzina) in a 2-col grid, 12px gap. Inputs/select: bg `#1A2530`, 8px radius, border on focus turns amber. Route indicator row: dot→dashed line→"18 KM" label→dashed line→amber dot. Price meter row: bg `#1A2530`, 10px radius; label "Cena kursu" (Barlow Condensed, uppercase, muted) + sub "zaliczka przez BLIK rezerwuje auto"; price right-aligned, 30px Space Grotesk 700, green (`#3ECF8E`), counts up from 0 to "149 zł" on page load (~70ms tick, decelerating). Primary button "Zarezerwuj kurs" full width, amber bg, 9px radius, 15.5px bold, hover lifts + amber glow. Footnote "Bez dopłat nocnych. Bez dopłat niedzielnych." centered, 12px muted.
- **Live map/status panel** — panel bg `#121A24`, 14px radius, relative-positioned, contains an SVG "map" (400×340 viewbox) with grid lines, a stylized river path, a dashed direction line to "Kraków", the route from base (Czernichów) through an intermediate town (Sanka) to the customer town (Rybna, green dot), and an animated car marker (circle + soft halo) that moves along the route and changes color with status. Overlay: top-left "live" pill (pulsing dot + status label), bottom driver card ("Michał · VW T6 · KR 4X2137" + status sub-line, right-aligned ETA + eta sub-label).
- **Panel klienta section** — 4 status-legend cards in a row (Postój/Aktywny/W drodze do Ciebie/Zajęty), each left-bordered in its status color.
- **Zasięg section** — 7 "road sign" cards (town + km), left border in green, amber km label.
- **Jak to działa section** — 3 numbered step cards (01/02/03), big amber-dim number, title, description.
- **Wycieczki section** — 3 trip cards (Auschwitz-Birkenau, Kopalnia Wieliczka, Zakopane): title, description, price in green, "Zobacz trasę →" amber link.
- **Fleet section** — 2-col: left = copy + 3 stat pairs (7 Miejsc / 24/7 Dostępność / 25km Stała cena, amber numbers); right = simple line-art van icon in a gradient panel.
- **Footer** — logo repeat, address/coverage blurb, phone + email, bottom bar with © and "Projekt wizualny — wersja robocza" (remove/replace once shipped).

## Interactions & Behavior
- **Price meter**: counts up 0 → 149 on mount, ~70ms interval, step = `ceil(remaining/4)` (decelerating "odometer" feel).
- **Driver status state machine**: cycles through 4 states on a timer — `postoj` (4s) → `aktywny` (4s) → `wdrodze` (11s) → `zajety` (5s) → repeats. Each state sets: status pill label + color, driver-card sub-label, car marker color.
  - `wdrodze` additionally animates the car marker along an 11-point route (1.1s per hop) and counts down an ETA ("6 min" → … → "Na miejscu").
  - Other states park the car at the base position (Czernichów) and show "—" for ETA.
  - This is a **front-end simulation for the mock**; production should subscribe to real driver location/status (e.g. websocket or polling) and drive the same visual states.
- Nav links are in-page anchors (`#zasieg`, `#jak-to-dziala`, `#wycieczki`); Blog/Cennik are placeholder links pending their own routes.
- Hover states: nav links lighten to full text color; primary/CTA buttons lift 1px with an amber glow shadow; inputs get an amber border on focus.
- Responsive: hero grid and 3-col grids (steps/trips) collapse to 1 column under ~860–960px; H1 drops to 38px under 520px; nav links hide under 860px (mobile nav not yet designed — flag this as an open gap).

## State Management
- `meterValue: number` — animated price counter.
- `driverStatus: 'postoj' | 'aktywny' | 'wdrodze' | 'zajety'` — current status.
- `carPosition: {x, y}` (or real lat/lng in production) — marker position.
- `eta: string` — display ETA text.
- Booking form fields: `from`, `to` (enum of the 7 towns), `date`, `time` — no validation/submit wired yet; needs a real reservation + BLIK deposit flow per the business brief.
- Production data needs: live driver GPS feed, driver status feed, distance/ETA calc service, and the pricing rule engine (flat 149 zł inside the 25 km zone listed, custom quote outside it).

## Design Tokens

**Colors**
- Background: `#0B0F16`
- Panel: `#121A24` / Panel alt: `#1A2530`
- Amber (primary accent): `#F5A623` / Amber dim: `#8a5f1c`
- Green (live/available): `#3ECF8E`
- Red (busy status): `#E5484D`
- Text: `#EDEEF2` / Muted text: `#8B96A3`
- Hairline border: `rgba(237,238,242,0.09)`

**Typography**
- Headings: Space Grotesk, 600–700
- Body: Inter, 400–600
- Eyebrows/labels/road-sign text: Barlow Condensed, uppercase, 500–600, ~0.08–0.16em tracking
- Scale used: 52px (H1) / 32px (H2) / 19–30px (H3/card titles) / 14–16.5px (body) / 11.5–13px (labels)

**Radii**: 6px (small tags/signs) · 8–9px (inputs/buttons) · 10–14px (cards/panels) · 16px (fleet visual) · 20px (pill) · 50% (dots/markers)

**Shadows**: amber glow on hover, `0 4px 20px rgba(245,166,35,0.35)` (nav CTA) / `0 6px 22px rgba(245,166,35,.3)` (primary button) / logo dot glow `0 0 12px 2px var(--amber)`

**Spacing**: section padding 70px vertical; content max-width 1180px, 24px side padding; card padding 14–26px; grid gaps 12–56px depending on context.

## Assets
No photographic/icon assets — all graphics are inline SVG (map illustration, van line-art). Real photos (driver Michał, the VW T6 vehicle, service area) are planned but not yet supplied; treat current SVGs as placeholders for real photography/mapping later. Fonts loaded from Google Fonts (Space Grotesk, Inter, Barlow Condensed).

## Planned sitemap (not yet designed beyond Home)
```
/                          — this page
/nocny-transfer-krakow     — night-niche SEO landing (top priority)
/transfer-lotnisko-balice  — airport transfer landing
/wycieczki/auschwitz
/wycieczki/wieliczka
/wycieczki/zakopane
/cennik                    — fixed vs. custom pricing table
/o-nas
/kontakt
/blog, /blog/:slug
```
Reuse the same design tokens, price-meter component, and driver-status-panel component across these pages for consistency (see brief for full copy/SEO requirements).

## Files
- `landing-page-reference.html` — standalone HTML/CSS/JS reference for the Home page (open directly in a browser).
