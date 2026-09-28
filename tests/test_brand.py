"""Regression checks for the shipped brand contract and generated artifacts."""
import colorsys
import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


sync = module('sync_tokens')
assets = module('gen_logo_assets')
TOKENS = {key: value.strip() for key, value in sync.css_tokens().items()}
NEUTRALS = {'000000', 'ffffff', '06060a', '0a0a0f', '111118', '16161f',
            '1c1c28', '13121f', 'f0f0f5', '9ca3af', '6b7280', '0a0a0a'}
PURPLES = {'7c3aed', '8b5cf6', 'a78bfa'}


def rgb(value):
    raw = value.lstrip('#')[:6]
    return [int(raw[i:i+2], 16) / 255 for i in (0, 2, 4)]


def contrast(foreground, background):
    def luminance(value):
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb(value)]
        return sum(c * w for c, w in zip(channels, (0.2126, 0.7152, 0.0722)))
    lo, hi = sorted([luminance(foreground), luminance(background)])
    return (hi + 0.05) / (lo + 0.05)


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.elements = []
        self.styles = []
        self.ids = []
        self.text = []
        self.in_style = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'style' in attrs:
            self.styles.append(attrs['style'])
        self.in_style = self.in_style or tag == 'style'

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
        else:
            self.text.append(data)


class TokensAndPolicy(unittest.TestCase):
    def test_complete_css_json_parity(self):
        actual = json.loads((ROOT / 'brand/tokens.json').read_text())
        self.assertEqual(actual, json.loads(sync.export()))
        self.assertEqual((ROOT / 'brand/tokens.json').read_text(), sync.export())
        # Every leaf except metadata maps to exactly one CSS custom property.
        def leaves(value):
            return sum(leaves(v) for v in value.values()) if isinstance(value, dict) else 1
        self.assertEqual(leaves({k: v for k, v in actual.items() if k != '$meta'}), len(TOKENS))

    def test_observed_values_and_compatible_names(self):
        expected = {'--color-bg-base': '#0a0a0f', '--color-bg-primary': '#0a0a0f',
                    '--color-bg-subtle': '#111118', '--color-bg-secondary': '#111118',
                    '--color-bg-card': '#16161f', '--color-bg-card-hover': '#1c1c28',
                    '--color-bg-hover': '#1c1c28', '--color-text-primary': '#f0f0f5',
                    '--color-text-secondary': '#9ca3af', '--color-text-muted': '#6b7280',
                    '--brand-violet': '#7c3aed', '--brand-violet-hover': '#8b5cf6',
                    '--brand-violet-strong': '#a78bfa', '--color-border': '#ffffff14',
                    '--color-border-hover': '#ffffff29', '--color-border-strong': '#ffffff3d',
                    '--radius-card': '14px', '--radius-button': '10px', '--radius-chip': '6px',
                    '--radius-pill': '9999px', '--font-weight-normal': '400'}
        for key, value in expected.items():
            self.assertEqual(TOKENS[key], value, key)
        for name in ('success', 'warning', 'error', 'info'):
            for suffix in ('', '-soft', '-muted'):
                self.assertIn(f'--color-{name}{suffix}', TOKENS)

    def test_all_shipped_color_literals(self):
        sources = {str(p.relative_to(ROOT)): p.read_text() for p in ROOT.glob('brand/*.css')}
        for p in ROOT.glob('brand/assets/*.svg'):
            sources[str(p.relative_to(ROOT))] = p.read_text()
        for p in (ROOT / 'index.html', ROOT / 'brand/preview.html'):
            sources[str(p.relative_to(ROOT))] = '\n'.join(Page(p.read_text()).styles)
        sources['tokens.json'] = (ROOT / 'brand/tokens.json').read_text()
        for name in ('README.md', 'BRAND.md', 'PROVENANCE.md'):
            sources[name] = (ROOT / name).read_text()
        for name, content in sources.items():
            for literal in re.findall(r'(?<![\w-])#([\da-fA-F]{8}|[\da-fA-F]{6}|[\da-fA-F]{4}|[\da-fA-F]{3})(?![\w-])', content):
                expanded = ''.join(c * 2 for c in literal) if len(literal) in (3, 4) else literal
                self.assertIn(expanded[:6].lower(), NEUTRALS | PURPLES, (name, literal))
            self.assertNotRegex(content, r'\b(?:rgb|rgba|hsl|hsla|oklch|oklab|lab|lch|color-mix|color)\s*\(', name)
            # Value-position named hues must not bypass the hex policy.
            self.assertNotRegex(content, r'[:=]\s*["\']?(?:red|blue|green|cyan|yellow|orange|teal|pink|magenta)\b', name)

    def test_token_references_exist(self):
        for path in [*ROOT.glob('brand/*.css'), ROOT / 'index.html', ROOT / 'brand/preview.html']:
            for token in re.findall(r'var\((--[\w-]+)\)', path.read_text()):
                self.assertIn(token, TOKENS, (path.name, token))

    def test_only_two_authored_font_families(self):
        sans = '"Plus Jakarta Sans", system-ui, sans-serif'
        mono = '"Source Code Pro", ui-monospace, monospace'
        self.assertEqual(TOKENS['--font-sans'], sans)
        self.assertEqual(TOKENS['--font-display'], sans)
        self.assertEqual(TOKENS['--font-mono'], mono)
        font_css = (ROOT / 'brand/fonts.css').read_text()
        families = re.findall(r'family=([^&]+)', font_css)
        self.assertEqual(families, ['Plus+Jakarta+Sans:wght@400;500;600;700', 'Source+Code+Pro:wght@400;500;600;700'])
        self.assertIn('&display=swap', font_css)
        for path in [*ROOT.glob('brand/*.css'), ROOT / 'index.html', ROOT / 'brand/preview.html']:
            for value in re.findall(r'font-family\s*:\s*([^;}]+)', path.read_text()):
                self.assertRegex(value.strip(), r'^var\(--font-(sans|display|mono)\)$', path.name)
        self.assertRegex(font_css, r'h1, h2, h3, h4, h5, h6\s*\{[^}]*font-weight: var\(--font-weight-normal\)')
        self.assertIn('.dx-stat__value', font_css)

    def test_text_and_focus_contrast_on_supported_surfaces(self):
        for bg in ('#0a0a0f', '#111118', '#16161f', '#1c1c28', '#13121f'):
            for fg in ('#f0f0f5', '#9ca3af', '#a78bfa'):
                self.assertGreaterEqual(contrast(fg, bg), 4.5, (fg, bg))
            self.assertGreaterEqual(contrast(TOKENS['--color-focus-ring'], bg), 3)
            self.assertLess(contrast('#6b7280', bg), 4.5)
        self.assertGreaterEqual(contrast('#ffffff', '#7c3aed'), 4.5)
        self.assertGreaterEqual(contrast('#0a0a0a', '#8b5cf6'), 4.5)

    def test_readable_components_do_not_use_muted(self):
        self.assertNotIn('var(--color-text-muted)', (ROOT / 'brand/components.css').read_text())
        for path in (ROOT / 'index.html', ROOT / 'brand/preview.html'):
            self.assertNotIn('var(--color-text-muted)', '\n'.join(Page(path.read_text()).styles))

    def test_status_styles_and_shape_contract(self):
        css = (ROOT / 'brand/components.css').read_text()
        self.assertNotIn('.dx-pill::before', css)
        for variant in ('success', 'warning', 'error', 'info', 'neutral'):
            self.assertIn(f'.dx-pill--{variant}', css)
        self.assertRegex(css, r'\.dx-btn--marketing\s*\{[^}]*var\(--radius-pill\)')
        self.assertRegex(css, r'\.dx-badge\s*\{[^}]*var\(--radius-chip\)')
        self.assertRegex(css, r'\.dx-card\s*\{[^}]*background: var\(--color-bg-card\)')
        self.assertIn('prefers-reduced-motion: reduce', (ROOT / 'brand/tokens.css').read_text())


class PagesAndDocs(unittest.TestCase):
    def test_local_links_images_and_unique_ids(self):
        for path in (ROOT / 'index.html', ROOT / 'brand/preview.html'):
            page = Page(path.read_text())
            self.assertEqual(len(page.ids), len(set(page.ids)), path.name)
            self.assertEqual(sum(tag == 'main' for tag, _ in page.elements), 1)
            for tag, attrs in page.elements:
                for attr in ('src', 'href'):
                    value = attrs.get(attr, '')
                    if not value or urlsplit(value).scheme:
                        continue
                    url = urlsplit(value)
                    if url.path:
                        self.assertTrue((path.parent / url.path).is_file(), (path.name, value))
                    elif url.fragment:
                        self.assertIn(url.fragment, page.ids, (path.name, value))
                if tag == 'img':
                    self.assertIn('alt', attrs)
                if tag == 'label' and 'for' in attrs:
                    self.assertIn(attrs['for'], page.ids)

    def test_status_examples_have_visible_labels_and_icons(self):
        for path in (ROOT / 'index.html', ROOT / 'brand/preview.html'):
            source = path.read_text()
            pills = re.findall(r'<span class="dx-pill(?: [^"]*)?">(.*?)</span>\s*([^<]*)</span>', source, re.S)
            self.assertGreaterEqual(len(pills), 3)
            for icon, label in pills:
                self.assertIn('aria-hidden="true"', icon)
                self.assertTrue(label.strip(), path.name)
            for label in ('Live', 'Testnet', 'Down'):
                self.assertIn(label, source)

    def test_swatches_use_canonical_css(self):
        source = (ROOT / 'index.html').read_text()
        self.assertIn('tokens.getPropertyValue(varname)', source)
        self.assertIn('getComputedStyle(document.documentElement)', source)
        self.assertIn("showToast('Copy unavailable.", source)

    def test_documented_tokens_and_preview_swatches_match(self):
        guide = (ROOT / 'BRAND.md').read_text()
        for line in guide.splitlines():
            names = re.findall(r'`(--[\w-]+)`', line)
            values = re.findall(r'`(#[\da-f]{6,8})`', line)
            if names and values:
                for name in names:
                    self.assertEqual(TOKENS[name], values[0])
        preview = (ROOT / 'brand/preview.html').read_text()
        for token, value in re.findall(r'<div class="swatch" style="background:var\((--[\w-]+)\)[^"]*">[^<]*(#[\da-f]{6})</div>', preview):
            self.assertEqual(TOKENS[token], value)

    def test_provenance_and_font_limitation_documented(self):
        for name in ('README.md', 'BRAND.md', 'PROVENANCE.md', 'index.html', 'brand/preview.html'):
            source = (ROOT / name).read_text()
            self.assertIn('2026-09-28', source, name)
            self.assertIn('https://demos.network/', source, name)
            self.assertIn('exact color parity', source, name)
            self.assertIn('deliberate', source.lower(), name)
        for name in ('README.md', 'BRAND.md', 'PROVENANCE.md'):
            source = (ROOT / name).read_text()
            self.assertIn('Plus Jakarta Sans', source)
            self.assertIn('Source Code Pro', source)
            self.assertIn('self-host', source)
        provenance = (ROOT / 'PROVENANCE.md').read_text()
        for word in ('green', 'cyan', 'amber', 'red', 'blue'):
            self.assertIn(word, provenance)
        self.assertIn('radial', provenance)
        self.assertIn('checked in Chrome', provenance)
        self.assertIn('1440, 768 and 390', provenance)
        self.assertIn('Clipboard interactions remain', provenance)


class LogoAssets(unittest.TestCase):
    def test_svg_geometry_and_purple_stops(self):
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        shapes = []
        for path in (ROOT / 'brand/assets').glob('*.svg'):
            tree = ET.fromstring(path.read_text())
            self.assertEqual(tree.attrib['viewBox'], '-27.7 0 348.94 348.94')
            shapes.append(tree.find('svg:path', ns).attrib['d'])
        self.assertEqual(len(set(shapes)), 1)
        gradient = ET.fromstring((ROOT / 'brand/assets/demos-logo-gradient.svg').read_text())
        self.assertEqual([s.attrib['stop-color'] for s in gradient.findall('.//svg:stop', ns)], ['#a78bfa', '#7c3aed'])
        self.assertIn('fill="#7c3aed"', (ROOT / 'brand/assets/favicon.svg').read_text())

    def test_png_dimensions_transparency_and_palette(self):
        expected = {f'demos-logo-{variant}-{size}.png' for variant in assets.VARIANTS for size in assets.SIZES}
        self.assertEqual({p.name for p in (ROOT / 'brand/assets/png').glob('*.png')}, expected)
        for path in (ROOT / 'brand/assets/png').glob('*.png'):
            with Image.open(path) as image:
                size = int(path.stem.rsplit('-', 1)[1])
                self.assertEqual(image.size, (size, size))
                self.assertEqual(image.mode, 'RGBA')
                pixels = list(image.getdata())
                self.assertTrue(any(p[3] == 0 for p in pixels))
                self.assertTrue(any(p[3] == 255 for p in pixels))
                for r, g, b, alpha in pixels:
                    if alpha < 240:
                        continue  # Alpha-edge rounding is checked by exact SVG raster equality below.
                    if 'gradient' in path.name:
                        hue, saturation, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                        self.assertTrue(250 <= hue * 360 <= 270 and saturation > 0.25, (path.name, r, g, b))
                    else:
                        self.assertTrue(max(abs(a - b) for a, b in zip((r, g, b), (240, 240, 245))) <= 1)

    def test_pngs_match_fresh_svg_renders(self):
        for variant in assets.VARIANTS:
            for size in assets.SIZES:
                path = ROOT / f'brand/assets/png/demos-logo-{variant}-{size}.png'
                self.assertEqual(path.read_bytes(), assets.render(variant, size), path.name)

    def test_zip_exact_contents_and_determinism(self):
        path = ROOT / 'brand/assets/demos-brand-assets.zip'
        expected = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in assets.bundle_paths()}
        with zipfile.ZipFile(path) as archive:
            self.assertEqual(set(archive.namelist()), set(expected))
            self.assertEqual(len(archive.namelist()), len(expected))
            for info in archive.infolist():
                self.assertEqual(archive.read(info.filename), expected[info.filename], info.filename)
                self.assertEqual(info.date_time, assets.ZIP_DATE)
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
        self.assertEqual(path.read_bytes(), assets.bundle_bytes())
        self.assertEqual(assets.bundle_bytes(), assets.bundle_bytes())


if __name__ == '__main__':
    unittest.main()
