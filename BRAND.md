# Demos Network brand and design package

This package aligns with the dark visual language of
[demos.network](https://demos.network/) as captured on **2026-09-28**, under a
strict **black/white/neutral-and-purple-only** policy. The live website has extra
semantic colors; this package deliberately excludes them, including for statuses.
It does not claim exact color parity. [PROVENANCE.md](PROVENANCE.md) separates
observations from adaptations.

## Color

| Role | CSS token | Value |
| --- | --- | --- |
| Page | `--color-bg-base` / `--color-bg-primary` | `#0a0a0f` |
| Subtle | `--color-bg-subtle` / `--color-bg-secondary` | `#111118` |
| Card | `--color-bg-card` | `#16161f` |
| Hover | `--color-bg-card-hover` / `--color-bg-hover` | `#1c1c28` |
| Primary text | `--color-text-primary` | `#f0f0f5` |
| Secondary text | `--color-text-secondary` | `#9ca3af` |
| Decorative or disabled | `--color-text-muted` | `#6b7280` |
| Action | `--brand-violet` | `#7c3aed` |
| Action hover | `--brand-violet-hover` | `#8b5cf6` |
| Readable purple emphasis | `--brand-violet-strong` | `#a78bfa` |
| Border | `--color-border` | `#ffffff14` |
| Border hover | `--color-border-hover` | `#ffffff29` |
| Strong border | `--color-border-strong` | `#ffffff3d` |

The approved near-black and gray tokens have subtle cool casts inherited from
the site. These specific neutrals are permitted; they do not authorize additional
chromatic accents. Purple and white alpha fills are allowed. No green, cyan,
yellow, amber, red or blue is permitted in authored UI, states, charts or assets.

Use secondary text for labels, captions, placeholders and other small readable
content. Muted `#6b7280` fails 4.5:1 on these dark surfaces and must not carry
essential small text. The compatibility token `--color-text-faint` now equals
secondary. Use strong purple for small links; raw action purple is a fill, not a
small-text color. Hairline borders are decorative separators, not sufficient
standalone control indicators.

## Typography

| Role | Family | Weight |
| --- | --- | --- |
| All headings, body, navigation, buttons and inputs | Plus Jakarta Sans | Headings/body 400; UI emphasis 500–700 |
| Code, hashes, addresses, technical labels and data values | Source Code Pro | 400–700 |

`--font-display` and `--font-sans` intentionally use the same family. Only generic
fallbacks follow the authored family. The live CSS includes named system
fallbacks, which this package intentionally omits. `brand/fonts.css` loads both
families, including regular 400; it requires a network connection. See the
[font loading notes](README.md#fonts) for the self-hosting limitation.

- Hero: `clamp(2.5rem, 7vw, 4.5rem)`; 40px minimum, up to 72px desktop,
  line-height 1.05 and tracking -0.02em.
- Section heading: `clamp(2.25rem, 5.5vw, 4.5rem)`, regular 400,
  line-height 1.1, tracking -0.015em. Desktop specimens reach 60–72px.
- Body: at least 16px, line-height 1.6. Technical captions may be 12–14px when
  sufficiently contrasted; inputs remain 16px to avoid mobile zoom.
- Code and data: tabular numerals and ligatures disabled.

## Layout, shape and depth

Use a centered 1200px content container, 24px gutters and responsive one-column
layouts on narrow screens. Marketing sections use 80–128px vertical space. These
are package conventions based on observed utility sizes, not a reconstruction of
every live layout. Data views can be denser without changing the type families.

Cards are opaque `#16161f`, have 24px padding and a 14px radius. Hover uses
`#1c1c28`. Standard buttons have a 10px radius and at least 44px height. Marketing
CTAs use `9999px` pill corners; chips use 6px. White-alpha borders and restrained
dark shadows separate surfaces. Glass is optional via `.dx-card--glass`.

`--gradient-brand` is a purple-only accent-to-strong linear gradient. `--glow-hero`
and `--glow-ambient` are restrained purple radial adaptations, not measured live
radial geometry. Use them behind hero content, not every card. Live multihue
gradients are deliberately excluded. The retained logo gradient runs light
purple to action purple and is a package treatment, not a verified live logo fill.

## Components

Import `tokens.css`, `fonts.css` and `components.css` in that order.

```html
<div class="dx-card">
  <h2>Network overview</h2>
  <p>Use readable neutral text for supporting information.</p>
  <a class="dx-btn dx-btn--primary dx-btn--marketing" href="#details">Explore Demos</a>
</div>
```

- `.dx-btn`: primary, secondary and ghost variants; add `--marketing` for a pill.
  Primary uses white text on action purple. Hover uses the observed brighter
  purple with dark text so small labels keep 4.5:1 contrast; this is a deliberate
  accessibility adaptation. Visible focus uses strong purple with a dark offset.
- `.dx-card`: opaque by default; `--hover` adds hover styling, `--glass` opts into
  a translucent surface when supported. Validate text against the actual backdrop.
- `.dx-stat`: readable secondary label and regular monospace value.
- `.dx-row` / `.dx-mono`: wrapping label/value rows and technical text. Long
  addresses wrap instead of overflowing mobile layouts.
- `.dx-input`: visible label, readable placeholder, 16px text and purple focus.
- `.dx-nav`: wrapping navigation, fixed light image on dark, visible active/focus states.
- `.dx-badge`: 6px chip for a visible category such as “Transfer”.

### Status semantics

Keep semantic names to preserve integrations, but never encode a state solely
through color. All statuses must have visible text. Distinct icons supplement
labels and use `aria-hidden="true"` when redundant. Do not use colored emoji.

| Class/token | Treatment | Example label/icon |
| --- | --- | --- |
| `.dx-pill`, `--success` / `--color-success` | Strong purple on soft purple | ✓ Live / Success |
| `--warning` / `--color-warning` | Primary neutral on white alpha | ! Testnet / Warning |
| `--error` / `--color-error` | Strong purple, double border | × Down / Error |
| `--info` / `--color-info` | Secondary neutral | i Information |
| `--neutral` | Secondary neutral | — Idle |

```html
<span class="dx-pill dx-pill--error">
  <span class="dx-pill__icon" aria-hidden="true">×</span> Error: connection unavailable
</span>
```

The default, success, warning, error, info, soft and muted semantic names remain
available. Applications should announce dynamic results with appropriate status
or alert semantics, while keeping the visible label meaningful without color.

## Logo and downloads

The existing two-comma mark geometry is retained. Its historical repository
attribution was the faucet/indexer; this capture does not independently verify
that geometry or establish a new logo source.

| Asset | Behavior |
| --- | --- |
| `demos-logo.svg` | `currentColor`; inherits only when inline in the document |
| `demos-logo-white.svg` | Fixed `#f0f0f5`; use as `<img>` on dark/purple |
| `demos-logo-gradient.svg` | Two purple stops only |
| `favicon.svg` | Fixed action purple, visible on light and dark tab surfaces |

A standalone SVG in `<img>` does **not** inherit the page's `color`. Use the
fixed light image on dark backgrounds, the default black-rendering standalone
mark on light, or inline SVG when color inheritance is required.

```html
<img class="dx-logo" src="brand/assets/demos-logo-white.svg" alt="Demos">
```

Keep clear space around the mark and preserve its aspect ratio. PNGs are
transparent, 16/32/64/128/256/512px, in white and purple gradient variants. They
are rendered from the SVGs, never manually recolored. Download
[the complete kit](brand/assets/demos-brand-assets.zip). Rebuild commands and
renderer version are in [README.md](README.md#generate-and-check).

## Accessibility and maintenance

Use 4.5:1 for normal text and 3:1 for essential UI indicators. Tests check the
supported opaque surfaces, primary and hover labels, and focus colors; this is
not a blanket accessibility certification. Test custom compositions separately.
Keep a visible keyboard focus and text labels, respect reduced motion, and verify
mobile wrapping. Static examples show sample data only.

CSS is canonical. Run `scripts/sync_tokens.py` to regenerate the full JSON mirror.
The Tailwind 3 preset replaces default colors and families; avoid reintroducing
unapproved defaults through other presets, plugins or custom styles. Dark is the
supported theme. The former optional light override was removed because it was
not a complete or verified theme; consumers needing light mode must define and
validate an approved neutral/purple theme explicitly.
