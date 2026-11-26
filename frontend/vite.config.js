import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5180, strictPort: true },
  test: {
    environment: "jsdom",
    include: ["tests/unit/**/*.test.jsx"],
    setupFiles: ["./tests/setup.js"],
  },
});
