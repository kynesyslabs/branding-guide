# Demos branding guide

Light/default design tokens, reusable dark scopes, components and logo assets.
**Source priority: [local latest](http://localhost:3005/) >
[deployed secondary](https://demos.network/)**, captured **2026-09-28**. The owner
identified localhost as the latest website; it supersedes the public-site styling
in branch base `b9f1f44`. Only approved branding values are included.

**Black, white, neutrals and purple only, including statuses.** The reference styles
also contain extra semantic colors. Those are deliberately excluded here; this
package does not claim exact color parity. See [PROVENANCE.md](PROVENANCE.md)
for observed styles and deliberate policy decisions.

Plus Jakarta Sans is used for all headings, body and UI. Source Code Pro is used
for technical text. Headings are bold 700, with −0.035em tracking and 1.04 line-height. Hero type
is 48/76/92px; H2 is 36/56px. Cards have a 20px radius. Status labels and icons carry meaning independently of color.

## Files

- `brand/tokens.css` — canonical light/default and dark scoped CSS tokens, including compatible legacy names.
- `brand/tokens.json` — compatible default JSON mirror plus complete `themes.light` / `themes.dark`
  values, responsive overrides and source metadata.
- `brand/fonts.css` — the two verified families and generic fallbacks.
- `brand/components.css` — cards, standard and marketing buttons, status pills, data and forms.
- `brand/tailwind.preset.js` — Tailwind 3 preset replacing default colors and font stacks.
- `index.html` — interactive guide with token swatches and copyable examples.
- `brand/preview.html` — compact component preview.
- `brand/assets/` — SVG originals, regenerated PNGs and a reproducible ZIP.
- [BRAND.md](BRAND.md) — usage, accessibility and design rules.

## Use

```html
<link rel="stylesheet" href="brand/tokens.css">
<link rel="stylesheet" href="brand/fonts.css">
<link rel="stylesheet" href="brand/components.css">
```

Light is the default. Apply a reusable theme to any container:

```html
<section data-theme="dark">
  <div class="dx-card">Dark component</div>
  <div data-theme="light" class="dx-card">Nested light component</div>
</section>
```

`data-surface="ink"` and `.dx-theme-dark` are dark aliases; `.dx-theme-light`
is a light alias. Colors, shadows and focus styles reset at each theme boundary.
For Tailwind 3, import the CSS above and configure:

```js
module.exports = {
  presets: [require('./brand/tailwind.preset.js')],
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
};
```

Use `bg-bg-card`, `text-text-secondary`, `bg-brand-violet`, `font-mono`,
`rounded-card`, `rounded-chip`, and `focus:shadow-focus`. The preset replaces
Tailwind's color and font defaults, so unapproved hue utilities are unavailable.
Utilities inherit the current scoped theme. The preset matches the source’s
810px `md` and 1200px `lg` breakpoints. Consumers must also keep custom styles
and additional plugins within the policy.
Tailwind 4 requires a separate integration; this JavaScript preset targets 3.

## Preview

Open either HTML file, or serve the repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Visit `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/brand/preview.html`.
Copy buttons require a browser with clipboard access; failures display a message.
Network data and forms are visual examples, not live services.

## Fonts

`fonts.css` imports only Plus Jakarta Sans and Source Code Pro, with normal
weights 400, 500, 600 and 700 and `display=swap`. It requires Google Fonts network
access; the current network imports were verified in the supplied evidence.
Offline rendering uses generic `system-ui`/`sans-serif` and
`ui-monospace`/`monospace` fallbacks. Font binaries are not bundled and no self-host
font work is required for this alignment. No third authored family is permitted.

## Generate and check

Python 3 and Node.js are used for checks. Install the pinned PNG inspection
dependency with `python3 -m pip install -r requirements-dev.txt` in your environment.
The renderer is `rsvg-convert` from librsvg (`brew install librsvg` on macOS or
`apt install librsvg2-bin` on Debian/Ubuntu).

```sh
python3 scripts/sync_tokens.py
python3 scripts/gen_logo_assets.py
python3 scripts/sync_tokens.py --check
python3 -m unittest discover -s tests -v
node tests/test_tailwind.js
python3 scripts/gen_logo_assets.py --check
```

The reference renderer is **librsvg 2.61.3 / cairo 1.18.4**. PNG byte comparisons
require the same rendering stack; another version may rasterize edges differently.
The ZIP uses sorted entries, fixed timestamps and permissions, and uncompressed
entries for deterministic bytes. It includes the styles, pages, docs, source SVGs,
PNGs, generation scripts and tests. Regenerate it after any packaged file changes.

`scripts/crawl.py` and `scripts/analyze.py` remain optional inspection utilities
(the crawler requires Playwright). Their raw output is evidence, not approved
brand tokens: never promote the site's extra colors automatically.

## Verification handoff

Automated checks cover both themes, CSS/JSON parity, typography, palette,
contrast, theme-aware swatches, local links, SVG/PNG freshness and ZIP contents.
Both preview pages were checked in Chrome at 1440, 768 and 390 pixels;
prior browser results apply only to the superseded public-site version.
