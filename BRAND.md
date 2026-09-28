# Demos Network brand and design package

**Source priority: [local latest](http://localhost:3005/) >
[deployed secondary](https://demos.network/)**, captured **2026-09-28**.
The owner-designated latest website supersedes the regular-heading, 14px-card,
dark-only guidance from `b9f1f44`. [PROVENANCE.md](PROVENANCE.md) retains that history.
Only approved branding values are published, with independent guide examples.

The strict policy is **black, white, neutrals and purple only**, including statuses.
Extra source semantic colors are deliberately excluded; this is not exact color parity.

## Color and themes

Light is the root/default theme. Dark is an explicit, reusable scope, matching
the source’s home, lifecycle, build and join sections. Each theme supplies all
color, glass, focus and shadow values so nested themes reset correctly.

| Role | CSS token | Light/default | Dark scope |
| --- | --- | --- | --- |
| Page | `--color-bg-base` / `--color-bg-primary` | `#f8f8f6` | `#111118` |
| Subtle | `--color-bg-subtle` / `--color-bg-secondary` | `#f1f1ee` | `#16161e` |
| Card | `--color-bg-card` | `#fefefc` | `#1c1c24` |
| Hover | `--color-bg-card-hover` / `--color-bg-hover` | `#f4f4f1` | `#23232c` |
| Tinted | `--color-bg-tinted` | `#f7f4fe` | `#1b1726` |
| Letterbox | `--color-bg-letterbox` | `#111118` | `#0b0b10` |
| Primary text | `--color-text-primary` | `#111118` | `#f8f8f6` |
| Secondary text | `--color-text-secondary` | `#676770` | `#a1a1aa` |
| Decorative / disabled text | `--color-text-muted` | `#7c7c85` | `#71717a` |
| Action | `--brand-violet` | `#7c3aed` | `#7c3aed` |
| Action hover | `--brand-violet-hover` | `#6d28d9` | `#8b5cf6` |
| Readable purple | `--brand-violet-strong` | `#6d28d9` | `#a78bfa` |
| Heading highlight | `--brand-violet-highlight` | `#6d28d9` | `#c4b5fd` |
| Border | `--color-border` | `#e4e4df` | `#2a2a33` |
| Hover border | `--color-border-hover` | `#d2d2cc` | `#3a3a45` |
| Strong border | `--color-border-strong` | `#bdbdb6` | `#52525b` |
| Control boundary (adaptation) | `--color-border-control` | `#7c7c85` | `#71717a` |

These specific warm light neutrals, cool dark neutrals and pale purple tints are
approved. They do not authorize extra accents. No green, cyan, yellow, amber,
red or blue is permitted in authored UI, statuses, charts or assets.

Use secondary text for readable labels, captions and placeholders. Muted colors
are not safe for essential small text across all supported surfaces. The
compatibility token `--color-text-faint` equals secondary. Strong purple is the
small-link color. The letterbox token is always dark: use a dark scope for text
on it; it is not a light-theme content surface.

## Typography and spacing

| Role | Family | Weight / treatment |
| --- | --- | --- |
| Headings | Plus Jakarta Sans | Bold 700, −0.035em tracking, 1.04 line-height |
| Body, navigation, buttons and inputs | Plus Jakarta Sans | Body 400; UI emphasis 500–700 |
| Code, hashes, addresses and data | Source Code Pro | 400–700, tabular numerals, no ligatures |

`--font-display` and `--font-sans` share the same family. Only generic fallbacks
follow these two authored families. The existing Google Fonts network imports
are verified; offline rendering uses generic fallbacks. No self-host font work
is required for this update. See [font loading](README.md#fonts).

| Viewport | Hero | H2 | Section vertical / horizontal padding |
| --- | --- | --- | --- |
| Below 810px (including measured 390px and 768px) | 48px | 36px | 96px / 24px |
| 810–1199px | 76px | 56px | 144px / 40px |
| From 1200px (including measured 1440px) | 92px | 56px | 144px / 40px |

The compatible `--text-fluid-hero` and `--text-fluid-h2` names now follow these
source breakpoints rather than the old clamps. Tailwind `md` is 810px and `lg`
is 1200px. Hero content is left aligned with bold purple emphasis, never italic.
Body text is at least 16px with line-height 1.6. Technical captions may be 12–14px
with sufficient contrast; inputs stay 16px to avoid mobile zoom.

Use the retained 1200px content container as a guide convention. Cards use 24px
padding and **20px corners**; standard buttons use 10px, chips 6px, marketing
CTAs pill corners. Cards are opaque by default. Optional glass, neutral shadows,
purple-only radial glows and logo gradients are package adaptations, not claims
of exact source geometry. Reusable examples do not reproduce the private site’s
content or artwork.

## Components and theme scopes

Import `tokens.css`, `fonts.css` and `components.css` in that order.

```html
<section data-theme="dark">
  <div class="dx-card">
    <h2>Component example</h2>
    <p>Readable secondary text inherits the section theme.</p>
    <button class="dx-btn dx-btn--primary">Continue</button>
  </div>
  <div class="dx-card" data-theme="light">A nested light card.</div>
</section>
```

Use `data-theme="light"` or `.dx-theme-light` for a light reset; use
`data-theme="dark"`, `.dx-theme-dark` or `data-surface="ink"` for dark sections.
Token utilities inherit the nearest theme scope without requiring `dark:` variants.
For mixed or nested themes, use these token utilities directly. Tailwind's legacy
`dark:` variant is retained only for whole-page `[data-theme="dark"]` consumers;
it does not reset inside a nested light section and does not recognize the CSS
scope aliases. Do not use it for section-level theming.

- `.dx-btn`: primary, secondary and ghost; add `--marketing` for pill corners.
  Primary labels are white. Light-theme hover keeps white on darker purple;
  dark-theme hover switches to black text on brighter purple to preserve contrast.
- `.dx-card`: opaque; `--hover` adds hover styling and `--glass` opts into glass.
  Validate glass against the actual backdrop.
- `.dx-stat`, `.dx-row`, `.dx-mono`: readable labels and wrapping technical data.
- `.dx-input`: visible label, readable placeholder, 16px text and purple focus.
  Inputs and ghost buttons use the stronger control boundary for at least 3:1.
- `.dx-nav`: wrapping navigation and visible current/focus states. Match the
  standalone logo variant to its background.
- `.dx-badge`: 6px chip with a visible category label.

### Status semantics

Semantic names remain compatible, including their `-soft` and `-muted` forms.
Meaning comes from visible labels and distinct text icons, not color or emoji.

| Class/token | Treatment | Label/icon |
| --- | --- | --- |
| `.dx-pill`, `--success` / `--color-success` | Readable purple on soft purple | ✓ Live / Success |
| `--warning` / `--color-warning` | Primary neutral on neutral tint | ! Testnet / Warning |
| `--error` / `--color-error` | Purple, double border | × Down / Error |
| `--info` / `--color-info` | Secondary neutral | i Information |
| `--neutral` | Secondary neutral | — Idle |

```html
<span class="dx-pill dx-pill--error">
  <span class="dx-pill__icon" aria-hidden="true">×</span> Error: connection unavailable
</span>
```

Use appropriate status/alert semantics for dynamic results. Redundant icons
are hidden from assistive technology while the visible label remains meaningful.

## Logo and downloads

The existing two-comma geometry is retained; the historic faucet/indexer
attribution is not independently reverified by this capture.

| Asset | Behavior |
| --- | --- |
| `demos-logo.svg` | `currentColor`; inherits only when inline |
| `demos-logo-white.svg` | Fixed warm white; use as an image on dark/purple |
| `demos-logo-gradient.svg` | Two purple stops only |
| `favicon.svg` | Fixed action purple |

Standalone SVG images do not inherit the page’s text color. Use the default
black-rendering standalone mark on light, the fixed light mark on dark, or
inline SVG for inheritance. Preserve aspect ratio and clear space. Transparent
PNGs come in 16/32/64/128/256/512px white and gradient variants, rendered directly
from the current SVGs. [Download the kit](brand/assets/demos-brand-assets.zip).

## Accessibility and maintenance

Use at least 4.5:1 for normal text and 3:1 for essential UI boundaries/focus.
Tests cover both themes’ opaque surfaces, status tint compositing, button labels
and control/focus contrast. Muted text restrictions, hover label changes,
stronger control boundaries and opaque focus rings are deliberate accessibility
adjustments. This is not a certification of arbitrary custom compositions.
Keep visible keyboard focus, respect reduced motion and verify mobile wrapping.

CSS is canonical. Run `scripts/sync_tokens.py` to generate JSON: existing top-level
keys describe light/default; `themes.light` and `themes.dark` contain explicit,
complete values; `responsive` records breakpoint overrides. The Tailwind 3 preset
replaces framework colors and font families. Rebuild PNGs and ZIP after changes.
Both preview pages were checked in Chrome at 1440, 768 and 390 pixels.
