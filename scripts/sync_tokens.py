#!/usr/bin/env python3
"""Export canonical :root CSS tokens to the compatible JSON schema."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = {
    "name": "Demos Network Brand Tokens",
    "mode": "dark",
    "sources": ["https://demos.network/"],
    "captureDate": "2026-09-28",
    "palettePolicy": "Black, white, neutrals and purple only, including statuses.",
    "provenance": "../PROVENANCE.md",
}


def css_tokens():
    css = re.sub(r'/\*.*?\*/', '', (ROOT / 'brand/tokens.css').read_text(), flags=re.S)
    root = re.search(r':root\s*\{([^}]+)\}', css).group(1)
    return dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', root))


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


def export():
    result = {'$meta': META}
    for name, raw in css_tokens().items():
        path = token_path(name)
        target = result
        for key in path[:-1]:
            target = target.setdefault(key, {})
        raw = raw.strip()
        value = json.loads(raw) if path[0] == 'lineHeight' or path[:2] == ('font', 'weight') else raw
        target[path[-1]] = value
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
