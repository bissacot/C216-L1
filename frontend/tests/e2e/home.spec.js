import { expect, test } from "@playwright/test";

test("abre a página inicial do HelpDesk Hub", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/HelpDesk Hub/);
  await expect(
    page.getByRole("heading", { name: "HelpDesk Hub", level: 1 }),
  ).toBeInViewport();
  await expect(
    page.getByText("Central Inteligente de Chamados de TI"),
  ).toBeVisible();
});
