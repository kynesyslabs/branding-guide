# Demos branding guide

Dark design tokens, reusable components and logo assets aligned with
[demos.network](https://demos.network/), captured **2026-09-28**.

**Black, white, neutrals and purple only, including statuses.** The live website
also uses extra semantic colors. Those are deliberately excluded here; this
package does not claim exact color parity. See [PROVENANCE.md](PROVENANCE.md)
for observed styles and deliberate policy decisions.

Plus Jakarta Sans is used for all headings, body and UI. Source Code Pro is used
for technical text. Headings are regular 400, with large desktop type and roomy
spacing. Status labels and icons carry meaning independently of color.

## Files

- `brand/tokens.css` — canonical dark CSS tokens, including compatible legacy names.
- `brand/tokens.json` — complete generated JSON mirror with source metadata.
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
Consumers must also keep custom styles and additional plugins within the policy.
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
access; offline rendering uses generic `system-ui`/`sans-serif` and
`ui-monospace`/`monospace` fallbacks. Font binaries are not bundled: downloading
them was unavailable during this update. For self-hosting, obtain these same
families from their upstream distributions, retain their SIL Open Font License
files, and replace the import with local `@font-face` rules. Do not add a third
authored family or claim offline font parity until the binaries are included.

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
