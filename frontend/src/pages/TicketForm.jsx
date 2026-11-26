import { ArrowLeft, Save } from "lucide-react";
import { useState } from "react";
import {
  Link,
  useNavigate,
  useOutletContext,
  useParams,
} from "react-router-dom";
import {
  Alert,
  Field,
  Options,
  PageTitle,
  Panel,
  State,
} from "../components/ui";
import { useAction, useResource } from "../hooks/resources";
import { catalogs, tickets } from "../services/api";
import { active, priorities, ticketCode } from "../utils/format";

function Form({ ticket, refs }) {
  const navigate = useNavigate(),
    { notify } = useOutletContext(),
    action = useAction();
  const [draft, set] = useState(
    ticket || {
      title: "",
      description: "",
      requester_id: "",
      category_id: "",
      priority: "MEDIUM",
      assignee: "",
    },
  );
  const [validation, setValidation] = useState("");
  const field = (name) => ({
    value: draft[name] ?? "",
    onChange: (e) => set({ ...draft, [name]: e.target.value }),
  });
  function submit(e) {
    e.preventDefault();
    const title = draft.title.trim(),
      description = draft.description.trim(),
      assignee = draft.assignee?.trim() || null;
    if (
      !title ||
      !description ||
      (ticket?.status === "IN_PROGRESS" && !assignee)
    ) {
      setValidation("Preencha os campos obrigatórios com texto.");
      return;
    }
    setValidation("");
    const body = {
      title,
      description,
      requester_id: Number(draft.requester_id),
      category_id: Number(draft.category_id),
      priority: draft.priority,
      assignee,
    };
    action.run(
      () => (ticket ? tickets.edit(ticket.id, body) : tickets.create(body)),
      (result) => {
        notify(
          ticket
            ? "Chamado atualizado."
            : "Chamado aberto. Notificações registradas para processamento.",
        );
        navigate(`/tickets/${result.id}`);
      },
    );
  }
  if (ticket && !active(ticket.status))
    return <Alert message="O chamado está encerrado e não permite edição." />;
  const missing = !refs.people.length || !refs.groups.length;
  return (
    <Panel title="Dados do chamado">
      {missing && (
        <p className="inline-note">
          Para abrir um chamado, cadastre{" "}
          <Link to="/requesters">um solicitante</Link> e{" "}
          <Link to="/categories">uma categoria</Link>.
        </p>
      )}
      <form className="form-grid" onSubmit={submit}>
        <Field label="Título">
          <input required maxLength={200} {...field("title")} />
        </Field>
        <Field label="Descrição">
          <textarea required rows={4} {...field("description")} />
        </Field>
        <div className="form-cols">
          <Field label="Solicitante">
            <select required {...field("requester_id")}>
              <option value="">Selecione o solicitante</option>
              {refs.people.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} · {v.email}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Categoria">
            <select required {...field("category_id")}>
              <option value="">Selecione a categoria</option>
              {refs.groups.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Prioridade">
            <select {...field("priority")}>
              <Options values={priorities} />
            </select>
          </Field>
          <Field label="Responsável">
            <input
              required={ticket?.status === "IN_PROGRESS"}
              maxLength={150}
              {...field("assignee")}
            />
          </Field>
        </div>
        <Alert message={validation || action.error} />
        <div className="form-actions">
          <Link
            className="button"
            to={ticket ? `/tickets/${ticket.id}` : "/tickets"}
          >
            Voltar
          </Link>
          <button
            className="button primary"
            type="submit"
            disabled={missing || action.busy}
          >
            <Save size={16} />
            {ticket ? "Salvar alterações" : "Abrir chamado"}
          </button>
        </div>
      </form>
    </Panel>
  );
}
export default function TicketForm() {
  const { id } = useParams();
  const r = useResource(`form/${id || "new"}`, async (signal) => {
    const [refs, ticket] = await Promise.all([
      catalogs(signal),
      id ? tickets.get(id, signal) : null,
    ]);
    return { refs, ticket };
  });
  return (
    <>
      <Link className="back" to={id ? `/tickets/${id}` : "/tickets"}>
        <ArrowLeft size={15} />
        Chamados
      </Link>
      <PageTitle
        title={id ? `Editar chamado ${ticketCode(id)}` : "Novo chamado"}
        description="Informe os dados da solicitação de suporte."
      />
      <State resource={r}>
        {(data) => <Form key={id || "new"} {...data} />}
      </State>
    </>
  );
}
