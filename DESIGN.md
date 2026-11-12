# Blackout Arcade — Dimension Liquid Glass Design System

> Dusk-lit frosted glass console on a `#0a0a0a` void canvas with personalizable accent glow.

**Theme:** dark (`#0a0a0a` Void Canvas + `#161616` Graphite)  
**Active Implementation:** [`frontend/index.html`](frontend/index.html), [`frontend/css/main.css`](frontend/css/main.css), [`frontend/css/games.css`](frontend/css/games.css), [`frontend/js/app.js`](frontend/js/app.js)

> [!NOTE]
> **Archival Note:** An earlier *Cards Against Humanity* ("Apocalypse broadcast on blackout paper") editorial design concept—centered around `#000000` Void Black, `#ebe4d8` Bone Cream, `#c3bdb3` Ash Taupe, `#ff4034` Alarm Red, and Spektra poster display type—was superseded by the **Dimension Liquid Glass Console** design system documented below. Backwards-compatible CSS variable aliases (`--color-void-black`, `--color-bone-cream`, `--color-ash-taupe`, `--color-alarm-red`, `--font-spektra`, `--font-helvetica-neue-lt`) remain mapped to active Liquid Glass tokens in `:root` for scoped board components.

---

## Visual Philosophy

Blackout Arcade combines a **PS5-inspired edge-to-edge console shell** with **Dimension Liquid Glass** depth:

- **Void Canvas & Graphite Base:** Full-bleed `#0a0a0a` canvas layered beneath blurred ambient dusk orbs (`.liquid-orb`), subtle hairline radar orbits (`.radar-svg`), and dynamic full-viewport SVG hero artwork tinted by the active `--accent`.
- **Translucent Specular Glass:** Panels, navigation pills, cards, and modals sit on multi-stop translucent gradients backed by `backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat))`, `1px` hairline borders (`rgba(229, 229, 229, 0.16)`), and crisp inset top specular highlights (`--glass-specular`).
- **User-Personalizable Chromatic Signal:** A single dynamic `--accent` token drives radial spotlights, active rail outlines, `1px` specular divider washes (`--gradient-accent-wash`), status pulse dots, and interactive board highlights.

---

## Tokens — Colors & Surfaces

### Neutral Canvas, Glass & Text Tokens (`:root` in `frontend/css/main.css`)

| Role | Token | Value | Purpose |
|------|-------|-------|---------|
| Void Canvas | `--color-void-canvas` | `#0a0a0a` | Primary full-bleed page background |
| Graphite | `--color-graphite` | `#161616` | Elevated dark surfaces & high-contrast ink on white/light fills |
| Frosted Glass | `--color-frosted-glass` | `rgba(212, 212, 212, 0.09)` | Base frosted surface tint |
| Ink Black | `--color-ink-black` | `#000000` | Deep shadow base & scrim anchoring |
| Snow White | `--color-snow-white` | `#ffffff` | Primary CTA pill fills, active titles, high-emphasis icons |
| Bone | `--color-bone` | `#ededed` | Default body text, headings, and control foregrounds |
| Ash | `--color-ash` | `#c2c2c2` | Secondary prose, descriptions, metadata, hints |
| Smoke | `--color-smoke` | `#b2b2b2` | Muted supporting labels |
| Slate | `--color-slate` | `#686868` | Placeholders, timestamps, tertiary captions |
| Hairline | `--color-hairline` | `rgba(229, 229, 229, 0.16)` | Standard `1px` glass borders & dividers |
| Hairline Strong | `--color-hairline-strong` | `rgba(229, 229, 229, 0.34)` | Interactive input borders & hover/modal boundaries |

### Personalizable Accent Presets & Contrast (`ACCENT_PRESETS` in `frontend/js/app.js`)

The default accent is **Crimson Glow (`#E5484D`)**. Users can switch presets or pick any custom 6-digit hex color in the Settings modal (persisted to `localStorage` under `blackout_accent_color`).

| Preset ID | Display Name | Hex | Swatch Class | `--accent-contrast` |
|-----------|--------------|-----|--------------|---------------------|
| `crimson` *(default)* | Crimson Glow | `#E5484D` | `.swatch-crimson` | `#FFFFFF` |
| `violet` | Dusk Violet | `#6B62F2` | `.swatch-violet` | `#FFFFFF` |
| `cobalt` | Cobalt Ice | `#3B82F6` | `.swatch-cobalt` | `#FFFFFF` |
| `amber` | Sunset Amber | `#F59E0B` | `.swatch-amber` | `#0A0A0A` |
| `emerald` | Emerald Mist | `#10B981` | `.swatch-emerald` | `#FFFFFF` |
| `rose` | Rose Quartz | `#F43F5E` | `.swatch-rose` | `#FFFFFF` |
| `mono` | Pure Mono | `#EDEDED` | `.swatch-mono` | `#0A0A0A` |

#### Runtime-Derived Accent Tokens (`_applyAccentColor`)

- `--accent`: Selected hex color (default `#e5484d`)
- `--accent-rgb`: Comma-separated RGB triplet (default `229, 72, 77`)
- `--accent-subtle`: `rgba(var(--accent-rgb), 0.09)`
- `--accent-soft`: `rgba(var(--accent-rgb), 0.18)`
- `--accent-mid`: `rgba(var(--accent-rgb), 0.42)`
- `--accent-glow`: `rgba(var(--accent-rgb), 0.565)`
- `--accent-contrast`: Dynamically computed from relative luminance (`0.2126*R + 0.7152*G + 0.0722*B) / 255`: `#0A0A0A` when luminance `> 0.62` (such as **Pure Mono `#EDEDED`** or **Sunset Amber `#F59E0B`**), `#FFFFFF` otherwise. Used across accent-filled action buttons, Dominoes tags/badges, UNO wild controls, and error toast banners so foreground labels never lose legibility under light or monochrome accents.
- `--gradient-accent-wash`: Horizontal `1px` specular glow wash peaking at `rgba(var(--accent-rgb), 0.565)` in the center and fading to transparent edges.

#### Semantic Status & Hazard Signals

Critical game and connection indicators preserve unambiguous semantic colors even when `--accent` is set to **Pure Mono (`#EDEDED`)**:

- **WebSocket Online (`#ws-status-dot.is-online`):** `#10b981` (emerald)
- **WebSocket Offline (`#ws-status-dot.is-offline`):** `#f59e0b` (amber pulse)
- **Minesweeper Flagged (`.ms-cell.flagged`):** Distinct warning/amber tint
- **Minesweeper Detonated Mine (`.ms-cell.mine`):** Distinct semantic hazard `#e5484d` tint
- **Globe Thermal Distance Scale (`heatFillColor`):** Cool indigo/sky (Far) → yellow/amber (Warm) → crimson/red (Hot) → `#10B981` emerald (Exact)

---

## Tokens — Liquid Glass Refraction & Elevation

Users can tune glass intensity in **Appearance & Settings** (`GLASS_PRESETS`, persisted in `localStorage` under `blackout_glass_intensity`):

| Level | Label | `--glass-blur` | `--glass-sat` |
|-------|-------|----------------|---------------|
| `subtle` | Subtle Frost | `10px` | `130%` |
| `liquid` *(default)* | Liquid Glass | `20px` | `165%` |
| `deep` | Deep Refraction | `32px` | `195%` |

### Surface Gradients & Utility Classes

- `.glass-nav`: `--glass-elevated` (`linear-gradient(155deg, rgba(32, 32, 36, 0.72), rgba(16, 16, 18, 0.62))`), `backdrop-filter: blur(var(--glass-blur)) saturate(var(--glass-sat))`, `--glass-specular`, `--glass-elevation`.
- `.glass-card`: `--glass-surface` (`linear-gradient(145deg, rgba(255, 255, 255, 0.09), rgba(212, 212, 212, 0.03) 50%, rgba(255, 255, 255, 0.05))`), `border-radius: var(--radius-card)` (`24px`), `--glass-specular`, `--glass-elevation`.
- `.glass-subcard`: `rgba(255, 255, 255, 0.04)` with `calc(var(--glass-blur) * 0.7)` blur and `140%` saturation (`border-radius: 18px`).
- `.glass-modal`: `--glass-modal-bg` (`linear-gradient(160deg, rgba(26, 26, 30, 0.84), rgba(12, 12, 14, 0.80))`), `calc(var(--glass-blur) + 6px)` blur, `175%` saturation, `--color-hairline-strong` border.

---

## Tokens — Typography

Fonts are loaded via Google Fonts (`DM Sans` 400–700, `Geist` 400/500/600, `Inter` 400/500/600) with crisp system sans fallbacks.

### Font Families

- `--font-dm-sans`: `'DM Sans', 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` (default body, hero display, buttons, labels)
- `--font-geist`: `'Geist', 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` (`.heading`, `.heading-lg`, `.hud-game-title`, `.comms-title`, `.settings-title`, `.index-num`)

### Type Scale & Weights

| Role | Token | Size | Line Height Token | Weight / Usage |
|------|-------|------|-------------------|----------------|
| Caption | `--text-caption` | `13px` | `--leading-caption: 1.5` (`tracking: 0.02em`) | HUD chips, logs, chat, secondary labels |
| Body | `--text-body` | `16px` | `--leading-body: 1.5` | Prose, descriptions, default body |
| Subheading | `--text-subheading` | `18px` | `--leading-subheading: 1.5` | Settings section titles, subheads |
| Heading SM | `--text-heading-sm` | `24px` | `--leading-heading-sm: 1.33` | Compact modal & panel headings |
| Heading | `--text-heading` | `36px` | `--leading-heading: 1.11` | Modal & bunker primary titles (`clamp(24px, 3vw, 32px)`) |
| Heading LG | `--text-heading-lg` | `48px` | `--leading-heading-lg: 1.04` | Game Over headline (`clamp(32px, 4.5vw, 48px)`) |
| Display | `--text-display` | `72px` | `--leading-display: 1` | Entry & PS5 hero display (`clamp(44px, 5.5vw, 72px)`) |

Font weight tokens: `--font-weight-regular: 400`, `--font-weight-medium: 500`, `--font-weight-semibold: 600`, `--font-weight-bold: 700` (`--font-weight-extrabold: 600` legacy alias).

---

## Tokens — Spacing, Radii & Layout

### Spacing & Widths

- Scale: `--spacing-4` (`4px`), `--spacing-6` (`6px`), `--spacing-8` (`8px`), `--spacing-10` (`10px`), `--spacing-12` (`12px`), `--spacing-14` (`14px`), `--spacing-16` (`16px`), `--spacing-20` (`20px`), `--spacing-24` (`24px`), `--spacing-28` (`28px`), `--spacing-32` (`32px`), `--spacing-40` (`40px`), `--spacing-48` (`48px`), `--spacing-56` (`56px`), `--spacing-60` (`64px`).
- Containers: `--page-max-width: 1200px`, `--console-max-width: 1440px`, `--arena-max-width: 1200px`.

### Radii

| Element | Token | Value |
|---------|-------|-------|
| Icon Badge | `--radius-icon` | `4px` |
| UI Control / Input | `--radius-ui` / `--radius-input` | `10px` |
| Floating Nav / HUD | `--radius-nav` | `22px` |
| Card / Activity Tile / Modal | `--radius-card` | `24px` |
| Large Panel | `--radius-panel` | `40px` |
| Pill Button / Tag | `--radius-pill` | `9999px` |

---

## Console Shell & Core Components

1. **Liquid Glass Entry Gate (`<main id="view-entry">`):**
   - Centered `.status-banner-pill` displaying live WebSocket status (`#ws-status-dot` + `#ws-status-entry`).
   - `.entry-glass-card` (`border-radius: 32px`) with `1px` top accent wash, `h1.display-headline`, callsign form, and inline quick accent swatch strip.
2. **PS5-Inspired Console Hub (`#view-lobby` → `<main id="tab-games">`):**
   - Floating `.ps5-topbar-inner.glass-nav` with brand gem, `Hub` tab, World Country Encyclopedia button (`197` nations), Bunker Records button, Settings button (with accent dot), Callsign Avatar button, and live clock.
   - Horizontal Game Switcher Rail (`#ps5-game-rail`, `role="listbox"`, `aria-orientation="horizontal"`): `100px × 100px` glass tiles expanding to `250px × 250px` when active (`76px → 164px` on `max-height: 800px` laptop viewports; `66px → 96px` on `max-width: 760px` mobile).
   - Middle-left hero block (`h1#ps5-hero-title`, description, contextual Difficulty / Category / Custom Minesweeper inputs, and `Play Solo` / `Host Game` / `Join Game` pill CTAs).
   - Bottom edge-to-edge 16:9 Liquid Glass Activity Strip (`#ps5-activity-strip`) for instant deep-linking, plus below-the-fold Contextual Help, Live Rooms, and Top Module Records (`section.ps5-hub-details`).
3. **Game Arena & Sidebars (`#view-arena` → `<main class="arena-body">`):**
   - Sticky `.arena-hud.glass-nav` with `← Hub`, Room Code + Copy cluster, `h1#hud-game-title`, centered turn indicator & `#arena-spectator-badge`, player chips, `SFX: ON/OFF` toggle (`#btn-arena-mute`), `Theme` button, `Pin Help` toggle, and `Comms` toggle with `#comms-unread-dot`.
   - Left-docked **Pinned Game Help** (`aside#pip-help-panel`, `280px` sticky on desktop, inline flow card `<= 1024px`).
   - Right-docked **Room Comms Sidebar** (`aside#arena-comms-drawer`, `320px` sticky on desktop, fixed slide-over drawer `<= 1024px`) housing `LIVE EVENT LOG` (`#arena-events-list`) and `ROOM CHAT` (`#arena-chat-list`, `#arena-chat-form`).
4. **Modals (`role="dialog"`, `aria-modal="true"`):**
   - Settings & Accent Personalization (`#modal-settings`), Join Room (`#modal-quickjoin`), Game Over (`#modal-gameover`), Bunker Records (`#modal-leaderboard`), Rename Callsign (`#modal-rename`), World Country Encyclopedia (`#modal-encyclopedia`), and Custom Chess Board Editor (`#modal-chess-custom-editor`).

---

## Accessibility & CSS Discipline

- **Semantic Landmarks & Headings:** Every active view has a `<main>` landmark (`#view-entry`, `#tab-games`, `.arena-body`) and a visible `<h1>` (`h1.display-headline`, `h1#ps5-hero-title`, `h1#hud-game-title`). Section subheadings use semantic `<h3>` (`.bunker-sublabel`) rather than styled `<div>`s.
- **ARIA & Live Regions:** `role="listbox"` / `aria-orientation="horizontal"` on `#ps5-game-rail`; `role="radiogroup"` / `role="radio"` / `aria-checked` on difficulty and QA category pill groups; `aria-labelledby` on all dialogs; `role="log"` + `aria-live="polite"` on event log and room chat; `aria-live="polite"` on `#ws-status-entry`, `#toast-banner`, and `#arena-spectator-badge`; `aria-pressed` on mute buttons.
- **Keyboard Focus Visibility:** Explicit `:focus-visible` outlines (`outline: 2px solid var(--accent); outline-offset: 2px;`) across links, buttons, inputs, selects, textareas, `[tabindex]`, rail tiles, difficulty/filter pills, accent swatches, encyclopedia items, and chess editor squares.
- **Zero Inline Styles:** [`frontend/index.html`](frontend/index.html) contains zero `style="..."` attributes; all layout, typography, spacing, and accent states are controlled via semantic CSS classes and CSS custom properties.
