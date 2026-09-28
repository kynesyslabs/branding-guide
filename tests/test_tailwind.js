// Execute the preset and verify that it replaces framework color/font defaults.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const preset = require('../brand/tailwind.preset.js');
const css = fs.readFileSync(path.join(root, 'brand/tokens.css'), 'utf8');
const tokens = new Set([...css.matchAll(/(--[\w-]+)\s*:/g)].map(match => match[1]));
const colors = preset.theme.colors;
assert.ok(colors && !preset.theme.extend.colors, 'Colors must replace defaults, not extend them');
assert.deepEqual(Object.keys(colors).sort(), ['bg', 'black', 'border', 'brand', 'current', 'error', 'glass', 'info', 'success', 'text', 'transparent', 'warning', 'white'].sort());
assert.ok(!preset.theme.extend.fontFamily, 'Fonts must replace defaults');
assert.deepEqual(preset.theme.fontFamily, {
  sans: 'var(--font-sans)', serif: 'var(--font-sans)', display: 'var(--font-display)', mono: 'var(--font-mono)',
});
function walk(value) {
  if (value && typeof value === 'object') return Object.values(value).forEach(walk);
  if (typeof value !== 'string') return;
  for (const [, token] of value.matchAll(/var\((--[\w-]+)\)/g)) assert.ok(tokens.has(token), token);
}
walk(preset);
for (const [name, token] of Object.entries({ success: 'success', warning: 'warning', error: 'error', info: 'info' })) {
  assert.deepEqual(colors[name], {
    DEFAULT: `var(--color-${token})`,
    soft: `var(--color-${token}-soft)`,
    muted: `var(--color-${token}-muted)`,
  });
}
const mappedColors = new Set([...JSON.stringify(colors).matchAll(/var\((--[\w-]+)\)/g)].map(match => match[1]));
for (const token of tokens) {
  if (/^--(?:brand-|glass-|color-(?!focus-ring))/.test(token)) {
    assert.ok(mappedColors.has(token), `Missing Tailwind color mapping: ${token}`);
  }
}
assert.equal(colors.glass.border, 'var(--glass-border)');
assert.equal(colors.brand['violet-hover'], 'var(--brand-violet-hover)');
assert.equal(preset.theme.extend.borderRadius.chip, 'var(--radius-chip)');
assert.equal(preset.theme.extend.borderRadius.pill, 'var(--radius-pill)');
assert.equal(preset.theme.extend.fontSize['fluid-hero'][0], 'var(--text-fluid-hero)');
assert.equal(preset.theme.ringColor.DEFAULT, 'var(--color-focus-ring)');
assert.ok(!preset.theme.extend.ringColor, 'Focus ring must replace the framework fallback');
const vm = require('node:vm');
for (const file of ['index.html', 'brand/preview.html']) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  for (const [, script] of html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)) new vm.Script(script, {filename: file});
}
const json = JSON.parse(fs.readFileSync(path.join(root, 'brand/tokens.json'), 'utf8'));
assert.equal(json.$meta.mode, 'light');
assert.deepEqual(Object.keys(json.themes), ['light', 'dark']);
assert.equal(preset.theme.screens.md, '810px');
assert.equal(preset.theme.screens.lg, '1200px');
assert.equal(colors.brand['violet-highlight'], 'var(--brand-violet-highlight)');
assert.equal(colors.text['on-accent-hover'], 'var(--color-text-on-accent-hover)');
assert.equal(colors.border.control, 'var(--color-border-control)');
for (const theme of Object.values(json.themes)) {
  assert.equal(theme.radius.card, '20px');
  assert.equal(theme.font.weight.bold, 700);
  assert.equal(theme.letterSpacing.hero, '-0.035em');
  assert.equal(theme.lineHeight.hero, 1.04);
}
console.log('Tailwind preset: palette, font defaults, compatibility, geometry and token references passed');
