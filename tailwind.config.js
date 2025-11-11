module.exports = {
  content: ["./**/templates/**/*.html","./**/templates/*.html"],
  theme: { extend: {} },
  plugins: [
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("daisyui")
  ],
  daisyui: { themes: ["light", "dark"] }
}
