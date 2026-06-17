#!/usr/bin/env python3
"""
Regenerate logo PNGs (16/32/64/128/256/512, white + gradient) + zip bundle
from the SVGs in brand/assets/. Requires playwright chromium.
Usage: python scripts/gen_logo_assets.py
"""
import asyncio, glob, os, zipfile
from pathlib import Path
from playwright.async_api import async_playwright

ASSETS = Path("brand/assets")
PNG = ASSETS / "png"
SIZES = [16, 32, 64, 128, 256, 512]


async def render(browser, svg, size, out):
    html = (f'<!doctype html><meta charset=utf-8>'
            f'<style>html,body{{margin:0;background:transparent}}'
            f'svg{{display:block;width:{size}px;height:{size}px}}</style>{svg}')
    pg = await browser.new_page(viewport={"width": size, "height": size})
    await pg.set_content(html, wait_until="networkidle")
    await pg.screenshot(path=str(out), omit_background=True)
    await pg.close()


async def main():
    PNG.mkdir(parents=True, exist_ok=True)
    white = (ASSETS / "demos-logo-white.svg").read_text()
    grad = (ASSETS / "demos-logo-gradient.svg").read_text()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for s in SIZES:
            await render(b, white, s, PNG / f"demos-logo-white-{s}.png")
            await render(b, grad, s, PNG / f"demos-logo-gradient-{s}.png")
        await b.close()
    # bundle: logos (svg+png) + the CSS package + tokens + tailwind preset.
    # Fonts load from Google Fonts CDN (see fonts.css) — not bundled.
    brand = ASSETS.parent  # brand/
    files = (sorted(glob.glob(str(ASSETS / "*.svg")))
             + sorted(glob.glob(str(PNG / "*.png")))
             + sorted(glob.glob(str(brand / "*.css")))
             + [str(brand / "tokens.json"), str(brand / "tailwind.preset.js")])
    zpath = ASSETS / "demos-brand-assets.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if os.path.exists(f):
                z.write(f, os.path.relpath(f, brand.parent))  # paths like brand/...
    print(f"[ok] {len(SIZES)*2} PNGs + CSS + {zpath.name} ({os.path.getsize(zpath)} b)")


if __name__ == "__main__":
    asyncio.run(main())
