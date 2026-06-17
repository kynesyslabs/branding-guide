# Demos branding guide

Brand tokens and component styles for Demos Network dapps, pulled from the live
sites (demos.network, scan.demos.network, faucet.demos.sh, kynesys.xyz) so new
apps don't have to guess at the colors.

Dark-first. Violet for identity, green for actions, cyan for data.

Live page: https://kynesyslabs.github.io/branding-guide/

## What's here

- `brand/tokens.css` — all the CSS variables. Import this and use `var(--...)`.
- `brand/tokens.json` — same values as JSON, if you need them in JS or a design tool.
- `brand/components.css` — ready-made dapp pieces (cards, buttons, status pills,
  stat cards, data rows, inputs, nav). Class prefix `dx-`.
- `brand/tailwind.preset.js` — Tailwind preset wired to the variables.
- `brand/fonts.css` — font stacks (Inter, Plus Jakarta Sans, Fira Code via Google Fonts).
- `brand/assets/` — logo (SVG + PNG sizes), favicon, and a zip of everything.
- `index.html` — the design system page. Open it to see every token and component.
- `BRAND.md` — the longer writeup: color roles, type rules, do/don't, accessibility notes.

## Use it

Plain CSS:

```html
<link rel="stylesheet" href="brand/tokens.css">
<link rel="stylesheet" href="brand/fonts.css">
<link rel="stylesheet" href="brand/components.css">
```

Tailwind:

```js
// tailwind.config.js
module.exports = { presets: [require('./brand/tailwind.preset.js')] };
```

Then `bg-bg-card`, `text-text-primary`, `border-border`, `bg-brand-green`,
`font-mono`, `rounded-card`, and so on. For focus styles use `shadow-focus`
(the ring is built to pass contrast on any surface).

## See it

Open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
# then http://localhost:8000/index.html
```

## Fonts

`fonts.css` loads Inter, Plus Jakarta Sans and Fira Code from Google Fonts. For
production you'll probably want to self-host them (next/font, @fontsource, or
just drop the woff2 files in and swap the `@import` for `@font-face`).

## Notes

The token set is a trimmed version of what scan.demos.network ships (~110 of its
~234 declarations — the ones worth reusing). If something looks off against the
live sites, the live sites win; open an issue.

Logo files come straight from the faucet and indexer repos.
