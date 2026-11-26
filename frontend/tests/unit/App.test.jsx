import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import App from "../../src/App.jsx";

it("identifica o projeto e a finalidade da central", () => {
  render(<App />);
  expect(
    screen.getByRole("heading", { level: 1, name: "HelpDesk Hub" }),
  ).toBeVisible();
  expect(
    screen.getByText("Central Inteligente de Chamados de TI"),
  ).toBeVisible();
});
