export default function App() {
  return (
    <div className="shell">
      <main className="welcome">
        <div className="intro">
          <h1>
            HelpDesk <span>Hub</span>
          </h1>
          <p>Central Inteligente de Chamados de TI</p>
        </div>
        <div className="tickets" aria-hidden="true">
          <div className="ticket ticket-back" />
          <div className="ticket ticket-front">
            <i />
            <i />
            <i />
          </div>
        </div>
      </main>
      <footer className="mx-auto flex w-full max-w-6xl items-center gap-3 border-t py-5 text-sm">
        <strong>C216</strong>
        <span>Sistemas Distribuídos</span>
      </footer>
    </div>
  );
}
