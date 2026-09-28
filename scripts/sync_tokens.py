#!/usr/bin/env python3
"""Export default, complete theme values and responsive CSS tokens to JSON."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = {
    "name": "Demos Network Brand Tokens",
    "mode": "light",
    "sources": ["http://localhost:3005/", "https://demos.network/"],
    "sourcePriority": "Owner-designated local latest > deployed secondary",
    "themes": ["light", "dark"],
    "captureDate": "2026-09-28",
    "palettePolicy": "Black, white, neutrals and purple only, including statuses.",
    "provenance": "../PROVENANCE.md",
}


def css_source():
    return re.sub(r'/\*.*?\*/', '', (ROOT / 'brand/tokens.css').read_text(), flags=re.S)


def declarations(block):
    return dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', block))


def css_tokens(theme='light'):
    if theme not in META['themes']:
        raise ValueError(f'Unknown theme: {theme}')
    css = css_source()
    common = declarations(re.search(r':root\s*\{([^}]+)\}', css).group(1))
    selector = r':root, \[data-theme="light"\]' if theme == 'light' else r'\[data-theme="dark"\]'
    overrides = declarations(re.search(selector + r'[^{}]*\{([^}]+)\}', css).group(1))
    return {**common, **overrides}


def responsive_tokens():
    return {width: declarations(block) for width, block in re.findall(
        r'@media \(min-width: (\d+px)\)\s*\{\s*:root\s*\{([^}]+)\}', css_source())}


def token_path(name):
    special = {
        '--color-border': ('color', 'border', 'default'),
        '--color-focus-ring': ('color', 'focus-ring'),
        '--focus-ring': ('focusRing',),
        '--gradient-brand': ('gradient', 'brand'),
        '--vignette': ('gradient', 'vignette'),
        '--transition': ('motion', 'transition'),
    }
    if name in special:
        return special[name]
    for prefix, path in (
        ('--brand-', ('color', 'brand')), ('--color-bg-', ('color', 'bg')),
        ('--glass-', ('color', 'glass')), ('--color-text-', ('color', 'text')),
        ('--color-border-', ('color', 'border')), ('--color-', ('color', 'status')),
        ('--glow-', ('gradient',)), ('--font-weight-', ('font', 'weight')),
        ('--font-', ('font',)), ('--text-', ('fontSize',)),
        ('--leading-', ('lineHeight',)), ('--tracking-', ('letterSpacing',)),
        ('--space-', ('space',)), ('--layout-', ('layout',)), ('--radius-', ('radius',)),
        ('--shadow-', ('shadow',)), ('--blur-', ('blur',)),
        ('--ease-', ('motion',)), ('--duration-', ('motion',)),
    ):
        if name.startswith(prefix):
            key = name[2:] if prefix in ('--glow-', '--ease-', '--duration-') else name[len(prefix):]
            return (*path, key)
    raise ValueError(f'Unmapped token: {name}')


def structure(tokens):
    result = {}
    for name, raw in tokens.items():
        path = token_path(name)
        target = result
        for key in path[:-1]:
            target = target.setdefault(key, {})
        raw = raw.strip()
        value = json.loads(raw) if path[0] == 'lineHeight' or path[:2] == ('font', 'weight') else raw
        target[path[-1]] = value
    return result


def export():
    result = {'$meta': META, **structure(css_tokens())}
    result['themes'] = {theme: structure(css_tokens(theme)) for theme in META['themes']}
    result['responsive'] = {width: structure(tokens) for width, tokens in responsive_tokens().items()}
    return json.dumps(result, indent=2) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if JSON differs; do not write.')
    args = parser.parse_args()
    path = ROOT / 'brand/tokens.json'
    expected = export()
    if args.check:
        if path.read_text() != expected:
            raise SystemExit('tokens.json is stale. Run python3 scripts/sync_tokens.py')
        print('CSS / JSON parity passed')
    else:
        path.write_text(expected)
        print('Updated brand/tokens.json')
