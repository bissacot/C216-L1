import {fireEvent,screen,within} from "@testing-library/react";
import {expect,it,vi} from "vitest";
import {mockHttp,openPage,ticket} from "./fixtures";

const cases=[
  ["OPEN","Iniciar atendimento","Responsável","IN_PROGRESS",{assignee:"Equipe local"}],
  ["IN_PROGRESS","Resolver chamado","Descrição da solução","RESOLVED",{resolution:"Cabo trocado"}]
];
it.each(cases)("%s exige os dados do atendimento e confirma a transição", async (initial,action,label,status,details)=>{
  let current={...ticket,status:initial};
  const change=vi.fn(({body})=>{current={...current,...body};return current;});
  mockHttp({"GET /tickets/7":()=>current,"PATCH /tickets/7/status":change,
    "GET /tickets/7/history":[{id:1,field_name:"status",old_value:"OPEN",new_value:"IN_PROGRESS",changed_by:"Ana",changed_at:ticket.opened_at}]});
  openPage("/tickets/7");
  expect(await screen.findByText("Aberto → Em atendimento")).toBeVisible();
  fireEvent.click(screen.getByRole("button",{name:action}));
  const modal=within(screen.getByRole("dialog"));
  const field=modal.getByLabelText(label);
  expect(field).toBeRequired();
  fireEvent.change(field,{target:{value:"   "}});
  fireEvent.click(modal.getByRole("button",{name:"Confirmar"}));
  expect(modal.getByRole("alert")).toHaveTextContent("obrigatório");
  expect(change).not.toHaveBeenCalled();
  fireEvent.change(field,{target:{value:Object.values(details)[0]}});
  fireEvent.click(modal.getByRole("button",{name:"Confirmar"}));
  expect(await screen.findByText("Atendimento atualizado.")).toBeVisible();
  expect(change.mock.lastCall[0].body).toEqual({status,...details});
  if (status==="RESOLVED") {
    expect(await screen.findByText("Solução registrada")).toBeVisible();
    expect(screen.queryByRole("link",{name:"Editar chamado"})).toBeNull();
    expect(screen.queryByRole("button",{name:"Cancelar chamado"})).toBeNull();
  } else {
    expect(await screen.findByRole("button",{name:"Resolver chamado"})).toBeVisible();
  }
});

it("permite desistir antes de cancelar ou excluir e atualiza a navegação após a exclusão", async ()=>{
  let current=ticket;
  const cancel=vi.fn(()=>{current={...ticket,status:"CANCELLED"};return current;});
  const remove=vi.fn(()=>new Response(null,{status:204}));
  mockHttp({"GET /tickets/7":()=>current,"PATCH /tickets/7/status":cancel,"DELETE /tickets/7":remove});
  openPage("/tickets/7");
  expect(await screen.findByRole("button",{name:"Cancelar chamado"})).toBeVisible();
  expect(screen.queryByRole("button",{name:"Excluir chamado"})).toBeNull();
  for (const [action, confirm, call] of [["Cancelar chamado","Confirmar",cancel],["Excluir chamado","Confirmar exclusão",remove]]) {
    fireEvent.click(await screen.findByRole("button",{name:action}));
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button",{name:"Voltar"}));
    expect(call).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button",{name:action}));
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button",{name:confirm}));
    expect(call).toHaveBeenCalledTimes(1);
  }
  expect(await screen.findByRole("heading",{name:"Central de chamados"})).toBeVisible();
  expect(screen.getByText("Chamado excluído.")).toBeVisible();
});
