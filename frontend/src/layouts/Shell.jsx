import {
  Bell,
  ChevronRight,
  Columns2,
  Headset,
  LayoutDashboard,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Sun,
  Tags,
  Ticket,
  UsersRound,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { Alert } from "../components/ui";

const items = [
  ["/", "Dashboard", LayoutDashboard],
  ["/tickets", "Chamados", Ticket],
  ["/notifications", "Notificações", Bell],
  ["/requesters", "Solicitantes", UsersRound],
  ["/categories", "Categorias", Tags],
];
function Nav({ close }) {
  return (
    <nav aria-label="Menu principal">
      {[
        ["Operação", items.slice(0, 3)],
        ["Cadastros", items.slice(3)],
      ].map(([title, links]) => (
        <div key={title} className="nav-group">
          <p>{title}</p>
          {links.map(([path, name, Icon]) => (
            <NavLink
              key={path}
              end={path === "/"}
              to={path}
              onClick={close}
              aria-label={name}
              title={name}
            >
              <Icon size={19} />
              <span>{name}</span>
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  );
}
function Brand() {
  return (
    <Link className="brand" to="/" aria-label="HelpDesk Hub">
      <span className="brand-icon">
        <Headset size={23} />
      </span>
      <span>
        HelpDesk <b>Hub</b>
      </span>
    </Link>
  );
}
function pref(key, defaultValue) {
  try {
    return localStorage.getItem(key) ?? defaultValue;
  } catch {
    return defaultValue;
  }
}
function save(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* Preferências opcionais. */
  }
}
export default function Shell() {
  const loc = useLocation(),
    menu = useRef(null);
  const [dark, setDark] = useState(
    () => pref("helpdesk.theme", "light") === "dark",
  );
  const [compact, setCompact] = useState(
    () => pref("helpdesk.compact", "false") === "true",
  );
  const [flash, setFlash] = useState("");
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    save("helpdesk.theme", dark ? "dark" : "light");
  }, [dark]);
  useEffect(() => {
    save("helpdesk.compact", String(compact));
  }, [compact]);
  useEffect(() => {
    if (!flash) return;
    const t = setTimeout(() => setFlash(""), 7000);
    return () => clearTimeout(t);
  }, [flash]);
  const section =
    items.find(
      ([path]) =>
        path !== "/" &&
        (loc.pathname === path || loc.pathname.startsWith(`${path}/`)),
    )?.[1] || (loc.pathname === "/" ? "Dashboard" : "Página");
  useEffect(() => {
    document.title = `${section} · HelpDesk Hub`;
  }, [section]);
  const theme = (
    <button
      type="button"
      title={dark ? "Tema claro" : "Tema escuro"}
      aria-label={dark ? "Ativar tema claro" : "Ativar tema escuro"}
      onClick={() => setDark(!dark)}
    >
      {dark ? <Sun size={18} /> : <Moon size={18} />}
      <span>{dark ? "Tema claro" : "Tema escuro"}</span>
    </button>
  );
  return (
    <div className={`app-shell ${compact ? "compact" : ""}`}>
      <a className="skip" href="#conteudo">
        Ir para o conteúdo
      </a>
      <aside className="sidebar">
        <Brand />
        <Nav />
        <div className="side-bottom">
          {theme}
          <button
            type="button"
            aria-label={compact ? "Expandir menu" : "Recolher menu"}
            onClick={() => setCompact(!compact)}
          >
            {compact ? (
              <PanelLeftOpen size={18} />
            ) : (
              <PanelLeftClose size={18} />
            )}
            <span>Recolher menu</span>
          </button>
        </div>
      </aside>
      <dialog ref={menu} aria-label="Navegação" className="mobile-drawer">
        <div className="drawer-top">
          <Brand />
          <button
            type="button"
            aria-label="Fechar menu"
            onClick={() => menu.current.close()}
          >
            <X size={20} />
          </button>
        </div>
        <Nav close={() => menu.current.close()} />
        <div className="side-bottom">{theme}</div>
      </dialog>
      <div className="workspace">
        <div className="topbar">
          <button
            className="icon-button mobile-toggle"
            type="button"
            aria-label="Abrir menu"
            onClick={() => menu.current.showModal()}
          >
            <Menu size={20} />
          </button>
          <div className="crumb">
            <Columns2 size={16} />
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>{section}</strong>
          </div>
          <div className="top-tools">
            <span className="workspace-name">
              <span className="workspace-dot" />
              Central de TI
            </span>
            <Link
              className="icon-button"
              aria-label="Abrir notificações"
              to="/notifications"
            >
              <Bell size={18} />
            </Link>
          </div>
        </div>
        <main id="conteudo" tabIndex="-1">
          <Alert success message={flash} />
          <Outlet context={{ notify: setFlash }} />
        </main>
      </div>
    </div>
  );
}
