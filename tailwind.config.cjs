/** @type {import('tailwindcss').Config} */
export default {
  mode: "jit",
  darkMode: 'class',
  content: ["./src/**/*.{html,js,svelte,ts}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        fredoka: ['Fredoka', 'sans-serif'],
      },
      fontWeight: {
        light: 300,
        regular: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
      },
      colors: {
        agent: {
          bg: '#0B0A0F',
          surface: '#0c0b12',
          elevated: '#15141B',
          border: 'rgba(255,255,255,0.08)',
          purple: '#653FC5',
          purpleDim: 'rgba(101,63,197,0.15)',
          muted: '#6b7280',
          soft: '#9ca3af',
        },
        dark: {
          primary: '#1f2937',
          secondary: '#374151',
          accent: '#4b5563',
        },
      },
      boxShadow: {
        agent: '0 24px 80px -20px rgba(101, 63, 197, 0.35)',
        'agent-cta': '0 0 0 1px rgba(101,63,197,0.35), 0 8px 20px -8px rgba(101,63,197,0.55)',
        'agent-soft': '0 1px 0 0 rgba(255,255,255,0.06) inset, 0 18px 40px -28px rgba(0,0,0,0.75)',
        'agent-lift': '0 22px 48px -24px rgba(101, 63, 197, 0.28), 0 18px 40px -28px rgba(0,0,0,0.8)',
      },
      backgroundImage: {
        'agent-grid':
          'linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)',
      },
      backgroundSize: {
        'agent-grid': '48px 48px',
      },
      keyframes: {
        'agent-pulse-soft': {
          '0%, 100%': { opacity: '0.45' },
          '50%': { opacity: '0.8' },
        },
      },
      animation: {
        'agent-pulse-soft': 'agent-pulse-soft 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
