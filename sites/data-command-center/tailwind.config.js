/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        void: '#020617',
        cyanSignal: '#22d3ee',
        violetSignal: '#a78bfa',
        amberSignal: '#f59e0b',
        panel: 'rgba(8, 18, 38, 0.68)',
      },
      fontFamily: {
        display: ['"Rajdhani"', '"Segoe UI"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"SFMono-Regular"', 'monospace'],
      },
      boxShadow: {
        holo: '0 0 0 1px rgba(34, 211, 238, 0.28), 0 24px 80px rgba(2, 6, 23, 0.55)',
      },
    },
  },
  plugins: [],
};
