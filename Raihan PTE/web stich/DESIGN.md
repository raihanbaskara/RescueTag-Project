---
name: Rescue-Tag Telemetry & Command Portal
colors:
  surface: '#fbf8f5'
  surface-dim: '#f3ece5'
  surface-bright: '#ffffff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fdfbf9'
  surface-container: '#f7f2ec'
  surface-container-high: '#f0e8df'
  surface-container-highest: '#e6ded3'
  on-surface: '#0f172a'
  on-surface-variant: '#475569'
  outline: '#cbd5e1'
  outline-variant: '#eedfd2'
  surface-tint: '#ea580c'
  primary: '#ea580c'
  on-primary: '#ffffff'
  primary-container: '#fff7ed'
  on-primary-container: '#c2410c'
  secondary: '#d97706'
  on-secondary: '#ffffff'
  secondary-container: '#fef3c7'
  on-secondary-container: '#92400e'
  tertiary: '#0f766e'
  on-tertiary: '#ffffff'
  tertiary-container: '#f0fdfa'
  on-tertiary-container: '#115e59'
  error: '#dc2626'
  on-error: '#ffffff'
  background: '#f8f5f0'
  on-background: '#0f172a'
typography:
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  brand-title:
    fontFamily: Playfair Display
    fontStyle: italic
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
  tech-label:
    fontFamily: Space Grotesk
    fontSize: 11px
    fontWeight: '700'
    letterSpacing: 0.2em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.25rem
  lg: 2rem
---

# Rescue-Tag Design System — Google Stitch Specification

## 1. Visual Atmosphere & Aesthetic Philosophy
- **Domain:** Subterranean Emergency Rescue & Disaster Medical Triage (IoT Wearable + 433 MHz LoRa Mesh Network).
- **Core Philosophy:** Industrial Brutalism meets High-End Swiss Typography. Tactile hardware precision, declassified aerospace coordinates, and warm amber/rescue-orange emergency hues.
- **Palette Tone:** Warm Canvas Ivory (#fbf8f5) with high-contrast International Rescue Orange (#ea580c), Warm Amber (#d97706), and Dark Slate (#0f172a). No AI-purple gradients, no pure black #000000.
- **Three Dials Setting:**
  - DESIGN_VARIANCE: 7 (Asymmetric Split Stage)
  - MOTION_INTENSITY: 6 (Fluid CSS + Tactile Spring States)
  - VISUAL_DENSITY: 6 (Tactical Telemetry Density with Generous Whitespace)

## 2. Typographic Hierarchy
1. **Brand Wordmark:** Playfair Display Italic (ont-brand) — elegant, timeless editorial serif. Used exclusively for 'Rescue-Tag'.
2. **Headlines & Primary CTAs:** Outfit (ont-outfit) — geometric sans with balanced, tall vertical proportions (anti-squish / anti-gepeng).
3. **Tactical & Telemetry Labels:** Space Grotesk (ont-tech) & Rajdhani (ont-tactical) — monoline aerospace precision for coordinates, node IDs, and protocol badges.
4. **Data Values & Counters:** JetBrains Mono (ont-mono) — strict tabular figures for BPM, temperatures, and latency.
5. **Body Copy:** Plus Jakarta Sans (ont-sans) — readable, warm neutral sans-serif.

## 3. Structural Components & Layout Rules
- **Doppelrand Architecture:** Nested double-bezel container (
ing-1 ring-black/10 rounded-[2.5rem] outer tray with an inner frosted glass canvas 
ounded-[2rem]).
- **Product Showcase Stage:**
  - Ambient studio horizon (
adial-gradient warm glow behind hardware).
  - Declassified corner blueprint crosshairs (+) and coordinate marks (LAT -8.2465° // LON 113.6965°).
  - Strict zero-collision rule: No floating tooltip stickers plastered over the watch. The live OLED screen on the watch displays its own high-definition telemetry.
- **Spec Rail:** Ultra-fine hairline dividers (order-t border-black/[0.06]) displaying three balanced metrics (ENCLOSURE, TELEMETRY, RELAY).
- **Segmented Role Selector:** Apple/Linear-style tactile pill switcher with active white elevation and orange accent.
- **CTA Button:** Button-in-button tactile press state (tn-tactile active:scale-[0.98]) with directional arrow badge.

## 4. Anti-Patterns & Banned Elements
- **Banned:** Generic floating pill badges hovering over device straps.
- **Banned:** 'Gepeng' / flat-stretched horizontal display fonts (e.g. Syne in extra-bold).
- **Banned:** Pure black backgrounds or drop shadows.
- **Banned:** Outdated gas sensor telemetry (CO, O2, BME688) not present in hardware.
- **Banned:** Untested depth metrics (-120m, -250m).
- **Banned:** Redundant 'Deploy Squad' actions in sidebar.
