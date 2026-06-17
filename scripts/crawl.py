#!/usr/bin/env python3
"""
Phase 1: Crawl target URL(s) and capture raw extraction artifacts.
Usage: python scripts/crawl.py --url https://example.com [--urls url2 url3] [--out ./ui-extracted]
"""

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Page, Browser

try:
    from playwright_stealth import stealth_async
    HAS_STEALTH = True
except ImportError:
    HAS_STEALTH = False
    print("[WARN] playwright-stealth not installed. Bot detection bypass disabled.")


VIEWPORT = {"width": 1440, "height": 900}
MOBILE_VIEWPORT = {"width": 390, "height": 844}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

STYLE_PROPS = [
    "display", "position", "flexDirection", "flexWrap", "justifyContent",
    "alignItems", "gridTemplateColumns", "gridTemplateRows", "gap",
    "width", "height", "minWidth", "maxWidth", "minHeight", "maxHeight",
    "padding", "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
    "margin", "marginTop", "marginRight", "marginBottom", "marginLeft",
    "backgroundColor", "color", "borderColor", "borderWidth", "borderStyle",
    "borderRadius", "boxShadow", "opacity", "backgroundImage",
    "fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing",
    "textDecoration", "textTransform", "backdropFilter",
    "zIndex", "overflow", "cursor", "transition",
]

COMPONENT_SELECTORS = [
    ("nav", "navigation"),
    ("header", "header"),
    ("main", "main_content"),
    ("footer", "footer"),
    ("aside", "sidebar"),
    ("h1", "heading_h1"),
    ("h2", "heading_h2"),
    ("h3", "heading_h3"),
    ("p", "paragraph"),
    ("a", "link"),
    ("button", "button"),
    ("input", "input"),
    ("textarea", "textarea"),
    ("select", "select"),
    ("img", "image"),
    ("code, pre", "code"),
    ("[class*='card']", "card"),
    ("[class*='modal']", "modal"),
    ("[class*='sidebar']", "sidebar_component"),
    ("[class*='nav']", "nav_component"),
    ("[class*='menu']", "menu"),
    ("[class*='tab']", "tab"),
    ("[class*='badge']", "badge"),
    ("[class*='avatar']", "avatar"),
    ("[class*='icon']", "icon"),
    ("[class*='btn']", "button_component"),
    ("[class*='hero']", "hero"),
    ("[class*='toast'], [class*='alert'], [role='alert']", "alert"),
    ("[class*='tooltip']", "tooltip"),
    ("[class*='dropdown']", "dropdown"),
    ("[role='dialog']", "dialog"),
    ("[class*='skeleton']", "skeleton_loader"),
]


async def detect_auth_wall(page: Page) -> bool:
    url = page.url.lower()
    title = (await page.title()).lower()
    auth_signals = ["login", "signin", "sign-in", "unauthorized", "403", "401"]
    return any(s in url or s in title for s in auth_signals)


async def extract_css_variables(page: Page) -> dict:
    return await page.evaluate("""() => {
        const vars = {};
        const sheets = [...document.styleSheets];
        for (const sheet of sheets) {
            try {
                const rules = [...sheet.cssRules || []];
                for (const rule of rules) {
                    if (rule.selectorText === ':root' || rule.selectorText === 'html') {
                        const style = rule.style;
                        for (let i = 0; i < style.length; i++) {
                            const prop = style[i];
                            if (prop.startsWith('--')) {
                                vars[prop] = style.getPropertyValue(prop).trim();
                            }
                        }
                    }
                }
            } catch (e) {}
        }
        const rootStyle = getComputedStyle(document.documentElement);
        for (let i = 0; i < rootStyle.length; i++) {
            const prop = rootStyle[i];
            if (prop.startsWith('--')) {
                vars[prop] = rootStyle.getPropertyValue(prop).trim();
            }
        }
        return vars;
    }""")


async def extract_component_styles(page: Page) -> dict:
    components = {}
    for selector, name in COMPONENT_SELECTORS:
        try:
            el = page.locator(selector).first
            count = await el.count()
            if count == 0:
                components[name] = {"found": False}
                continue
            styles = await page.evaluate(
                """([sel, props]) => {
                    const el = document.querySelector(sel);
                    if (!el) return null;
                    const cs = getComputedStyle(el);
                    const result = {};
                    for (const p of props) { result[p] = cs[p]; }
                    result._tagName = el.tagName.toLowerCase();
                    result._classList = [...el.classList].join(' ');
                    result._textSample = (el.textContent || '').trim().slice(0, 80);
                    return result;
                }""",
                [selector, STYLE_PROPS],
            )
            components[name] = {"found": True, "styles": styles}
        except Exception as e:
            components[name] = {"found": False, "error": str(e)}
    return components


async def extract_color_palette(page: Page) -> list:
    return await page.evaluate("""() => {
        const seen = new Map();
        const els = document.querySelectorAll('*');
        const sample = [...els].filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).slice(0, 400);
        for (const el of sample) {
            const cs = getComputedStyle(el);
            const tag = el.tagName.toLowerCase();
            for (const prop of ['backgroundColor', 'color', 'borderColor']) {
                const val = cs[prop];
                if (!val || val === 'rgba(0, 0, 0, 0)' || val === 'transparent') continue;
                const key = val;
                if (!seen.has(key)) {
                    seen.set(key, { value: val, usedFor: prop, exampleTag: tag, count: 1 });
                } else { seen.get(key).count++; }
            }
            const bg = cs.backgroundImage;
            if (bg && bg.includes('gradient')) {
                const key = 'gradient:' + bg.slice(0,120);
                if (!seen.has(key)) seen.set(key, { value: bg, usedFor: 'backgroundImage', exampleTag: tag, count: 1 });
                else seen.get(key).count++;
            }
        }
        return [...seen.values()].sort((a, b) => b.count - a.count).slice(0, 80);
    }""")


async def extract_typography(page: Page) -> dict:
    return await page.evaluate("""() => {
        const fonts = new Map();
        const sizes = new Map();
        const els = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,a,button,label,span,li,td,th,code')]
            .filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0 && el.textContent.trim().length > 0;
            }).slice(0, 250);
        for (const el of els) {
            const cs = getComputedStyle(el);
            const ff = cs.fontFamily, fs = cs.fontSize, fw = cs.fontWeight;
            const tag = el.tagName.toLowerCase();
            if (ff) {
                if (!fonts.has(ff)) fonts.set(ff, { family: ff, usedIn: [tag], weights: [fw] });
                else {
                    const e = fonts.get(ff);
                    if (!e.usedIn.includes(tag)) e.usedIn.push(tag);
                    if (!e.weights.includes(fw)) e.weights.push(fw);
                }
            }
            if (fs) {
                if (!sizes.has(fs)) sizes.set(fs, { size: fs, usedIn: [tag], count: 1 });
                else sizes.get(fs).count++;
            }
        }
        return {
            fontFamilies: [...fonts.values()],
            fontSizes: [...sizes.values()].sort((a,b)=>parseFloat(a.size)-parseFloat(b.size)),
        };
    }""")


async def extract_layout_zones(page: Page) -> list:
    return await page.evaluate("""() => {
        const selectors = ['header','nav','main','aside','footer',
            '[role="banner"]','[role="navigation"]','[role="main"]',
            '[role="complementary"]','[role="contentinfo"]',
            '.sidebar','.panel','.drawer','#sidebar','#main','#content'];
        const vw = window.innerWidth;
        const zones = []; const seen = new Set();
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (!el) continue;
            const r = el.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) continue;
            const key = `${Math.round(r.left)},${Math.round(r.top)}`;
            if (seen.has(key)) continue;
            seen.add(key);
            zones.push({ selector: sel, tagName: el.tagName.toLowerCase(),
                classList: [...el.classList].join(' '), role: el.getAttribute('role')||'',
                bounds: { left:Math.round(r.left), top:Math.round(r.top),
                    width:Math.round(r.width), height:Math.round(r.height),
                    widthFraction: Math.round((r.width/vw)*100) } });
        }
        return zones;
    }""")


async def extract_spacing_scale(page: Page) -> list:
    return await page.evaluate("""() => {
        const values = new Map();
        const els = [...document.querySelectorAll('*')].slice(0, 500);
        const props = ['paddingTop','paddingRight','paddingBottom','paddingLeft',
            'marginTop','marginRight','marginBottom','marginLeft','gap','rowGap','columnGap'];
        for (const el of els) {
            const cs = getComputedStyle(el);
            for (const p of props) {
                const v = cs[p];
                if (!v || v === '0px' || v === 'normal' || v === 'auto') continue;
                const px = parseFloat(v);
                if (isNaN(px) || px <= 0) continue;
                const key = Math.round(px).toString();
                values.set(key, (values.get(key)||0)+1);
            }
        }
        return [...values.entries()].sort((a,b)=>parseFloat(a[0])-parseFloat(b[0]))
            .map(([px,count])=>({px:parseInt(px),count})).filter(e=>e.count>=3);
    }""")


async def detect_framework(page: Page) -> dict:
    return await page.evaluate("""() => {
        const signals = {};
        if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || document.querySelector('[data-reactroot]')) signals.react = true;
        if (window.__NEXT_DATA__ || document.getElementById('__NEXT_DATA__')) signals.nextjs = true;
        if (window.__VUE__ || document.querySelector('[data-v-]')) signals.vue = true;
        if (window.__NUXT__) signals.nuxt = true;
        if (document.querySelector('[class^="svelte-"]')) signals.svelte = true;
        const classes = [...document.querySelectorAll('[class]')].map(el=>el.className).join(' ');
        if (/\\b(flex|grid|p-\\d|m-\\d|text-\\w+|bg-\\w+|rounded|shadow|border)\\b/.test(classes)) signals.tailwind = true;
        if (document.querySelector('[data-radix-popper-content-wrapper],[data-state]')) signals.radix = true;
        return signals;
    }""")


async def detect_dark_mode_support(page: Page) -> bool:
    return await page.evaluate("""() => {
        const sheets = [...document.styleSheets];
        for (const sheet of sheets) {
            try {
                const rules = [...sheet.cssRules || []];
                for (const rule of rules) {
                    if (rule.media && rule.media.mediaText &&
                        rule.media.mediaText.includes('prefers-color-scheme')) return true;
                }
            } catch (e) {}
        }
        return false;
    }""")


async def capture_url(browser: Browser, url: str, out_dir: Path, label: str) -> dict:
    context = await browser.new_context(viewport=VIEWPORT, user_agent=USER_AGENT, locale="en-US")
    page = await context.new_page()
    if HAS_STEALTH:
        try:
            await stealth_async(page)
        except Exception:
            pass
    print(f"  [->] Loading {url}")
    try:
        await page.goto(url, wait_until="networkidle", timeout=35000)
    except Exception as e:
        print(f"  [!] networkidle timeout -> domcontentloaded: {e}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        except Exception as e2:
            print(f"  [x] load failed: {e2}")
            await context.close()
            return {"url": url, "error": f"load_failed: {e2}", "label": label}
    await asyncio.sleep(3)

    if await detect_auth_wall(page):
        print(f"  [x] Auth wall on {url}")
        await context.close()
        return {"url": url, "error": "auth_wall", "label": label}

    page_title = await page.title()
    final_url = page.url
    print(f"  [ok] {page_title} ({final_url})")

    ss_path = out_dir / "screenshots" / f"{label}_desktop.png"
    ss_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        await page.screenshot(path=str(ss_path), full_page=True, type="png")
    except Exception as e:
        print(f"  [!] full_page screenshot failed, viewport only: {e}")
        await page.screenshot(path=str(ss_path), type="png")

    mob_path = None
    try:
        mctx = await browser.new_context(viewport=MOBILE_VIEWPORT,
            user_agent=USER_AGENT.replace("Macintosh","iPhone"), is_mobile=True)
        mp = await mctx.new_page()
        if HAS_STEALTH:
            try: await stealth_async(mp)
            except Exception: pass
        await mp.goto(url, wait_until="networkidle", timeout=20000)
        await asyncio.sleep(1.5)
        mob_path = out_dir / "screenshots" / f"{label}_mobile.png"
        await mp.screenshot(path=str(mob_path), full_page=True, type="png")
        await mctx.close()
    except Exception as e:
        print(f"  [!] mobile screenshot failed: {e}")
        mob_path = None

    supports_dark = await detect_dark_mode_support(page)

    print("  [->] Extracting design data...")
    raw = {
        "url": url, "final_url": final_url, "label": label, "title": page_title,
        "viewport": VIEWPORT,
        "framework": await detect_framework(page),
        "dark_mode_support": supports_dark,
        "css_variables": await extract_css_variables(page),
        "component_styles": await extract_component_styles(page),
        "color_palette": await extract_color_palette(page),
        "typography": await extract_typography(page),
        "layout_zones": await extract_layout_zones(page),
        "spacing_scale": await extract_spacing_scale(page),
        "screenshots": {
            "desktop": str(ss_path.relative_to(out_dir)),
            "mobile": str(mob_path.relative_to(out_dir)) if mob_path else None,
        },
    }
    await context.close()
    return raw


async def crawl(urls, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=[
            "--no-sandbox","--disable-blink-features=AutomationControlled","--disable-dev-shm-usage"])
        for i, url in enumerate(urls):
            parsed = urlparse(url)
            host = parsed.netloc.replace('.', '_')
            path = parsed.path.strip('/').replace('/', '_') or 'home'
            label = f"page_{i:02d}_{host}_{path}"
            print(f"\n[{i+1}/{len(urls)}] {url}")
            result = await capture_url(browser, url, out_dir, label)
            results.append(result)
            ap = out_dir / "raw" / f"{label}.json"
            ap.parent.mkdir(parents=True, exist_ok=True)
            ap.write_text(json.dumps(result, indent=2, default=str))
            print(f"  [ok] saved {ap}")
        await browser.close()
    (out_dir / "raw" / "manifest.json").write_text(json.dumps(results, indent=2, default=str))
    print(f"\n[ok] Crawl complete.")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--urls", nargs="*", default=[])
    ap.add_argument("--out", default="./ui-extracted")
    args = ap.parse_args()
    asyncio.run(crawl([args.url] + args.urls, Path(args.out)))


if __name__ == "__main__":
    main()
