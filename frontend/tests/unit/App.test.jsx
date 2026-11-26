import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import App from "../../src/App.jsx";

afterEach(() => vi.unstubAllGlobals());

it("identifica o projeto e a finalidade da central", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
  render(<App />);
  expect(screen.getByRole("link", { name: "HelpDesk Hub" })).toBeVisible();
  expect(
    screen.getByRole("heading", { level: 1, name: "Dashboard" }),
  ).toBeVisible();
  expect(
    screen.getByText("Visão geral dos chamados e da operação de suporte."),
  ).toBeVisible();
  expect(screen.getByRole("status")).toHaveTextContent("Carregando");
  expect(await screen.findByRole("alert")).toHaveTextContent("conectar à API");
  fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
  expect(fetch).toHaveBeenCalledTimes(2);
  await screen.findByRole("alert");
});
