import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  globalSetup: "./tests/compose.js",
  forbidOnly: Boolean(process.env.CI),
  use: { baseURL: process.env.E2E_BASE_URL, trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile",
      testIgnore: "**/tickets.spec.js",
      use: { ...devices["Pixel 7"], defaultBrowserType: "chromium" },
    },
  ],
});
