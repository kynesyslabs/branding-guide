/**
 * Demos Network — Tailwind preset
 * Drop-in: `presets: [require('./brand/tailwind.preset.js')]` in tailwind.config.js
 * then import ./brand/tokens.css and ./brand/fonts.css once at app root.
 *
 * Colors map to the CSS variables so theme switching (dark/light) works
 * without rebuilding. Use e.g. bg-bg-card, text-text-primary, border-border,
 * bg-brand-violet, ring-brand-violet/30, etc.
 */
module.exports = {
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        brand: {
          violet: 'var(--brand-violet)',
          'violet-strong': 'var(--brand-violet-strong)',
        },
        bg: {
          letterbox: 'var(--color-bg-letterbox)',
          primary: 'var(--color-bg-primary)',
          base: 'var(--color-bg-base)',
          secondary: 'var(--color-bg-secondary)',
          card: 'var(--color-bg-card)',
          'card-hover': 'var(--color-bg-card-hover)',
          hover: 'var(--color-bg-hover)',
          tinted: 'var(--color-bg-tinted)',
        },
        glass: {
          card: 'var(--glass-card)',
          'card-hover': 'var(--glass-card-hover)',
          panel: 'var(--glass-panel)',
        },
        text: {
          primary: 'var(--color-text-primary)',
          secondary: 'var(--color-text-secondary)',
          muted: 'var(--color-text-muted)',
          faint: 'var(--color-text-faint)',
          inverse: 'var(--color-text-inverse)',
        },
        border: {
          subtle: 'var(--color-border-subtle)',
          DEFAULT: 'var(--color-border)',
          strong: 'var(--color-border-strong)',
          hover: 'var(--color-border-hover)',
        },
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        info: 'var(--color-info)',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        display: 'var(--font-display)',
        mono: 'var(--font-mono)',
      },
      fontSize: {
        caption: ['var(--text-caption)', { lineHeight: '1.4' }],
        label: ['var(--text-label)', { lineHeight: '1.5' }],
        base: ['var(--text-base)', { lineHeight: 'var(--leading-body)' }],
        lg: ['var(--text-lg)', { lineHeight: '1.5' }],
        xl: ['var(--text-xl)', { lineHeight: '1.4' }],
        '2xl': ['var(--text-2xl)', { lineHeight: '1.3' }],
        '3xl': ['var(--text-3xl)', { lineHeight: '1.2' }],
        hero: ['var(--text-hero)', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
        'fluid-hero': 'var(--text-fluid-hero)',
        'fluid-h2': 'var(--text-fluid-h2)',
        'fluid-h3': 'var(--text-fluid-h3)',
        'fluid-body': 'var(--text-fluid-body)',
      },
      spacing: {
        1: 'var(--space-1)', 2: 'var(--space-2)', 3: 'var(--space-3)',
        4: 'var(--space-4)', 5: 'var(--space-5)', 6: 'var(--space-6)',
        8: 'var(--space-8)', 10: 'var(--space-10)', 12: 'var(--space-12)',
        16: 'var(--space-16)', 20: 'var(--space-20)', 24: 'var(--space-24)',
        32: 'var(--space-32)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)', md: 'var(--radius-md)', lg: 'var(--radius-lg)',
        button: 'var(--radius-button)', xl: 'var(--radius-xl)',
        card: 'var(--radius-card)', '2xl': 'var(--radius-2xl)',
        pill: 'var(--radius-pill)', full: 'var(--radius-pill)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)', md: 'var(--shadow-md)', lg: 'var(--shadow-lg)',
        // Two-layer focus ring matching --focus-ring. Use `shadow-focus` instead
        // of `ring-brand` — the ring-* utilities are single-layer and won't
        // reproduce the 1px dark offset that carries WCAG SC 1.4.11 on any surface.
        focus: 'var(--focus-ring)',
      },
      backgroundImage: {
        'glow-hero': 'var(--glow-hero)',
        'glow-ambient': 'var(--glow-ambient)',
        vignette: 'var(--vignette)',
      },
      ringColor: { brand: 'var(--color-focus-ring)' },
      transitionTimingFunction: { standard: 'var(--ease-standard)' },
      transitionDuration: { fast: 'var(--duration-fast)', base: 'var(--duration-base)' },
      backdropBlur: { sm: 'var(--blur-sm)', md: 'var(--blur-md)', '2xl': 'var(--blur-2xl)' },
    },
  },
};
