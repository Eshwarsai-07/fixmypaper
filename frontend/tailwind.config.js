/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#0f2a65", dark: "#061539", light: "#1e3a8a", accent: "#d4af37" },
        ink: { DEFAULT: "#111827", soft: "#6b7280" },
        panel: { DEFAULT: "#ffffff", muted: "#fafafa" },
        line: "#e5e7eb",
      },
      fontFamily: {
        serif: ["var(--font-serif)", "serif"],
        sans: ["var(--font-sans)", "Inter", "sans-serif"],
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        card: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
        lift: "0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04)",
      },
      borderRadius: {
        card: "12px",
      },
    },
  },
  plugins: [],
};
