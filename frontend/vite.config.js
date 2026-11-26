import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
import { defineConfig } from "vitest/config";
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, fileURLToPath(new URL("../", import.meta.url)), [
    "API_",
    "WEB_",
  ]);
  return {
    plugins: [react(), tailwindcss()],
    server: {
      host: "127.0.0.1",
      port: Number(process.env.WEB_PORT || env.WEB_PORT || 5180),
      strictPort: true,
      proxy: {
        "/api": {
          target:
            "http://127.0.0.1:" +
            (process.env.API_PORT || env.API_PORT || "8001"),
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
    test: {
      environment: "jsdom",
      include: ["tests/unit/**/*.test.jsx"],
      setupFiles: ["./tests/setup.js"],
    },
  };
});
