/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm, appetizing color palette
        'terracotta': {
          50: '#fdf6f3',
          100: '#fbeae4',
          200: '#f8d5c9',
          300: '#f2b6a1',
          400: '#e98d6f',
          500: '#df6b47',
          600: '#cc5030',
          700: '#ab4028',
          800: '#8d3726',
          900: '#753224',
        },
        'sage': {
          50: '#f6f7f4',
          100: '#e9ece4',
          200: '#d4daca',
          300: '#b6c2a7',
          400: '#96a77f',
          500: '#788c61',
          600: '#5e704b',
          700: '#4a583d',
          800: '#3d4834',
          900: '#343d2d',
        },
        'cream': {
          50: '#fefdfb',
          100: '#fdf9f3',
          200: '#faf3e6',
          300: '#f5e8d3',
          400: '#edd8b8',
          500: '#e2c49a',
          600: '#d4ab77',
          700: '#c08f58',
          800: '#a1754a',
          900: '#856240',
        },
        'espresso': {
          50: '#f7f5f4',
          100: '#edebe8',
          200: '#dbd6d1',
          300: '#c3bab2',
          400: '#a89b90',
          500: '#928374',
          600: '#857568',
          700: '#6f6157',
          800: '#5d524a',
          900: '#4d4540',
        },
      },
      fontFamily: {
        'display': ['"Playfair Display"', 'Georgia', 'serif'],
        'body': ['"DM Sans"', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [],
}

