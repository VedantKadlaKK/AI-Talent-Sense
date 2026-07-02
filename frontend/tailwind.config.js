/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18202f",
        mist: "#eef2f7",
        cobalt: "#1d4ed8",
        ember: "#b45309",
        pine: "#166534",
      },
      boxShadow: {
        panel: "0 1px 2px rgba(16, 24, 40, 0.08)",
      },
    },
  },
  plugins: [],
};
