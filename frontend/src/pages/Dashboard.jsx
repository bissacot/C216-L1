import {
  Activity,
  ArrowRight,
  ChartNoAxesColumn,
  ChartPie,
  CheckCheck,
  CircleAlert,
  Clock3,
  FolderOpen,
  Inbox,
  Layers3,
  Timer,
} from "lucide-react";
import { Link } from "react-router-dom";
import {
  Badge,
  Empty,
  NewTicket,
  PageTitle,
  Panel,
  Refresh,
  State,
} from "../components/ui";
import { useResource } from "../hooks/resources";
import { dashboard } from "../services/api";
import {
  date,
  deliveryStatuses,
  duration,
  priorities,
  priorityColors,
  statusColors,
  statuses,
  ticketCode,
} from "../utils/format";

function Metric({ icon: Icon, label, value, tint, to }) {
  return (
    <Link className={`metric ${tint}`} to={to}>
      <div>
        <span className="metric-icon">
          <Icon size={19} />
        </span>
        <span className="metric-label">{label}</span>
      </div>
      <strong>{value}</strong>
      <ArrowRight size={15} className="metric-arrow" />
    </Link>
  );
}
function StatusChart({ counts, total }) {
  let offset = 0;
  const stops = Object.entries(counts).map(([k, n]) => {
    const from = offset;
    offset += total ? (n / total) * 100 : 0;
    return `${statusColors[k]} ${from}% ${offset}%`;
  });
  return (
    <div className="status-chart">
      <div
        className="donut"
        aria-hidden="true"
        style={
          total ? { background: `conic-gradient(${stops.join(",")})` } : {}
        }
      >
        <div>
          <strong>{total}</strong>
          <span>chamados</span>
        </div>
      </div>
      <ul className="legend">
        {Object.entries(statuses).map(([k, label]) => (
          <li key={k}>
            <i style={{ background: statusColors[k] }} />
            {label}
            <b>{counts[k]}</b>
          </li>
        ))}
      </ul>
    </div>
  );
}
function Bars({ rows, total }) {
  return (
    <div className="bars">
      {rows.map(([label, count, color]) => (
        <div key={label} className="bar">
          <div>
            <span>{label}</span>
            <strong>{count}</strong>
          </div>
          <div className="bar-track" aria-hidden="true">
            <i
              style={{
                width: `${total ? (count / total) * 100 : 0}%`,
                background: color,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
export default function Dashboard() {
  const r = useResource("dashboard", dashboard, 60000);
  return (
    <>
      <PageTitle
        title="Dashboard"
        description="Visão geral dos chamados e da operação de suporte."
      >
        <NewTicket />
      </PageTitle>
      <div className="section-line">
        <div>
          <span className="section-rule" />
          Resumo operacional
        </div>
        <Refresh resource={r} />
      </div>
      <State resource={r}>
        {(d) => (
          <>
            <div className="metrics">
              <Metric
                icon={Layers3}
                label="Total de chamados"
                value={d.total}
                tint="indigo"
                to="/tickets"
              />
              <Metric
                icon={Inbox}
                label="Abertos"
                value={d.by_status.OPEN}
                tint="blue"
                to="/tickets?status=OPEN"
              />
              <Metric
                icon={Timer}
                label="Em atendimento"
                value={d.by_status.IN_PROGRESS}
                tint="amber"
                to="/tickets?status=IN_PROGRESS"
              />
              <Metric
                icon={CheckCheck}
                label="Resolvidos"
                value={d.by_status.RESOLVED}
                tint="green"
                to="/tickets?status=RESOLVED"
              />
            </div>
            <div className="chart-grid">
              <Panel title="Chamados por status" aside={<ChartPie size={17} />}>
                <StatusChart counts={d.by_status} total={d.total} />
              </Panel>
              <Panel
                title="Distribuição por prioridade"
                aside={<ChartNoAxesColumn size={18} />}
              >
                <Bars
                  rows={Object.entries(priorities).map(([k, label]) => [
                    label,
                    d.by_priority[k],
                    priorityColors[k],
                  ])}
                  total={d.total}
                />
              </Panel>
            </div>
            <Panel
              title="Chamados recentes"
              aside={
                <Link className="text-button" to="/tickets">
                  Ver todos <ArrowRight size={14} />
                </Link>
              }
            >
              {d.recent_tickets.length ? (
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        {["Chamado", "Prioridade", "Status", "Abertura"].map(
                          (x) => (
                            <th key={x}>{x}</th>
                          ),
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {d.recent_tickets.map((t) => (
                        <tr key={t.id}>
                          <td>
                            <Link
                              className="ticket-link"
                              to={`/tickets/${t.id}`}
                            >
                              <small>{ticketCode(t.id)}</small>
                              {t.title}
                            </Link>
                          </td>
                          <td>
                            <Badge value={t.priority} />
                          </td>
                          <td>
                            <Badge value={t.status} />
                          </td>
                          <td>{date(t.opened_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <Empty title="Nenhum chamado aberto ainda">
                  Os últimos cinco chamados aparecerão aqui após a abertura.
                </Empty>
              )}
            </Panel>
            <div className="chart-grid lower">
              <Panel
                title="Chamados por categoria"
                aside={<FolderOpen size={17} />}
              >
                {d.by_category.length ? (
                  <Bars
                    rows={d.by_category.map((x) => [
                      x.name,
                      x.count,
                      "#6284ed",
                    ])}
                    total={d.total}
                  />
                ) : (
                  <Empty title="Nenhuma categoria cadastrada" />
                )}
              </Panel>
              <Panel
                title="Indicadores de atendimento"
                aside={<Activity size={17} />}
              >
                <dl className="summary-list">
                  <div>
                    <dt>
                      <CircleAlert />
                      Críticos ativos
                    </dt>
                    <dd>{d.active_critical}</dd>
                  </div>
                  <div>
                    <dt>
                      <Clock3 />
                      Tempo médio de resolução
                    </dt>
                    <dd>{duration(d.average_resolution_seconds)}</dd>
                  </div>
                </dl>
                <h3 className="minor-title">Notificações por status</h3>
                <div className="counts">
                  {Object.entries(deliveryStatuses).map(([k, v]) => (
                    <Link to={`/notifications?status=${k}`} key={k}>
                      {v}
                      <b>{d.notifications[k]}</b>
                    </Link>
                  ))}
                </div>
              </Panel>
            </div>
          </>
        )}
      </State>
    </>
  );
}
