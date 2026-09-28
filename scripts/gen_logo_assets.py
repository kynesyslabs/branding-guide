#!/usr/bin/env python3
"""Render SVG sources with librsvg and build a deterministic, complete brand ZIP.

Usage: python3 scripts/gen_logo_assets.py [--check]
Requires rsvg-convert (librsvg); see README.md for the reference version.
"""
import argparse
import io
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'brand/assets'
SIZES = (16, 32, 64, 128, 256, 512)
VARIANTS = ('white', 'gradient')
ZIP_DATE = (2026, 9, 28, 0, 0, 0)


def render(variant, size):
    return subprocess.run(
        ['rsvg-convert', '--width', str(size), '--height', str(size),
         str(ASSETS / f'demos-logo-{variant}.svg')],
        check=True, capture_output=True,
    ).stdout


def bundle_paths():
    files = [ROOT / name for name in ('README.md', 'BRAND.md', 'PROVENANCE.md', 'index.html', 'requirements-dev.txt')]
    for pattern in ('brand/*.css', 'brand/*.json', 'brand/*.js', 'brand/*.html',
                    'brand/assets/*.svg', 'brand/assets/png/*.png', 'scripts/*.py', 'tests/*.py', 'tests/*.js'):
        files.extend(ROOT.glob(pattern))
    return sorted(files)


def bundle_bytes():
    stream = io.BytesIO()
    # Stored entries avoid compression-version differences; fixed metadata avoids mtimes.
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path in bundle_paths():
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), ZIP_DATE)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare with a fresh render; write nothing.')
    args = parser.parse_args()
    if not shutil.which('rsvg-convert'):
        raise SystemExit('Missing rsvg-convert. Install librsvg as documented in README.md.')
    png = ASSETS / 'png'
    if not args.check:
        png.mkdir(exist_ok=True)
    mismatches = []
    for variant in VARIANTS:
        for size in SIZES:
            path = png / f'demos-logo-{variant}-{size}.png'
            expected = render(variant, size)
            if args.check:
                if not path.exists() or path.read_bytes() != expected:
                    mismatches.append(str(path.relative_to(ROOT)))
            else:
                path.write_bytes(expected)
    archive = ASSETS / 'demos-brand-assets.zip'
    expected = bundle_bytes()
    if args.check:
        if not archive.exists() or archive.read_bytes() != expected:
            mismatches.append(str(archive.relative_to(ROOT)))
        if mismatches:
            raise SystemExit('Stale generated artifacts: ' + ', '.join(mismatches))
        print('12 PNGs match SVG renders; ZIP contents and metadata are current')
    else:
        archive.write_bytes(expected)
        print(f'Rebuilt 12 PNGs and {archive.relative_to(ROOT)} ({len(expected):,} bytes)')


if __name__ == '__main__':
    main()
