import { fireEvent, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { group, listing, mockHttp, openPage, person, ticket } from "./fixtures";

it("bloqueia a abertura quando falta uma categoria e oferece o cadastro", async () => {
  mockHttp({ "GET /categories": listing([]) });
  openPage("/tickets/new");
  expect(
    await screen.findByRole("button", { name: "Abrir chamado" }),
  ).toBeDisabled();
  expect(screen.getByRole("link", { name: "uma categoria" })).toHaveAttribute(
    "href",
    "/categories",
  );
});

it("valida, conserva o rascunho após 422 e abre uma única solicitação ao reenviar", async () => {
  const pending = Promise.withResolvers();
  const save = vi
    .fn()
    .mockReturnValueOnce(
      Response.json(
        { detail: [{ loc: ["body", "title"], msg: "Título inválido" }] },
        { status: 422 },
      ),
    )
    .mockReturnValueOnce(pending.promise);
  mockHttp({ "POST /tickets": save });
  openPage("/tickets/new");
  const submit = await screen.findByRole("button", { name: "Abrir chamado" });
  const title = screen.getByLabelText("Título"),
    description = screen.getByLabelText("Descrição");
  expect(title).toBeRequired();
  expect(description).toBeInvalid();
  fireEvent.change(title, { target: { value: "   " } });
  fireEvent.change(description, { target: { value: "Testar sinal" } });
  fireEvent.change(screen.getByRole("combobox", { name: "Solicitante" }), {
    target: { value: String(person.id) },
  });
  fireEvent.change(screen.getByRole("combobox", { name: "Categoria" }), {
    target: { value: String(group.id) },
  });
  fireEvent.click(submit);
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "campos obrigatórios",
  );
  expect(save).not.toHaveBeenCalled();
  fireEvent.change(title, { target: { value: "  Monitor apagado  " } });
  fireEvent.click(submit);
  expect(await screen.findByText("title: Título inválido")).toBeVisible();
  expect(description).toHaveValue("Testar sinal");
  expect(title).toHaveValue("  Monitor apagado  ");
  fireEvent.click(submit);
  expect(submit).toBeDisabled();
  fireEvent.submit(submit.form);
  expect(save).toHaveBeenCalledTimes(2);
  expect(save.mock.lastCall[0].body).toEqual({
    title: ticket.title,
    description: "Testar sinal",
    priority: "MEDIUM",
    assignee: null,
    category_id: group.id,
    requester_id: person.id,
  });
  pending.resolve(ticket);
  expect(
    await screen.findByText(/Chamado aberto\. Notificações/),
  ).toBeVisible();
  expect(
    await screen.findByRole("heading", { name: ticket.title }),
  ).toBeVisible();
});

it("carrega as opções das páginas seguintes e salva a edição em atendimento com responsável", async () => {
  const edit = vi.fn().mockReturnValue(ticket);
  const next = { ...person, id: 17, name: "Pessoa adicional" };
  mockHttp({
    "GET /requesters": ({ query }) =>
      listing(
        query.get("page") === "2" ? [next] : [person],
        Number(query.get("page")),
        2,
      ),
    "GET /tickets/7": {
      ...ticket,
      status: "IN_PROGRESS",
      assignee: "Equipe A",
    },
    "PUT /tickets/7": edit,
  });
  openPage("/tickets/7/edit");
  expect(await screen.findByDisplayValue(ticket.title)).toBeVisible();
  expect(
    screen.getByRole("option", { name: /Pessoa adicional/ }),
  ).toBeInTheDocument();
  const responsible = screen.getByLabelText("Responsável");
  fireEvent.change(responsible, { target: { value: " " } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("obrigatórios");
  expect(edit).not.toHaveBeenCalled();
  fireEvent.change(responsible, { target: { value: "Equipe B" } });
  fireEvent.click(screen.getByRole("button", { name: "Salvar alterações" }));
  expect(await screen.findByText("Chamado atualizado.")).toBeVisible();
  expect(edit.mock.lastCall[0].body).toMatchObject({
    title: ticket.title,
    assignee: "Equipe B",
  });
});

it.each(["RESOLVED", "CANCELLED"])(
  "impede edição direta de chamado %s",
  async (status) => {
    mockHttp({ "GET /tickets/7": { ...ticket, status } });
    openPage("/tickets/7/edit");
    expect(await screen.findByRole("alert")).toHaveTextContent("encerrado");
    expect(
      screen.queryByRole("button", { name: "Salvar alterações" }),
    ).toBeNull();
  },
);
