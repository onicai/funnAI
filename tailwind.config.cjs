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
      },
    },
  },
  plugins: [],
};
