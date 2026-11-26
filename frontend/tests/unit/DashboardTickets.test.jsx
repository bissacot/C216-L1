import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { emptyDashboard, group, listing, mockHttp, openPage, person, ticket } from "./fixtures";

it("mostra a base vazia e atualiza os indicadores e chamados recentes", async () => {
  const dashboard = vi.fn().mockReturnValueOnce(emptyDashboard).mockReturnValue({
    ...emptyDashboard, total: 1, by_status: {...emptyDashboard.by_status, OPEN: 1},
    by_priority: {...emptyDashboard.by_priority, HIGH: 1}, by_category: [{name:group.name,count:1}],
    recent_tickets:[ticket], average_resolution_seconds: 180
  });
  mockHttp({"GET /dashboard": dashboard});
  openPage("/");
  expect(await screen.findByText("Nenhum chamado aberto ainda")).toBeVisible();
  expect(screen.getByRole("link", {name:/Total de chamados/})).toHaveTextContent("0");
  fireEvent.click(screen.getByRole("button",{name:"Atualizar"}));
  expect(await screen.findByRole("link",{name:/Monitor apagado/})).toHaveAttribute("href","/tickets/7");
  expect(screen.getByRole("link",{name:/Abertos/})).toHaveTextContent("1");
  expect(screen.getByText("3 min")).toBeVisible();
  expect(screen.getByText(group.name)).toBeVisible();
});

it("aplica pesquisa, prioridade e ordenação, conserva filtros ao paginar e permite limpar", async () => {
  const load = vi.fn(({query}) => {
    if (query.get("q")==="monitor") return listing([query.get("page")==="2" ? {...ticket,title:"Segundo monitor"} : ticket], Number(query.get("page")),11);
    return listing([]);
  });
  mockHttp({"GET /tickets":load});
  openPage("/tickets");
  expect(await screen.findByText("Nenhum chamado encontrado")).toBeVisible();
  fireEvent.change(screen.getByRole("searchbox"),{target:{value:" monitor "}});
  fireEvent.change(screen.getByRole("combobox",{name:"Prioridade"}),{target:{value:"HIGH"}});
  fireEvent.change(screen.getByRole("combobox",{name:"Ordenar por"}),{target:{value:"title"}});
  fireEvent.change(screen.getByRole("combobox",{name:"Ordem"}),{target:{value:"asc"}});
  fireEvent.click(screen.getByRole("button",{name:"Aplicar filtros"}));
  const row = await screen.findByRole("row",{name:/Monitor apagado/});
  expect(within(row).getByText(person.name)).toBeVisible();
  expect(within(row).getByText(group.name)).toBeVisible();
  fireEvent.click(screen.getByRole("button",{name:"Próxima página"}));
  expect(await screen.findByText("Segundo monitor")).toBeVisible();
  expect(Object.fromEntries(load.mock.lastCall[0].query)).toMatchObject({q:"monitor",page:"2",priority:"HIGH",sort_by:"title",order:"asc"});
  expect(screen.getByRole("button",{name:"Próxima página"})).toBeDisabled();
  fireEvent.click(screen.getByRole("button",{name:"Limpar"}));
  expect(await screen.findByText("Nenhum chamado encontrado")).toBeVisible();
  expect(screen.getByRole("searchbox")).toHaveValue("");
});

it("recupera a listagem após uma falha HTTP do proxy", async () => {
  mockHttp({"GET /tickets":vi.fn().mockReturnValueOnce(new Response("Bad Gateway",{status:502})).mockReturnValue(listing([ticket]))});
  openPage("/tickets");
  expect(await screen.findByRole("alert")).toHaveTextContent("Serviço indisponível");
  fireEvent.click(screen.getByRole("button",{name:"Tentar novamente"}));
  expect(await screen.findByText(ticket.title)).toBeVisible();
  await waitFor(()=>expect(screen.queryByRole("alert")).toBeNull());
});

it("retorna ao dashboard por uma rota inválida e navega pelos indicadores", async () => {
  mockHttp();
  openPage("/inexistente");
  expect(screen.getByRole("heading",{name:"Página não encontrada"})).toBeVisible();
  fireEvent.click(screen.getByRole("link",{name:"Voltar ao dashboard"}));
  fireEvent.click(await screen.findByRole("link",{name:/Total de chamados/}));
  expect(await screen.findByRole("row",{name:/Monitor apagado/})).toBeVisible();
});
