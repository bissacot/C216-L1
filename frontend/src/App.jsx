import { useCallback, useEffect, useRef, useState } from "react";
import AlunoForm from "./components/AlunoForm.jsx";
import AlunoList from "./components/AlunoList.jsx";
import DeleteDialog from "./components/DeleteDialog.jsx";
import {
  buscarAluno,
  criarAluno,
  excluirAluno,
  listarAlunos,
  substituirAluno,
} from "./services/alunos.js";

export default function App() {
  const [alunos, setAlunos] = useState([]);
  const [editing, setEditing] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [search, setSearch] = useState("");
  const [message, setMessage] = useState("");
  const [listState, setListState] = useState("loading");
  const [activity, setActivity] = useState("");
  const [error, setError] = useState("");
  const disabled = listState !== "ready" || Boolean(activity);
  const formArea = useRef(null);
  const filtered = alunos.filter((aluno) =>
    [aluno.nome, aluno.email, aluno.curso].some((value) =>
      value
        .toLocaleLowerCase("pt-BR")
        .includes(search.trim().toLocaleLowerCase("pt-BR")),
    ),
  );

  const loadAlunos = useCallback(async (signal) => {
    setListState("loading");
    setError("");
    try {
      const records = await listarAlunos(signal);
      if (signal?.aborted) return;
      setAlunos(records);
      setListState("ready");
    } catch (err) {
      if (signal?.aborted) return;
      setError(err.message);
      setListState("error");
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    loadAlunos(controller.signal);
    return () => controller.abort();
  }, [loadAlunos]);

  async function saveAluno(values) {
    setActivity("Salvando cadastro…");
    setMessage("");
    setError("");
    try {
      const saved = editing
        ? await substituirAluno(editing.id, values)
        : await criarAluno(values);
      setAlunos((current) =>
        editing
          ? current.map((aluno) => (aluno.id === saved.id ? saved : aluno))
          : [...current, saved],
      );
      setEditing(null);
      setMessage(
        editing
          ? "Aluno atualizado com sucesso."
          : "Aluno cadastrado com sucesso.",
      );
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setActivity("");
    }
  }

  async function editAluno(aluno) {
    setActivity("Consultando aluno…");
    setMessage("");
    setError("");
    try {
      setEditing(await buscarAluno(aluno.id));
      formArea.current.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      setError(err.message);
    } finally {
      setActivity("");
    }
  }

  async function deleteAluno() {
    setActivity("Excluindo aluno…");
    setError("");
    setMessage("");
    try {
      await excluirAluno(deleting.id);
      setAlunos((current) =>
        current.filter((aluno) => aluno.id !== deleting.id),
      );
      if (editing?.id === deleting.id) setEditing(null);
      setDeleting(null);
      setMessage("Aluno excluído com sucesso.");
      document.getElementById("search").focus();
    } catch (err) {
      setError(err.message);
    } finally {
      setActivity("");
    }
  }

  const status =
    listState === "loading" ? "Carregando alunos…" : activity || message;
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
              {listState === "ready"
                ? alunos.length.toString().padStart(2, "0")
                : "—"}
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
            status
              ? "mb-6 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
              : "sr-only"
          }
        >
          {status}
        </div>
        {error && !deleting && (
          <p
            role="alert"
            className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-red-800"
          >
            {error}
          </p>
        )}
        <div className="grid items-start gap-7 lg:grid-cols-[360px_minmax(0,1fr)]">
          <div ref={formArea} className="scroll-mt-6">
            <AlunoForm
              key={editing?.id ?? "new"}
              aluno={editing}
              onSave={saveAluno}
              disabled={disabled}
              onCancel={() => {
                setEditing(null);
                setError("");
              }}
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
                  {listState === "ready" &&
                    `${alunos.length} ${alunos.length === 1 ? "aluno" : "alunos"}`}
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
            {listState === "error" && (
              <button
                type="button"
                className="m-5 underline"
                onClick={() => loadAlunos()}
              >
                Tentar carregar novamente
              </button>
            )}
            {listState === "ready" && (
              <>
                <AlunoList
                  alunos={filtered}
                  hasAlunos={alunos.length > 0}
                  onEdit={editAluno}
                  disabled={disabled}
                  onDelete={(aluno) => {
                    setError("");
                    setMessage("");
                    setDeleting(aluno);
                  }}
                />
                <div className="border-t border-stone-100 px-5 py-4 text-xs text-stone-500 sm:px-7">
                  {filtered.length} de {alunos.length} cadastros
                </div>
              </>
            )}
          </section>
        </div>
        <footer className="mt-10 flex flex-wrap justify-between gap-3 border-t border-stone-200 pt-5 text-xs text-stone-500">
          <span>campus. · Feito para organizar, pensado para pessoas.</span>
          <span>C216 L1 · Prática 7</span>
        </footer>
      </main>
      {deleting && (
        <DeleteDialog
          aluno={deleting}
          onConfirm={deleteAluno}
          pending={Boolean(activity)}
          error={error}
          onCancel={() => {
            setDeleting(null);
            setError("");
          }}
        />
      )}
    </>
  );
}
