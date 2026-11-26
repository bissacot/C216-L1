import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import { AppRoutes } from "../../src/App";

export const person = {id: 2, name: "Ana Lima", email: "ana@example.invalid", department: "Suporte"};
export const group = {id: 3, name: "Laboratório", description: "Infraestrutura"};
export const ticket = {
  id: 7, title: "Monitor apagado", description: "Verificar o cabo",
  requester_id: person.id, category_id: group.id, priority: "HIGH",
  status: "OPEN", assignee: null, opened_at: "2026-01-15T14:00:00Z"
};
export const emptyDashboard = {
  total: 0, by_status: {OPEN: 0, IN_PROGRESS: 0, RESOLVED: 0, CANCELLED: 0},
  by_priority: {LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0}, by_category: [],
  active_critical: 0, average_resolution_seconds: null, recent_tickets: [],
  notifications: {PENDING: 0, SENT: 0, FAILED: 0}
};
export function listing(items, page = 1, total = items.length) {
  return {items, page, total, page_size: 10};
}

export function mockHttp(overrides = {}) {
  const routes = {
    "GET /dashboard": emptyDashboard,
    "GET /requesters": listing([person]), "GET /categories": listing([group]),
    "GET /requesters/2": person, "GET /categories/3": group,
    "GET /tickets": listing([ticket]), "GET /tickets/7": ticket,
    "GET /tickets/7/history": [], "GET /tickets/7/notifications": [],
    "GET /notifications": listing([]),
    "GET /notifications/channels": {EMAIL: "DISABLED", TEAMS: "MOCK"}, ...overrides,
  };
  const fetchMock = vi.fn(async (input, init) => {
    const url = new URL(input, "http://localhost");
    const key = `${init.method} ${url.pathname.replace(/^\/api/, "")}`;
    if (!(key in routes)) throw new Error(`Requisição inesperada: ${key}`);
    const handler = routes[key];
    const value = typeof handler === "function"
      ? await handler({query: url.searchParams, body: init.body && JSON.parse(init.body)})
      : handler;
    return value instanceof Response ? value : Response.json(value);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

export function openPage(path) {
  return render(<MemoryRouter initialEntries={[path]}><AppRoutes /></MemoryRouter>);
}
