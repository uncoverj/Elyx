import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#f6f7fb",
        card: "#ffffff",
        text: "#1b1d2a",
        accent: "#0ea5e9",
        accent2: "#22c55e",
      },
      boxShadow: {
        soft: "0 10px 40px rgba(10, 20, 50, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
