#!/usr/bin/env python3
"""
Phase 2: Normalize raw crawl artifacts into structured design system JSON.
Usage: python scripts/analyze.py --raw ./ui-extracted/raw --out ./ui-extracted
"""

import argparse
import json
import re
import colorsys
from pathlib import Path
from collections import Counter


def parse_color_value(value):
    value = value.strip()
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', value)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        hex_val = f"#{r:02x}{g:02x}{b:02x}"
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        return {"raw": value, "hex": hex_val, "r": r, "g": g, "b": b, "alpha": a,
                "hue": round(h*360), "saturation": round(s*100), "lightness": round(v*100)}
    m = re.match(r'#([0-9a-fA-F]{3,8})', value)
    if m:
        h = m.group(1)
        if len(h) == 3: h = ''.join(c*2 for c in h)
        if len(h) >= 6:
            r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
            hh, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            return {"raw": value, "hex": f"#{h[:6]}", "r": r, "g": g, "b": b, "alpha": 1.0,
                    "hue": round(hh*360), "saturation": round(s*100), "lightness": round(v*100)}
    return None


def is_neutral(c):
    return c["saturation"] < 12


def deduplicate_colors(palette):
    parsed = []
    gradients = []
    for entry in palette:
        val = entry.get("value", "")
        if "gradient" in val:
            gradients.append({"value": val, "count": entry.get("count", 1)})
            continue
        c = parse_color_value(val)
        if c and c.get("alpha", 1.0) > 0.05:
            c["count"] = entry.get("count", 1)
            c["usedFor"] = entry.get("usedFor", "unknown")
            parsed.append(c)
    brand = [c for c in parsed if not is_neutral(c)]
    neutrals = [c for c in parsed if is_neutral(c)]
    brand.sort(key=lambda c: c["count"], reverse=True)
    neutrals.sort(key=lambda c: c["lightness"])
    return {"brand": brand[:12], "neutrals": neutrals[:14],
            "gradients": gradients[:6], "raw_count": len(parsed)}


def extract_font_scale(typo):
    sizes = typo.get("fontSizes", [])
    vals = []
    for e in sizes:
        px = round(float(re.sub(r'[^\d.]', '', e.get("size","0")) or 0))
        if px > 0:
            vals.append({"px": px, "rem": round(px/16,4),
                         "usedIn": e.get("usedIn",[]), "count": e.get("count",1)})
    seen = {}
    for e in vals:
        px = e["px"]
        if px not in seen or e["count"] > seen[px]["count"]:
            seen[px] = e
    scale = sorted(seen.values(), key=lambda e: e["px"])
    if scale:
        median = scale[len(scale)//2]["px"]
        for e in scale:
            px = e["px"]
            if px <= 10: e["semantic"]="xs"
            elif px <= 12: e["semantic"]="sm"
            elif px <= median-2: e["semantic"]="base-small"
            elif px <= median+2: e["semantic"]="base"
            elif px <= 20: e["semantic"]="lg"
            elif px <= 28: e["semantic"]="xl"
            elif px <= 36: e["semantic"]="2xl"
            else: e["semantic"]="3xl+"
    fonts = typo.get("fontFamilies", [])
    return {"scale": scale, "families": fonts,
            "primary_family": fonts[0]["family"] if fonts else "sans-serif",
            "mono_family": next((f["family"] for f in fonts if any(
                kw in f["family"].lower() for kw in ["mono","code","courier","consolas"])), "monospace")}


def infer_spacing_scale(raw):
    if not raw: return {"base": 4, "scale": [], "system": "unknown"}
    values = sorted(set(e["px"] for e in raw if e["px"] > 0))
    small = [v for v in values if v <= 8]
    if 4 in small: base = 4
    elif 5 in small: base = 5
    elif 8 in small and 4 not in small: base = 8
    else: base = 4
    named = []
    for v in values:
        named.append({"px": v, "multiple": round(v/base,1),
                      "name": f"space-{int(v/base)}" if v%base==0 else f"space-{v}px"})
    return {"base": base, "scale": named, "system": f"base-{base}"}


def normalize_layout_zones(zones, vp):
    vw = vp.get("width", 1440)
    out = []
    for z in zones:
        b = z.get("bounds", {})
        w, left = b.get("width",0), b.get("left",0)
        if w/vw > 0.7: pos = "full-width"
        elif left < 50 and w/vw < 0.35: pos = "left-sidebar"
        elif left > vw*0.65 and w/vw < 0.35: pos = "right-sidebar"
        else: pos = "centered"
        cl = z.get("classList","")
        out.append({"selector": z.get("selector"), "tagName": z.get("tagName"),
                    "role": z.get("role") or (cl.split()[0] if cl else ""),
                    "position": pos, "widthPx": w, "heightPx": b.get("height",0),
                    "widthPercent": round(w/vw*100), "bounds": b})
    return out


def extract_border_radius(comps):
    radii = Counter()
    for name, c in comps.items():
        if not c.get("found"): continue
        br = (c.get("styles") or {}).get("borderRadius","")
        if br and br != "0px": radii[br] += 1
    return [{"value": v, "count": cnt} for v, cnt in radii.most_common(8)]


def extract_shadows(comps):
    sh = Counter()
    for name, c in comps.items():
        if not c.get("found"): continue
        bs = (c.get("styles") or {}).get("boxShadow","")
        if bs and bs != "none": sh[bs] += 1
    return [{"value": v, "count": cnt} for v, cnt in sh.most_common(8)]


def analyze_single(raw):
    return {
        "url": raw.get("url"), "label": raw.get("label"), "title": raw.get("title"),
        "framework": raw.get("framework",{}), "dark_mode_support": raw.get("dark_mode_support",False),
        "screenshots": raw.get("screenshots",{}),
        "layout": {"zones": normalize_layout_zones(raw.get("layout_zones",[]),
                                                    raw.get("viewport",{"width":1440})),
                   "viewport": raw.get("viewport")},
        "tokens": {
            "colors": deduplicate_colors(raw.get("color_palette",[])),
            "css_variables": raw.get("css_variables",{}),
            "typography": extract_font_scale(raw.get("typography",{})),
            "spacing": infer_spacing_scale(raw.get("spacing_scale",[])),
            "borderRadius": extract_border_radius(raw.get("component_styles",{})),
            "shadows": extract_shadows(raw.get("component_styles",{})),
        },
        "components": raw.get("component_styles",{}),
    }


def merge_analyses(analyses):
    if not analyses: return {}
    primary = analyses[0]
    all_brand = {}
    for a in analyses:
        for c in a["tokens"]["colors"]["brand"]:
            k = c.get("hex", c.get("raw",""))
            if k not in all_brand or c["count"] > all_brand[k]["count"]:
                all_brand[k] = c
    all_neutral = {}
    for a in analyses:
        for c in a["tokens"]["colors"]["neutrals"]:
            k = c.get("hex", c.get("raw",""))
            if k not in all_neutral or c["count"] > all_neutral[k]["count"]:
                all_neutral[k] = c
    all_grad = {}
    for a in analyses:
        for g in a["tokens"]["colors"].get("gradients",[]):
            all_grad[g["value"]] = g
    all_vars = {}
    for a in analyses:
        all_vars.update(a["tokens"]["css_variables"])
    all_spacing = {}
    for a in analyses:
        for e in a["tokens"]["spacing"]["scale"]:
            all_spacing.setdefault(e["px"], e)
    all_radius = Counter()
    for a in analyses:
        for r in a["tokens"]["borderRadius"]:
            all_radius[r["value"]] += r["count"]
    all_shadow = Counter()
    for a in analyses:
        for s in a["tokens"].get("shadows",[]):
            all_shadow[s["value"]] += s["count"]
    return {
        "source_urls": [a["url"] for a in analyses],
        "primary_url": primary["url"],
        "frameworks": {a["label"]: a["framework"] for a in analyses},
        "dark_mode_support": any(a["dark_mode_support"] for a in analyses),
        "screenshots": {a["label"]: a["screenshots"] for a in analyses},
        "layouts": {a["label"]: a["layout"] for a in analyses},
        "tokens": {
            "colors": {
                "brand": sorted(all_brand.values(), key=lambda c: c["count"], reverse=True),
                "neutrals": sorted(all_neutral.values(), key=lambda c: c["lightness"]),
                "gradients": list(all_grad.values()),
            },
            "css_variables": all_vars,
            "typography": primary["tokens"]["typography"],
            "typography_all": {a["label"]: a["tokens"]["typography"] for a in analyses},
            "spacing": {**primary["tokens"]["spacing"],
                        "scale": sorted(all_spacing.values(), key=lambda e: e["px"])},
            "borderRadius": [{"value":v,"count":c} for v,c in all_radius.most_common(10)],
            "shadows": [{"value":v,"count":c} for v,c in all_shadow.most_common(10)],
        },
        "components": {a["label"]: a["components"] for a in analyses},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="./ui-extracted/raw")
    ap.add_argument("--out", default="./ui-extracted")
    args = ap.parse_args()
    raw_dir, out_dir = Path(args.raw), Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((raw_dir / "manifest.json").read_text())
    valid = [r for r in manifest if "error" not in r]
    errored = [r for r in manifest if "error" in r]
    if errored:
        print(f"[!] Skipping errored: {[(e['url'],e['error']) for e in errored]}")
    print(f"[->] Analyzing {len(valid)} page(s)...")
    analyses = [analyze_single(r) for r in valid]
    ds = merge_analyses(analyses)
    (out_dir / "design_system.json").write_text(json.dumps(ds, indent=2, default=str))
    print(f"[ok] design_system.json saved")


if __name__ == "__main__":
    main()
