export const statuses = {
  OPEN: "Aberto",
  IN_PROGRESS: "Em atendimento",
  RESOLVED: "Resolvido",
  CANCELLED: "Cancelado",
};
export const priorities = {
  LOW: "Baixa",
  MEDIUM: "Média",
  HIGH: "Alta",
  CRITICAL: "Crítica",
};
export const deliveryStatuses = {
  PENDING: "Pendente",
  SENT: "Enviada",
  FAILED: "Falha",
};
export const channels = { EMAIL: "E-mail", TEAMS: "Teams" };
export const modes = { DISABLED: "Desativado", MOCK: "Simulado", LIVE: "Real" };
export const statusColors = {
  OPEN: "#4f71ef",
  IN_PROGRESS: "#e5a13f",
  RESOLVED: "#22a889",
  CANCELLED: "#8897b1",
};
export const priorityColors = {
  LOW: "#62aaa7",
  MEDIUM: "#6386ec",
  HIGH: "#eaa251",
  CRITICAL: "#e16a78",
};
const dateFormat = new Intl.DateTimeFormat("pt-BR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});
export function date(value) {
  return value ? dateFormat.format(new Date(value)) : "—";
}
export function duration(seconds) {
  if (seconds == null) return "—";
  if (seconds < 60) return `${Math.round(seconds)} s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} min`;
  return (
    (seconds / 3600).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) +
    " h"
  );
}
export const ticketCode = (id) =>
  `#${String(id).padStart(id < 0 ? 1 : 4, "0")}`;
export function localBoundary(value, end = false) {
  if (!value) return undefined;
  return new Date(value + (end ? "T23:59:59.999" : "T00:00:00")).toISOString();
}
export const active = (status) => status === "OPEN" || status === "IN_PROGRESS";
