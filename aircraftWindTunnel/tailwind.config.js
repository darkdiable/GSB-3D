/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        'wind-tunnel': {
          'bg': '#0a1628',
          'panel': 'rgba(10, 22, 40, 0.85)',
          'border': 'rgba(0, 212, 255, 0.3)',
          'high-speed': '#00d4ff',
          'mid-speed': '#9d4edd',
          'low-speed': '#ff6b35',
          'text': '#e0f2fe',
          'text-secondary': '#94a3b8',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
        'display': ['Orbitron', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(0, 212, 255, 0.3)',
        'glow-lg': '0 0 40px rgba(0, 212, 255, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
};
