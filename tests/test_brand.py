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
THEMES = {theme: sync.css_tokens(theme) for theme in ('light', 'dark')}
NEUTRALS = {'000000', 'ffffff', 'f8f8f6', 'f1f1ee', 'fefefc', 'f4f4f1',
            '111118', '676770', '7c7c85', 'e4e4df', 'd2d2cc', 'bdbdb6',
            '16161e', '1c1c24', '23232c', '0b0b10', 'a1a1aa', '71717a',
            '2a2a33', '3a3a45', '52525b'}
PURPLES = {'7c3aed', '6d28d9', '8b5cf6', 'a78bfa', 'c4b5fd',
           'f7f4fe', '1b1726', 'f1ecfd', 'ede9fe'}


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
        self.assertEqual((ROOT / 'brand/tokens.json').read_text(), sync.export())
        def leaves(value):
            return sum(leaves(v) for v in value.values()) if isinstance(value, dict) else 1
        default = {k: v for k, v in actual.items() if k not in ('$meta', 'themes', 'responsive')}
        self.assertEqual(leaves(default), len(TOKENS))
        self.assertEqual(default, actual['themes']['light'])
        for theme, tokens in THEMES.items():
            self.assertEqual(leaves(actual['themes'][theme]), len(tokens))
            for name, value in tokens.items():
                leaf = actual['themes'][theme]
                for key in sync.token_path(name):
                    leaf = leaf[key]
                self.assertEqual(str(leaf), value, (theme, name))
        for width, tokens in sync.responsive_tokens().items():
            self.assertEqual(leaves(actual['responsive'][width]), len(tokens))
        self.assertEqual(actual['$meta']['mode'], 'light')
        self.assertEqual(actual['$meta']['sources'], ['http://localhost:3005/', 'https://demos.network/'])
        self.assertIn('local latest > deployed secondary', actual['$meta']['sourcePriority'])

    def test_observed_values_and_compatible_names(self):
        roles = ['color-bg-base', 'color-bg-subtle', 'color-bg-card', 'color-bg-hover',
                 'color-bg-tinted', 'color-bg-letterbox', 'color-text-primary',
                 'color-text-secondary', 'color-text-muted', 'brand-violet',
                 'brand-violet-hover', 'brand-violet-strong', 'brand-violet-highlight',
                 'color-border', 'color-border-hover', 'color-border-strong']
        expected = {
            'light': ['#f8f8f6', '#f1f1ee', '#fefefc', '#f4f4f1', '#f7f4fe', '#111118',
                      '#111118', '#676770', '#7c7c85', '#7c3aed', '#6d28d9', '#6d28d9',
                      '#6d28d9', '#e4e4df', '#d2d2cc', '#bdbdb6'],
            'dark': ['#111118', '#16161e', '#1c1c24', '#23232c', '#1b1726', '#0b0b10',
                     '#f8f8f6', '#a1a1aa', '#71717a', '#7c3aed', '#8b5cf6', '#a78bfa',
                     '#c4b5fd', '#2a2a33', '#3a3a45', '#52525b'],
        }
        for theme, tokens in THEMES.items():
            for role, value in zip(roles, expected[theme]):
                self.assertEqual(tokens['--'+role], value, (theme, role))
            for alias, original in [('bg-primary', 'bg-base'), ('bg-secondary', 'bg-subtle'),
                                    ('bg-card-hover', 'bg-hover'), ('text-faint', 'text-secondary')]:
                self.assertEqual(tokens['--color-'+alias], tokens['--color-'+original])
            for name in ('success', 'warning', 'error', 'info'):
                for suffix in ('', '-soft', '-muted'):
                    self.assertIn(f'--color-{name}{suffix}', tokens)
        for key, value in {'--radius-card': '20px', '--radius-button': '10px',
                           '--radius-chip': '6px', '--radius-pill': '9999px',
                           '--font-weight-normal': '400', '--font-weight-bold': '700',
                           '--tracking-hero': '-0.035em', '--tracking-section': '-0.035em',
                           '--leading-hero': '1.04', '--leading-tight': '1.04'}.items():
            self.assertEqual(TOKENS[key], value)

    def test_responsive_source_values(self):
        for width, hero, h2, gutter, padding in [(390, '3rem', '2.25rem', '24px', '96px'),
                (768, '3rem', '2.25rem', '24px', '96px'),
                (810, '4.75rem', '3.5rem', '40px', '144px'),
                (1199, '4.75rem', '3.5rem', '40px', '144px'),
                (1200, '5.75rem', '3.5rem', '40px', '144px'),
                (1440, '5.75rem', '3.5rem', '40px', '144px')]:
            for theme in THEMES:
                values = dict(THEMES[theme])
                for breakpoint, overrides in sync.responsive_tokens().items():
                    if width >= int(breakpoint[:-2]):
                        values.update(overrides)
                self.assertEqual([values[name] for name in ('--text-fluid-hero', '--text-fluid-h2',
                    '--layout-gutter', '--layout-section')], [hero, h2, gutter, padding], (theme, width))

    def test_theme_boundaries_reset_every_visual_token(self):
        css = sync.css_source()
        scopes = [re.search(selector + r'[^{}]*\{([^}]+)\}', css).group(1)
                  for selector in (r':root, \[data-theme="light"\]', r'\[data-theme="dark"\]')]
        declarations = [sync.declarations(scope) for scope in scopes]
        self.assertEqual(set(declarations[0]), set(declarations[1]))
        visual = {key for key in TOKENS if key.startswith(('--brand-', '--color-', '--glass-',
                  '--gradient-', '--glow-', '--shadow-', '--focus-', '--vignette'))}
        self.assertEqual(set(declarations[0]), visual)
        for mode, scope in zip(('light', 'dark'), scopes):
            self.assertIn('color-scheme: '+mode, scope)
        for alias in ('.dx-theme-dark', '.dx-theme-light', '[data-surface="ink"]'):
            self.assertIn(alias, css)

    def test_all_shipped_color_literals(self):
        sources = {str(p.relative_to(ROOT)): p.read_text() for p in ROOT.glob('brand/*.css')}
        for p in ROOT.glob('brand/assets/*.svg'):
            sources[str(p.relative_to(ROOT))] = p.read_text()
        for p in (ROOT / 'index.html', ROOT / 'brand/preview.html'):
            sources[str(p.relative_to(ROOT))] = '\n'.join(Page(p.read_text()).styles)
        sources['tokens.json'] = (ROOT / 'brand/tokens.json').read_text()
        for name in ('README.md', 'BRAND.md', 'PROVENANCE.md'):
            sources[name] = (ROOT / name).read_text().split('## Superseded public-site history')[0]
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
        self.assertRegex(font_css, r'h1, h2, h3, h4, h5, h6\s*\{[^}]*font-weight: var\(--font-weight-bold\)')
        self.assertIn('.dx-stat__value', font_css)

    def test_text_and_focus_contrast_on_supported_surfaces(self):
        def composite(color, background):
            if len(color) == 7:
                return color
            alpha = int(color[7:9], 16) / 255
            return '#' + ''.join(f'{round((fg * alpha + bg * (1-alpha)) * 255):02x}'
                                for fg, bg in zip(rgb(color), rgb(background)))
        for theme, tokens in THEMES.items():
            surfaces = [tokens['--color-bg-'+name] for name in ('base', 'subtle', 'card', 'hover', 'tinted')]
            for bg in surfaces:
                for name in ('color-text-primary', 'color-text-secondary', 'brand-violet-strong', 'brand-violet-highlight'):
                    self.assertGreaterEqual(contrast(tokens['--'+name], bg), 4.5, (theme, name, bg))
                for name in ('color-focus-ring', 'color-border-control'):
                    self.assertGreaterEqual(contrast(tokens['--'+name], bg), 3, (theme, name, bg))
                for status in ('success', 'warning', 'error', 'info'):
                    for suffix in ('soft', 'muted'):
                        fill = composite(tokens[f'--color-{status}-{suffix}'], bg)
                        self.assertGreaterEqual(contrast(tokens[f'--color-{status}'], fill), 4.5,
                                                (theme, status, suffix, bg))
            for text, fill in [('color-text-on-accent', 'brand-violet'),
                               ('color-text-on-accent-hover', 'brand-violet-hover')]:
                self.assertGreaterEqual(contrast(tokens['--'+text], tokens['--'+fill]), 4.5, (theme, text))
        css = (ROOT / 'brand/components.css').read_text()
        self.assertIn('color: var(--color-text-on-accent-hover)', css)
        self.assertRegex(css, r'\.dx-input\s*\{[^}]*border: 1px solid var\(--color-border-control\)')

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
        self.assertIn('getComputedStyle(group)', source)
        self.assertIn("['sw-', 'sw-dark-']", source)
        self.assertIn("showToast('Copy unavailable.", source)

    def test_documented_tokens_and_preview_swatches_match(self):
        guide = (ROOT / 'BRAND.md').read_text()
        for line in guide.splitlines():
            names = re.findall(r'`(--[\w-]+)`', line)
            values = re.findall(r'`(#[\da-f]{6,8})`', line)
            if names and len(values) == 2:
                for name in names:
                    for theme, value in zip(('light', 'dark'), values):
                        self.assertEqual(THEMES[theme][name], value)
        preview = (ROOT / 'brand/preview.html').read_text()
        for token, value in re.findall(r'<div class="swatch" style="background:var\((--[\w-]+)\)[^"]*">[^<]*(#[\da-f]{6})</div>', preview):
            self.assertEqual(TOKENS[token], value)

    def test_pages_show_both_themes_and_bold_left_hero(self):
        for name in ('index.html', 'brand/preview.html'):
            source = (ROOT / name).read_text()
            page = Page(source)
            self.assertTrue(any(tag == 'header' and attrs.get('data-theme') == 'dark' for tag, attrs in page.elements))
            self.assertTrue(any(tag == 'section' and attrs.get('data-theme') == 'dark' for tag, attrs in page.elements))
            self.assertTrue(any(attrs.get('data-theme') == 'light' for _, attrs in page.elements))
            self.assertNotIn('font-style:italic', source.replace(' ', ''))
            self.assertNotIn('Regular 400 headings', source)
        index = (ROOT / 'index.html').read_text()
        self.assertIn('.hero{ text-align:left;', index)
        self.assertIn('<section id="color">', index)
        self.assertIn('<section id="components" data-theme="dark">', index)

    def test_provenance_and_font_loading_documented(self):
        for name in ('README.md', 'BRAND.md', 'PROVENANCE.md', 'index.html', 'brand/preview.html'):
            source = (ROOT / name).read_text().split('## Superseded public-site history')[0]
            for phrase in ('2026-09-28', 'http://localhost:3005/', 'https://demos.network/',
                           'local latest', 'deployed secondary', 'exact color parity'):
                self.assertIn(phrase, source, (name, phrase))
            self.assertIn('deliberate', source.lower())
        for name in ('README.md', 'BRAND.md', 'PROVENANCE.md'):
            source = (ROOT / name).read_text().split('## Superseded public-site history')[0]
            for phrase in ('Plus Jakarta Sans', 'Source Code Pro', 'self-host', 'checked in Chrome'):
                self.assertIn(phrase, source)
        provenance = (ROOT / 'PROVENANCE.md').read_text()
        self.assertIn('Superseded public-site history — b9f1f44', provenance)
        self.assertIn('checked in Chrome', provenance)
        self.assertIn('1440, 768 and 390', provenance)
        self.assertIn('700-weight headings', provenance.split('## Superseded public-site history')[0])
        self.assertNotIn('parent reviewer', provenance)

    def test_private_reference_is_not_distributed(self):
        paths = assets.bundle_paths()
        for path in paths:
            self.assertNotIn('demos-local', path.name)
            if path.suffix in ('.html', '.css', '.md', '.json', '.svg'):
                source = path.read_text()
                for forbidden in ('/Users/', '/private/', '_next/static/chunks', '__nextjs-',
                                  'data-nextjs', 'source_code_pro_98e1ea32', 'plus_jakarta_sans_4f55765e'):
                    self.assertNotIn(forbidden, source, path.name)


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
                        self.assertTrue(max(abs(a - b) for a, b in zip((r, g, b), (248, 248, 246))) <= 1)

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
