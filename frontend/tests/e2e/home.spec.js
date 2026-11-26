import { expect, test } from "@playwright/test";

test("abre a página inicial do HelpDesk Hub", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/HelpDesk Hub/);
  await expect(
    page.getByRole("heading", { name: "Dashboard", level: 1 }),
  ).toBeInViewport();
  await expect(
    page.getByText("Visão geral dos chamados e da operação de suporte."),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: /Total de chamados/ }),
  ).toBeVisible();
});
