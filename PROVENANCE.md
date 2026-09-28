# Source observations and palette policy

Source URL: **https://demos.network/**

Capture date: **2026-09-28**
Observed stylesheet: https://demos.network/_next/static/css/affdf25fe5b17758.css

This update used the supplied live-browser capture `demos-live-evidence.json`
(computed custom properties, loaded font records and element samples) and
`demos-live.css` (captured stylesheet rules). The originals were read without
modification. Their SHA-256 fingerprints are:

| Capture | SHA-256 |
| --- | --- |
| `demos-live-evidence.json` | `645c51a600af95f9f97565463e789ee4d945cd17673994eb0160d53d123cdfbc` |
| `demos-live.css` | `70451172e5ce0387f43c0ca52437d03b2bee47b3d8597c0ca6b803f3db99b9e9` |

The raw captures are not distributed in this package. They include styles outside
the approved palette. Source URLs describe the dated evidence and may change on
a later deployment; the captured styles, rather than current remote responses,
are the basis for this update.

## Observed styles

| Evidence | Observation | Package mapping |
| --- | --- | --- |
| Dark theme CSS and computed variables | Base `#0a0a0f`, subtle `#111118`, card `#16161f`, hover `#1c1c28` | Exact values; primary/secondary/hover aliases retained |
| Dark theme CSS | Text `#f0f0f5`, `#9ca3af`, `#6b7280` | Exact primary/secondary/muted tokens |
| Dark theme CSS | Accent `#7c3aed`, hover `#8b5cf6`, strong `#a78bfa` | Action / hover / readable purple emphasis |
| Dark theme CSS | Borders `#ffffff14`, hover `#ffffff29`, strong `#ffffff3d` | Exact white-alpha border values |
| Loaded font records and font-face CSS | Plus Jakarta Sans, normal variable weight 200–800; Source Code Pro, 200–900 | Same two families; requested 400/500/600/700 weights |
| Heading samples | H1 72px / 400; H2 examples 60px, 64.9px and 72px / 400; H3 28px and 32px / 400 | Regular headings, responsive large type |
| Type utility CSS | Hero clamp 2.5rem / 7vw / 4.5rem; section clamp 2.25rem / 5.5vw / 4.5rem | Exact selected clamp expressions |
| Type utility CSS | Hero line-height 1.05 / tracking -0.02em; section 1.1 / -0.015em | Hero and section tokens |
| Wallet CTA sample | Purple fill, white label, 15px / 600, radius 9999px | Pill marketing modifier; 16px package label |
| Radius variables | Card 14px, standard button 10px, chip 6px | Exact shape tokens |
| Layout utility CSS | 24px card padding; max widths include 1100/1200/1400px; section sizes include 80/96/112/120/128/160px | 1200px container and 80–128px section convention |
| Gradient utility CSS | Linear directions to bottom, bottom right and right; accent-to-strong endpoints are available, alongside additional hues | Purple-only 135-degree accent-to-strong adaptation |

Utility presence establishes what the stylesheet supports, not which exact
combination appeared on every element. The capture does not record sufficient
inline gradient geometry to claim an exact live radial glow. The package's radial
glows and vignette remain clearly labeled adaptations. The live capture also has
larger display utilities; 72px is the selected package hero maximum, not a claim
that every heading on the website is at most 72px.

## Deliberate differences

The owner-directed palette permits **black, white, neutrals and purple only**.
The live site includes green success, cyan secondary accents, amber warning,
red error and blue information styling, plus multihue gradients. These are
intentionally excluded. Yellow is also prohibited. This package does **not**
claim exact color parity with the website.

- Status names are compatible, but all status values are purple or neutral.
  Visible labels and distinct text icons identify the state without color.
- The approved slightly cool neutral values above are preserved exactly. They
  do not broaden the allowed hue palette.
- Small readable text uses secondary rather than muted. The live muted token is
  retained for decorative or disabled content only. `text-faint` is a readable alias.
- Button hover uses dark text on the observed brighter purple, preserving small
  label contrast. Focus uses opaque strong purple and a dark offset.
- Only generic font fallbacks are authored. Fonts use a two-family Google Fonts
  import; font binaries could not be downloaded in the build environment, so
  self-hosting and exact offline font rendering remain outstanding.
- Opaque cards are the default. Optional glass, shadows, radial glows and reusable
  dapp arrangements are package conventions, not claimed exact live components.
- The legacy partial light theme is removed. Dark is the supported theme.
- Logo geometry is retained from the existing repository. Historical docs
  attributed it to faucet/indexer repositories; this capture does not independently
  verify that claim. The purple SVG treatment is retained, and all 12 PNGs and the
  ZIP are rebuilt from the current SVGs. The previous bundle had stale multicolor
  artwork. The favicon now has a fixed purple fill.

## Validation scope

The automated suite checks complete CSS/JSON parity, known source values,
approved color literals, font declarations and imports, status labels, local
page links, contrast on supported surfaces, PNG dimensions/transparency/palette,
SVG raster freshness, and ZIP byte-for-byte contents and deterministic metadata.
A Node check loads the Tailwind preset and verifies its palette/font replacement
and token references. See [README.md](README.md#generate-and-check) for commands.

On 2026-09-28, all 17 Python tests, the Node preset and inline-script checks,
CSS/JSON parity, asset freshness, Python syntax and `git diff --check` passed.

Both preview pages were subsequently checked in Chrome over a local HTTP server
at viewport widths 1440, 768 and 390 pixels. All six page/viewport combinations
loaded Plus Jakarta Sans and Source Code Pro, used 400-weight headings, had no
horizontal document overflow, and had no missing images. Desktop visual review
found no major layout or palette problems. Clipboard interactions remain
unverified; automated checks cover the inline scripts and their error handling.
