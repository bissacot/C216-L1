import { useRef, useState } from "react";
import AlunoForm from "./components/AlunoForm.jsx";
import AlunoList from "./components/AlunoList.jsx";
import DeleteDialog from "./components/DeleteDialog.jsx";

export default function App() {
  const [alunos, setAlunos] = useState([]);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const nextId = useRef(1);
  const formArea = useRef(null);
  const filtered = alunos.filter((aluno) =>
    [aluno.nome, aluno.email, aluno.curso].some((value) =>
      value
        .toLocaleLowerCase("pt-BR")
        .includes(search.trim().toLocaleLowerCase("pt-BR")),
    ),
  );

  function saveAluno(values) {
    if (editing) {
      setAlunos((current) =>
        current.map((aluno) =>
          aluno.id === editing.id ? { ...values, id: aluno.id } : aluno,
        ),
      );
      setEditing(null);
      setMessage("Aluno atualizado com sucesso.");
    } else {
      const id = nextId.current++;
      setAlunos((current) => [...current, { ...values, id }]);
      setMessage("Aluno cadastrado com sucesso.");
    }
  }

  function editAluno(aluno) {
    setEditing(aluno);
    setMessage("");
    formArea.current.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function deleteAluno() {
    setAlunos((current) => current.filter((aluno) => aluno.id !== deleting.id));
    if (editing?.id === deleting.id) setEditing(null);
    setDeleting(null);
    setMessage("Aluno excluído com sucesso.");
    document.getElementById("search").focus();
  }

  return (
    <>
      <a
        href="#main"
        className="sr-only rounded bg-white p-3 focus:not-sr-only focus:absolute focus:z-10"
      >
        Ir para o conteúdo
      </a>
      <header className="bg-[#172e29] text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-10">
          <div className="flex items-center gap-3">
            <span
              aria-hidden="true"
              className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#d5e8aa] text-xl text-[#172e29]"
            >
              ⌘
            </span>
            <span className="text-xl font-semibold tracking-tight">
              campus<span className="text-[#d5e8aa]">.</span>
            </span>
          </div>
          <span className="rounded-full border border-white/20 px-3 py-1.5 text-xs text-stone-200">
            C216 · Gestão acadêmica
          </span>
        </div>
      </header>
      <main
        id="main"
        className="mx-auto max-w-7xl px-5 py-10 sm:px-10 sm:py-14"
      >
        <div className="mb-9 flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-800">
              Pessoas que fazem o futuro
            </p>
            <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
              Gestão de alunos
            </h1>
            <p className="mt-4 max-w-lg text-sm leading-6 text-stone-600">
              Cada aluno, uma nova possibilidade. Organize os cadastros e
              mantenha sua turma por perto.
            </p>
          </div>
          <div className="flex items-center gap-4 rounded-xl border border-stone-200 bg-white px-5 py-4">
            <span className="text-3xl font-semibold tabular-nums">
              {alunos.length.toString().padStart(2, "0")}
            </span>
            <span className="text-xs leading-5 text-stone-500">
              Alunos
              <br />
              cadastrados
            </span>
          </div>
        </div>
        <div
          role="status"
          aria-live="polite"
          className={
            message
              ? "mb-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
              : "sr-only"
          }
        >
          {message}
        </div>
        <div className="grid items-start gap-7 lg:grid-cols-[360px_minmax(0,1fr)]">
          <div ref={formArea} className="scroll-mt-6">
            <AlunoForm
              key={editing?.id ?? "new"}
              aluno={editing}
              onSave={saveAluno}
              onCancel={() => setEditing(null)}
            />
          </div>
          <section
            className="min-w-0 overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm"
            aria-labelledby="list-title"
          >
            <div className="border-b border-stone-100 p-5 sm:p-7">
              <div className="flex items-center justify-between gap-3">
                <h2
                  id="list-title"
                  className="text-xl font-semibold tracking-tight"
                >
                  Sua turma
                </h2>
                <span className="rounded-full bg-[#eef2e6] px-3 py-1 text-xs font-medium text-emerald-900">
                  {alunos.length} {alunos.length === 1 ? "aluno" : "alunos"}
                </span>
              </div>
              <label htmlFor="search" className="sr-only">
                Buscar alunos
              </label>
              <input
                id="search"
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Buscar por nome, e-mail ou curso..."
                className="mt-5 w-full rounded-lg border border-stone-200 bg-stone-50 px-4 py-3 text-sm focus:outline-emerald-700"
              />
            </div>
            <AlunoList
              alunos={filtered}
              hasAlunos={alunos.length > 0}
              onEdit={editAluno}
              onDelete={setDeleting}
            />
            <div className="border-t border-stone-100 px-5 py-4 text-xs text-stone-500 sm:px-7">
              {filtered.length} de {alunos.length} cadastros nesta sessão
            </div>
          </section>
        </div>
        <aside className="mt-7 flex items-start gap-3 rounded-xl border border-[#dde4ce] bg-[#edf1e4] p-4 text-sm text-[#4a5a3b]">
          <span aria-hidden="true">ⓘ</span>
          <p>
            <strong className="font-semibold">
              Uma sessão, muitas possibilidades.
            </strong>{" "}
            Os cadastros ficam disponíveis enquanto esta página estiver aberta.
            Ao recarregar, a lista será reiniciada.
          </p>
        </aside>
        <footer className="mt-10 flex flex-wrap justify-between gap-3 border-t border-stone-200 pt-5 text-xs text-stone-500">
          <span>campus. · Feito para organizar, pensado para pessoas.</span>
          <span>C216 L1 · Prática 6</span>
        </footer>
      </main>
      {deleting && (
        <DeleteDialog
          aluno={deleting}
          onConfirm={deleteAluno}
          onCancel={() => setDeleting(null)}
        />
      )}
    </>
  );
}
