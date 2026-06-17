# Demos Network — Brand & Design Package

A reusable design system for building Demos Network dapps that look like they
belong. Extracted from the live properties:

| Site | Role | What it taught us |
|------|------|-------------------|
| `demos.network` | Marketing | Hero glow, display type, color-accented copy, dark editorial layout |
| `kynesys.xyz` | Parent brand | Austere, near-black, wide-tracked uppercase, bento grid |
| `faucet.demos.sh` | **Dapp** | Centered card, green CTA, status pills, mono values, floating input |
| `scan.demos.network` | **Dapp** | Top nav, stat cards, two-column data panels, tx badges — *full token system* |

The widest token surface lives in `scan.demos.network` (the raw scan dumped ~234
declarations across its stylesheets). This package normalizes that into a curated,
drop-in subset of ~110 design tokens — see `brand/tokens.css`.

---

## TL;DR — what Demos looks like

- **Dark-first.** Near-black backgrounds (`#08080a`), never pure black for surfaces.
- **Violet is identity** (`#7c3aed`) — glows, focus rings, links, brand moments.
- **Emerald is action** (`#34d399`) — primary buttons, success, "live" status.
- **Cyan is secondary** (`#06b6d4`) — data highlights, secondary emphasis.
- **Hairline borders** = white at ~9% alpha. That's the dark-UI separator.
- **Monospace for all data** — hashes, addresses, amounts, code (Fira Code / SF Mono).
- **Inter for UI, Plus Jakarta for marketing display.**
- **Base-4 spacing**, radius 4→16px (cards 14, buttons 10, pills full).
- **Elevation = hairline border + dark drop shadow**, not soft glow.
- Generous vertical whitespace on marketing; dense, tabular data on dapps.

---

## Files

```
brand/
  tokens.css         ← canonical :root CSS variables (import once)
  tokens.json        ← same values for JS / design tools
  tailwind.preset.js ← Tailwind preset wired to the variables
  fonts.css          ← font loading + base stacks
  components.css     ← dapp component primitives (.dx-* classes)
  preview.html       ← live render of the whole kit
  assets/
    demos-logo.svg          ← currentColor (themeable — inherits text color)
    demos-logo-white.svg    ← fixed #f4f4f5
    demos-logo-gradient.svg ← violet→cyan gradient (hero moments)
    favicon.svg             ← currentColor mark for <link rel=icon>
    png/                    ← 16/32/64/128/256/512 (white + gradient), transparent
    demos-brand-assets.zip  ← all of the above, bundled for download
BRAND.md             ← this file
ui-extracted/        ← raw extraction artifacts + screenshots (reference)
```

## Install

**Plain CSS / any framework:**
```html
<link rel="stylesheet" href="/brand/tokens.css">
<link rel="stylesheet" href="/brand/fonts.css">
<link rel="stylesheet" href="/brand/components.css"> <!-- optional -->
```

**Tailwind:**
```js
// tailwind.config.js
module.exports = { presets: [require('./brand/tailwind.preset.js')], content: [...] };
```
```css
/* app entry */
@import './brand/tokens.css';
@import './brand/fonts.css';
```
Then use `bg-bg-card`, `text-text-primary`, `border-border`, `bg-brand-green`,
`font-mono`, `rounded-card`, etc. For focus, use **`shadow-focus`** (the two-layer
ring that meets WCAG SC 1.4.11 on any surface) rather than `ring-brand`, which is
single-layer and only sets the ring color.

---

## 1. Logo

The Demos mark: two interlocking comma forms (a stylized "ⓓ" / yin-yang motion).
Source of truth: `demos-logo.svg` shipped in the faucet and indexer repos — copied
into `brand/assets/`.

| File | Fill | Use |
|------|------|-----|
| `demos-logo.svg` | `currentColor` | **Default.** Inherits surrounding text color — works on any bg, themes for free. |
| `demos-logo-white.svg` | `#f4f4f5` | Fixed light, when you can't set `color`. |
| `demos-logo-gradient.svg` | violet→cyan | Hero / splash moments only. |

PNG raster sizes (transparent) in `assets/png/` — 16/32/64/128/256/512, white +
gradient. Grab everything from `assets/demos-brand-assets.zip` (the preview's
"Download assets" buttons link these). Favicon: `<link rel="icon" href="/brand/assets/favicon.svg">`.

> The currentColor mark is **invisible on dark unless `color` is set** — that's
> the point (themeable). On a dark surface set `color: var(--color-text-primary)`;
> on light set a dark color; on green set `--color-text-inverse`. The preview's
> logo card shows all four placements.

```html
<!-- in nav, scales with font-size, picks up text color -->
<span class="dx-nav__brand"><img class="dx-logo" src="/brand/assets/demos-logo.svg" alt=""> Demos</span>
```

- `.dx-logo` sets `height: 1.5em` so it scales with the surrounding type.
- On a green button/surface, set `color: var(--color-text-inverse)` so the
  currentColor mark goes dark.
- Keep clear space ≥ the width of one comma around the mark. Don't recolor it
  outside the brand accents. Don't stretch — viewBox preserves aspect.

---

## 2. Color

### Brand accents
| Token | Hex | Use |
|-------|-----|-----|
| `--brand-violet` | `#7c3aed` | Brand identity, glows, focus rings, links |
| `--brand-violet-strong` | `#a78bfa` | Violet text on dark (passes contrast) |
| `--brand-green` | `#34d399` | **Primary CTA**, success, live status |
| `--brand-green-strong` | `#10b981` | CTA hover |
| `--brand-cyan` | `#06b6d4` | Secondary emphasis, data highlights |
| `--brand-cyan-strong` | `#22d3ee` | Cyan text on dark |

Each accent has `-soft` (12% fill) and `-border` (30%). Focus rings don't use a raw
accent — they use `--focus-ring` (a two-layer ring built on `--color-focus-ring`,
violet-strong @ 80%), which clears WCAG SC 1.4.11 on any surface.

### Backgrounds (layer dark → darker)
`--color-bg-letterbox` `#06060a` → `--color-bg-primary` `#08080a` (app) →
`--color-bg-secondary` `#0e0e11` (raised/glass) → `--color-bg-card` `#111113`
(cards) → `--color-bg-card-hover` `#16161a` → `--color-bg-hover` `#1d1d22`.

`--color-bg-tinted` `#13121f` is the violet-tinted surface for highlighted regions.

### Text
`--color-text-primary` `#f4f4f5` (headings) · `--color-text-secondary` `#b4b4bb`
(body) · `--color-text-muted` `#8a8a93` (labels) · `--color-text-faint` `#7c7c87`
(placeholder/disabled, AA 4.5:1 on dark surfaces) · `--color-text-inverse` `#0a0a0a` (on green buttons).

### Borders
White at low alpha: `subtle` 5% → `default` 9% → `strong` 15% → `hover` 16%.
This is *the* signature of the dark UI — use borders, not heavy shadows, to separate.

### Status
`success` `#34d399` · `warning` `#fbbf24` · `error` `#f87171` · `info` `#818cf8`,
each with a `-soft` background variant.

> Contrast note: brand green/cyan/violet at full saturation are bright accents on
> dark — fine for large UI elements and ≥18px bold text. For small body text use
> `-strong` variants or the neutral text tokens to hold WCAG AA (4.5:1).

---

## 3. Typography

| Stack | Token | Where |
|-------|-------|-------|
| Inter | `--font-sans` | All dapp/app UI. The default. |
| Plus Jakarta Sans | `--font-display` | Marketing headings, hero |
| Fira Code / SF Mono | `--font-mono` | Hashes, addresses, amounts, code |

All open-source (Google Fonts). Weights: 400/500/600/700.

**Rules:**
- Body min `16px` (`--text-base`) — prevents iOS auto-zoom on inputs.
- Hero/display: tight tracking (`-0.02em`) and line-height (`1.05–1.1`).
- Marketing uses fluid clamps: `--text-fluid-hero`, `--text-fluid-h2`, etc.
- kynesys-style eyebrows: uppercase + `--tracking-wide` (`0.12em`).
- **Every blockchain value is monospace** with `font-variant-numeric: tabular-nums`
  and ligatures off (`0`/`O`, `1`/`l` must stay distinct).

Scale: caption 12 · label 14 · base 16 · lg 18 · xl 20 · 2xl 24 · 3xl 30 · hero 48.

---

## 4. Spacing, radius, elevation

- **Spacing:** base-4 grid. Tokens `--space-1..32` (4px → 128px). Use tokens, never magic numbers.
- **Radius:** `sm` 4 (badges) · `md` 6 (chips) · `lg` 8 · `button` 10 · `xl` 12
  (inputs) · `card` 14 · `2xl` 16 · `pill` 9999.
- **Elevation:** hairline + drop, not glow.
  - `--shadow-sm` `0 1px 2px #0006`
  - `--shadow-md` `0 0 0 1px #ffffff0e, 0 2px 6px #0006`
  - `--shadow-lg` `0 0 0 1px #ffffff0e, 0 8px 24px #00000080`
- **Glass:** cards/nav are frosted — `--glass-card` / `--glass-panel` (translucent)
  + `--blur-md` (12px) backdrop blur + `--glass-border` (brighter edge). Needs a
  glow/texture behind it to read.

---

## 5. Signature visual: the violet glow

The marketing hero and dapp backgrounds use a soft violet radial behind content:
```css
.hero { background: var(--glow-ambient); }        /* page-level ambient */
.feature { background: var(--glow-hero); }         /* component-level */
```
Pair with `--vignette` to darken edges. Keep it subtle (alpha ≤ 0.12) — it reads
as depth, not decoration. `.dx-glow` in `components.css` wires this up.

---

## 6. Dapp component patterns

These are the recurring building blocks across the faucet and explorer. Full CSS
in `brand/components.css` (prefix `.dx-`). Each maps to a real on-site element.

### Card (`.dx-card`) — frosted glass
The faucet's whole UI is one centered card; the explorer is a grid of them.
Translucent `--glass-card` (~65%) + `backdrop-filter: blur(12px)` + brighter
`--glass-border` + `radius-card` (14px) + `shadow-md` + 24px padding. The blur
needs something behind it — place cards over the violet glow / a textured bg, or
they look flat. Opaque `--color-bg-card` fallback kicks in via `@supports` where
`backdrop-filter` is unsupported. For a fully opaque card, swap `background` to
`var(--color-bg-card)` and drop the blur.

### Button (`.dx-btn`)
- **Primary** (`--primary`): solid `brand-green`, `text-inverse` (dark), radius 10.
  This is the faucet "Request Tokens" CTA. Bold, high-contrast, the one strong color.
- **Secondary** (`--secondary`): violet-tinted fill + violet border + violet text.
- **Ghost** (`--ghost`): transparent + hairline border.
- All: min-height 44px (touch target), focus ring = violet `--focus-ring`.

### Status pill (`.dx-pill`)
The "Live" / "Testnet" / "Connected" badge. Pill radius, soft-colored bg + matching
border + glowing dot. Variants: success (default), warning, error, neutral.

### Stat card (`.dx-stat`)
Explorer's top row: muted label, big bold tabular number, icon top-right. Numbers
always `tabular-nums` so they don't jitter on update.

### Data row + mono (`.dx-row`, `.dx-mono`)
Block/tx lists and the faucet info panel. Label (muted) left, value right.
Addresses/hashes/amounts in `--font-mono`; green (`--accent`) for addresses &
success values, cyan for secondary data. Row separated by `border-subtle`.

### Input (`.dx-input`)
`bg-secondary` + hairline border + radius-xl, 16px text, faint placeholder.
Focus → violet border + violet ring. Faucet uses a floating label above it.

### Top nav (`.dx-nav`)
`bg-secondary` + bottom border + `blur-md` backdrop. Brand (logo + name) left,
links (muted, hover→primary, `aria-current` for active), search + status pill right.

### Tx-type badge (`.dx-badge`)
Small green-soft chip for transaction types ("Transfer") in lists.

---

## 7. Layout conventions

- **Dapps:** top nav (sticky, blurred) → page heading + search → stat-card row →
  two-column data panels → footer (links + "© year Demos Network" + powered-by logo).
  Max content width ~1200px, centered, 24px gutters.
- **Marketing:** full-bleed dark sections, centered hero with glow, generous
  vertical rhythm (80–128px between sections), bento/feature-card grids, color
  accent words in headings.
- **Mobile-first:** single column < 768px; stat cards stack; nav collapses;
  keep 16px body, 44px targets, 8–10px between tappables.

---

## 8. Accessibility & quality bar (2026)

- WCAG 2.1 AA contrast (4.5:1 text, 3:1 UI). Verify accent-on-dark for small text.
- Keyboard: visible focus = violet ring (`--focus-ring`) on every interactive element.
- Semantic HTML (`<header><nav><main><footer>`), ARIA where needed.
- Respect `prefers-reduced-motion` (tokens.css zeroes durations).
- Motion 150–300ms, `--ease-standard`. Use for cause/effect, not decoration.
- Loading: skeletons over spinners for content; spinner only for <3s actions.
- Performance: <1MB initial load; self-host fonts (next/font or @fontsource) in prod.

---

## 9. Do / Don't

**Do**
- Use semantic tokens (`--color-bg-card`), not raw hex, so theming works.
- Reserve solid green for the single primary action per view.
- Keep violet for identity/focus; cyan for data; green for action/success.
- Mono + tabular-nums for every on-chain value.

**Don't**
- Pure black (`#000`) for surfaces (halation). Use `#08080a`/`#111113`.
- Pure white text. Use `#f4f4f5`.
- Heavy/soft drop shadows. The dark UI separates with hairline borders.
- More than one solid accent button competing in the same view.

---

*Regenerate extraction artifacts: `python scripts/crawl.py --url <...> && python scripts/analyze.py`.
Screenshots and raw token dumps are in `ui-extracted/` for reference.*
