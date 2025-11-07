/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./**/templates/**/*.html",
    "./**/templates/*.html"
  ],
  theme: { extend: {} },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('daisyui')
  ],
  daisyui: {
    themes: [
      {
        armtheme: {
          "primary": "#2e5fff",
          "secondary": "#7ea1ff",
          "accent": "#22c55e",
          "neutral": "#1f2937",
          "base-100": "#0b1020",
          "base-200": "#0e1428",
          "base-300": "#111834",
          "info": "#38bdf8",
          "success": "#22c55e",
          "warning": "#fbbf24",
          "error": "#f43f5e",
        }
      },
      "light"
    ],
    darkTheme: "armtheme"
  }
}
