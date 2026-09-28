/**
 * Demos Network — Tailwind preset
 * Drop-in: `presets: [require('./brand/tailwind.preset.js')]` in tailwind.config.js
 * then import ./brand/tokens.css and ./brand/fonts.css once at app root.
 *
 * Tailwind 3 preset: colors and fonts REPLACE framework defaults to enforce
 * the neutral-and-purple palette. Import tokens.css and fonts.css.
 * Use bg-bg-card, text-text-primary, border-border and focus:shadow-focus.
 */
module.exports = {
  // Legacy whole-page variant only. Mixed/nested scopes must use token utilities
  // without dark: prefixes; see BRAND.md for scope/reset semantics.
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    screens: { sm: '640px', md: '810px', lg: '1200px', xl: '1440px', '2xl': '1536px' },
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      black: '#000000',
      white: '#ffffff',
      brand: {
        violet: 'var(--brand-violet)',
        'violet-hover': 'var(--brand-violet-hover)',
        'violet-soft': 'var(--brand-violet-soft)',
        'violet-soft-hover': 'var(--brand-violet-soft-hover)',
        'violet-border': 'var(--brand-violet-border)',
        'violet-strong': 'var(--brand-violet-strong)',
        'violet-highlight': 'var(--brand-violet-highlight)',
      },
      bg: {
        letterbox: 'var(--color-bg-letterbox)',
        primary: 'var(--color-bg-primary)',
        base: 'var(--color-bg-base)',
        secondary: 'var(--color-bg-secondary)',
        subtle: 'var(--color-bg-subtle)',
        card: 'var(--color-bg-card)',
        'card-hover': 'var(--color-bg-card-hover)',
        hover: 'var(--color-bg-hover)',
        tinted: 'var(--color-bg-tinted)',
      },
      glass: {
        card: 'var(--glass-card)',
        'card-hover': 'var(--glass-card-hover)',
        panel: 'var(--glass-panel)',
        border: 'var(--glass-border)',
      },
      text: {
        primary: 'var(--color-text-primary)',
        secondary: 'var(--color-text-secondary)',
        muted: 'var(--color-text-muted)',
        faint: 'var(--color-text-faint)',
        inverse: 'var(--color-text-inverse)',
        'on-accent': 'var(--color-text-on-accent)',
        'on-accent-hover': 'var(--color-text-on-accent-hover)',
      },
      border: {
        subtle: 'var(--color-border-subtle)',
        DEFAULT: 'var(--color-border)',
        strong: 'var(--color-border-strong)',
        control: 'var(--color-border-control)',
        hover: 'var(--color-border-hover)',
      },
      success: {
        DEFAULT: 'var(--color-success)',
        soft: 'var(--color-success-soft)',
        muted: 'var(--color-success-muted)',
      },
      warning: {
        DEFAULT: 'var(--color-warning)',
        soft: 'var(--color-warning-soft)',
        muted: 'var(--color-warning-muted)',
      },
      error: {
        DEFAULT: 'var(--color-error)',
        soft: 'var(--color-error-soft)',
        muted: 'var(--color-error-muted)',
      },
      info: {
        DEFAULT: 'var(--color-info)',
        soft: 'var(--color-info-soft)',
        muted: 'var(--color-info-muted)',
      },
    },
    fontFamily: {
      sans: 'var(--font-sans)',
      serif: 'var(--font-sans)', // Compatibility alias; no additional font family.
      display: 'var(--font-display)',
      mono: 'var(--font-mono)',
    },
    // Override the framework default ring fallback as well as the palette.
    ringColor: { DEFAULT: 'var(--color-focus-ring)', brand: 'var(--color-focus-ring)' },
    extend: {
      fontWeight: { normal: 'var(--font-weight-normal)', medium: 'var(--font-weight-medium)', semibold: 'var(--font-weight-semibold)', bold: 'var(--font-weight-bold)' },
      fontSize: {
        caption: ['var(--text-caption)', { lineHeight: '1.4' }],
        label: ['var(--text-label)', { lineHeight: '1.5' }],
        base: ['var(--text-base)', { lineHeight: 'var(--leading-body)' }],
        lg: ['var(--text-lg)', { lineHeight: '1.5' }],
        xl: ['var(--text-xl)', { lineHeight: '1.4' }],
        '2xl': ['var(--text-2xl)', { lineHeight: '1.3' }],
        '3xl': ['var(--text-3xl)', { lineHeight: '1.2' }],
        hero: ['var(--text-hero)', { lineHeight: 'var(--leading-hero)', letterSpacing: 'var(--tracking-hero)' }],
        'fluid-hero': ['var(--text-fluid-hero)', { lineHeight: 'var(--leading-hero)', letterSpacing: 'var(--tracking-hero)' }],
        'fluid-h2': ['var(--text-fluid-h2)', { lineHeight: 'var(--leading-tight)', letterSpacing: 'var(--tracking-section)' }],
        'fluid-h3': 'var(--text-fluid-h3)',
        'fluid-body': 'var(--text-fluid-body)',
      },
      spacing: {
        1: 'var(--space-1)', 2: 'var(--space-2)', 3: 'var(--space-3)',
        4: 'var(--space-4)', 5: 'var(--space-5)', 6: 'var(--space-6)',
        8: 'var(--space-8)', 10: 'var(--space-10)', 12: 'var(--space-12)',
        16: 'var(--space-16)', 20: 'var(--space-20)', 24: 'var(--space-24)',
        32: 'var(--space-32)', 'card-padding': 'var(--space-card-padding)', gutter: 'var(--layout-gutter)', section: 'var(--layout-section)',
      },
      maxWidth: { content: 'var(--layout-content)' },
      letterSpacing: { tight: 'var(--tracking-tight)', wide: 'var(--tracking-wide)', eyebrow: 'var(--tracking-eyebrow)' },
      borderRadius: {
        sm: 'var(--radius-sm)', md: 'var(--radius-md)', lg: 'var(--radius-lg)',
        button: 'var(--radius-button)', chip: 'var(--radius-chip)', xl: 'var(--radius-xl)',
        card: 'var(--radius-card)', '2xl': 'var(--radius-2xl)',
        pill: 'var(--radius-pill)', full: 'var(--radius-pill)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)', md: 'var(--shadow-md)', lg: 'var(--shadow-lg)',
        // Strong purple focus ring with a theme surface offset; validate on your surface.
        focus: 'var(--focus-ring)',
      },
      backgroundImage: {
        brand: 'var(--gradient-brand)',
        'glow-hero': 'var(--glow-hero)',
        'glow-ambient': 'var(--glow-ambient)',
        vignette: 'var(--vignette)',
      },
      transitionTimingFunction: { standard: 'var(--ease-standard)' },
      transitionDuration: { fast: 'var(--duration-fast)', base: 'var(--duration-base)' },
      backdropBlur: { sm: 'var(--blur-sm)', md: 'var(--blur-md)', '2xl': 'var(--blur-2xl)' },
    },
  },
};
