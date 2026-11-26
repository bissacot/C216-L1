import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// O jsdom não implementa os métodos nativos de <dialog>. O Chromium cobre o modal real.
if (!HTMLDialogElement.prototype.showModal) {
  Object.assign(HTMLDialogElement.prototype, {
    showModal() { this.open = true; },
    close() { this.open = false; },
  });
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
