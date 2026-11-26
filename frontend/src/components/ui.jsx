import {
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Inbox,
  LoaderCircle,
  Plus,
  RefreshCw,
  X,
} from "lucide-react";
import { useEffect, useId, useRef } from "react";
import { Link } from "react-router-dom";
import { deliveryStatuses, priorities, statuses } from "../utils/format";
export function Badge({ value, children }) {
  return (
    <span className={`badge tone-${value}`}>
      <i aria-hidden="true" />
      {children ||
        statuses[value] ||
        priorities[value] ||
        deliveryStatuses[value] ||
        value}
    </span>
  );
}
export function PageTitle({ title, description, children }) {
  return (
    <header className="page-title">
      <div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      <div className="actions">{children}</div>
    </header>
  );
}
export function NewTicket() {
  return (
    <Link className="button primary" to="/tickets/new">
      <Plus size={17} />
      Novo chamado
    </Link>
  );
}
export function Refresh({ resource }) {
  return (
    <button
      type="button"
      className="button"
      onClick={resource.refresh}
      disabled={resource.loading}
    >
      <RefreshCw size={15} />
      Atualizar
    </button>
  );
}
export function Panel({ title, aside, children, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-title">
        <h2>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}
export function Alert({ message, success = false }) {
  if (!message) return null;
  const Icon = success ? CheckCircle2 : AlertCircle;
  return (
    <div
      className={`alert ${success ? "success" : ""}`}
      role={success ? "status" : "alert"}
    >
      <Icon size={17} />
      {message}
    </div>
  );
}
export function State({ resource, children }) {
  return (
    <>
      {resource.error && (
        <div className="failure">
          <Alert message={resource.error} />
          <button
            type="button"
            className="text-button"
            onClick={resource.refresh}
          >
            Tentar novamente
          </button>
        </div>
      )}
      {resource.data != null
        ? children(resource.data)
        : !resource.error && (
            <div className="loading" role="status">
              <LoaderCircle size={19} className="spin" />
              Carregando dados…
            </div>
          )}
    </>
  );
}
export function Empty({ title = "Nenhum registro encontrado", children }) {
  return (
    <div className="empty">
      <span className="empty-icon">
        <Inbox size={21} />
      </span>
      <strong>{title}</strong>
      {children && <p>{children}</p>}
    </div>
  );
}
export function Pages({ data, go }) {
  const pages = Math.max(1, Math.ceil(data.total / data.page_size));
  return (
    <div className="pagination">
      <span>
        {data.total} {data.total === 1 ? "registro" : "registros"}
      </span>
      <div>
        <button
          type="button"
          aria-label="Página anterior"
          disabled={data.page <= 1}
          onClick={() => go(Math.min(pages, data.page - 1))}
        >
          <ArrowLeft size={15} />
        </button>
        <span>
          Página {data.page} de {pages}
        </span>
        <button
          type="button"
          aria-label="Próxima página"
          disabled={data.page >= pages}
          onClick={() => go(data.page + 1)}
        >
          <ArrowRight size={15} />
        </button>
      </div>
    </div>
  );
}
export function Field({ label, children }) {
  return (
    // biome-ignore lint/a11y/noLabelWithoutControl: children contém o controle nativo deste campo.
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}
export function Options({ values }) {
  return Object.entries(values).map(([value, label]) => (
    <option key={value} value={value}>
      {label}
    </option>
  ));
}
export function Dialog({ title, onClose, busy = false, children }) {
  const ref = useRef(null);
  const id = useId();
  useEffect(() => {
    const el = ref.current;
    el.showModal();
    return () => el.close();
  }, []);
  return (
    <dialog
      ref={ref}
      className="dialog"
      aria-labelledby={id}
      onCancel={(e) => {
        e.preventDefault();
        if (!busy) onClose();
      }}
    >
      <div className="panel-title">
        <h2 id={id}>{title}</h2>
        <button
          type="button"
          className="icon-button"
          disabled={busy}
          aria-label="Fechar"
          onClick={onClose}
        >
          <X size={18} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
