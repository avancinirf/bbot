import { useEffect, useState } from "react";
import {
  getSystemHealth,
  getSystemState,
  toggleSystemState,
} from "./api/system";
import {
  listBots,
  createBot,
  startBot,
  stopBot,
  blockBot,
  unblockBot,
  deleteBot,
  startAllBots,
  stopAllBots,
  closeBotPosition,
} from "./api/bots";
import { getAccountSummary } from "./api/binance";
import BotForm from "./components/BotForm";
import BotList from "./components/BotList";
import ActiveBotsPanel from "./components/ActiveBotsPanel";
import BotsSummary from "./components/BotsSummary";
import BinanceOrderTester from "./components/BinanceOrderTester";
import TradesBoard from "./components/TradesBoard";

const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [system, setSystem] = useState({
    app_name: "bbot",
    app_mode: "unknown",
  });
  const [systemRunning, setSystemRunning] = useState(false);
  const [bots, setBots] = useState([]);
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);
  const [showBalances, setShowBalances] = useState(false);

  const fetchBots = async () => {
    const botsData = await listBots();
    setBots(botsData);
  };

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [health, state, botsData, accountSummary] = await Promise.all([
        getSystemHealth(),
        getSystemState(),
        listBots(),
        getAccountSummary(),
      ]);

      setSystem(health);
      setSystemRunning(state.system_running);
      setBots(botsData);
      setAccount(accountSummary);
    } catch (err) {
      console.error(err);
      setError(
        "Erro ao carregar dados iniciais. Verifique se a API está no ar."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleToggleSystem = async () => {
    try {
      const res = await toggleSystemState();
      setSystemRunning(res.system_running);
    } catch (err) {
      console.error(err);
      alert("Erro ao alternar estado do sistema.");
    }
  };

  const handleCreateBot = async (botData) => {
    if (!window.confirm("Confirmar criação do bot?")) return;
    try {
      setCreating(true);
      setError(null);
      const newBot = await createBot(botData);
      setBots((prev) => [...prev, newBot]);
    } catch (err) {
      console.error(err);
      const msg = err?.message || "Erro ao criar bot.";
      alert(msg);
      setError(msg);
    } finally {
      setCreating(false);
    }
  };

  const updateBotInState = (updatedBot) => {
    setBots((prev) =>
      prev.map((b) => (b.id === updatedBot.id ? updatedBot : b))
    );
  };

  const removeBotFromState = (id) => {
    setBots((prev) => prev.filter((b) => b.id !== id));
  };

  const handleStartBot = async (id) => {
    if (!window.confirm("Confirmar LIGAR este bot?")) return;
    try {
      const updated = await startBot(id);
      updateBotInState(updated);
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao ligar bot.");
    }
  };

  const handleStopBot = async (id) => {
    if (!window.confirm("Confirmar DESLIGAR este bot?")) return;
    try {
      const updated = await stopBot(id);
      updateBotInState(updated);
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao desligar bot.");
    }
  };

  const handleBlockBot = async (id) => {
    if (!window.confirm("Confirmar BLOQUEAR este bot?")) return;
    try {
      const updated = await blockBot(id);
      updateBotInState(updated);
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao bloquear bot.");
    }
  };

  const handleUnblockBot = async (id) => {
    if (!window.confirm("Confirmar DESBLOQUEAR este bot?")) return;
    try {
      const updated = await unblockBot(id);
      updateBotInState(updated);
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao desbloquear bot.");
    }
  };

  const handleDeleteBot = async (id) => {
    if (
      !window.confirm(
        "Remover este bot e TODAS as informações relacionadas? Esta ação não pode ser desfeita."
      )
    ) {
      return;
    }
    try {
      await deleteBot(id);
      removeBotFromState(id);
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao remover bot.");
    }
  };

  const handleClosePosition = async (id) => {
    if (
      !window.confirm(
        "Confirmar FECHAR a posição deste bot ao preço de mercado atual?"
      )
    ) {
      return;
    }
    try {
      const updated = await closeBotPosition(id);
      updateBotInState(updated);
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao fechar posição do bot.");
    }
  };

  const handleStartAllBots = async () => {
    if (!window.confirm("Confirmar LIGAR TODOS os bots desbloqueados?")) return;
    try {
      await startAllBots();
      await fetchBots();
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao ligar todos os bots.");
    }
  };

  const handleStopAllBots = async () => {
    if (!window.confirm("Confirmar DESLIGAR TODOS os bots?")) return;
    try {
      await stopAllBots();
      await fetchBots();
    } catch (err) {
      console.error(err);
      alert(err?.message || "Erro ao desligar todos os bots.");
    }
  };

  const activeBots = bots.filter((b) => b.status === "online" && !b.blocked);
  const balancesCount = account?.balances?.length || 0;

  return (
    <div className="app-root">
      {/* Cabeçalho */}
      <header className="app-header">
        <div className="app-title">
          <h1>{system.app_name || "bbot"}</h1>
          <div className="app-mode">
            Modo:{" "}
            {system.app_mode === "simulation"
              ? "Simulação"
              : system.app_mode}
          </div>
        </div>
        <div className="app-header-actions">
          <span
            className={
              "system-status " + (systemRunning ? "on" : "off")
            }
          >
            {systemRunning ? "Sistema ligado" : "Sistema desligado"}
          </span>
          <button className="btn" onClick={handleToggleSystem}>
            {systemRunning ? "Desligar sistema" : "Ligar sistema"}
          </button>
        </div>
      </header>

      {/* ROW 1: Conta Binance */}
      <section className="account-info">
        <h2>Conta Binance</h2>

        {!account && <p>Carregando informações da conta...</p>}

        {account && (
          <>
            <p>
              Status de conexão:{" "}
              <strong>
                {account.connected
                  ? "Conectado"
                  : `Não conectado (${account.reason || "motivo desconhecido"})`}
              </strong>
            </p>
            <p>
              Modo backend: <strong>{account.mode}</strong>
            </p>
            <p>
              Ambiente Binance:{" "}
              <strong>{account.testnet ? "Testnet" : "Mainnet"}</strong>
            </p>
            <p>
              Pode operar (canTrade):{" "}
              <strong>{account.canTrade ? "Sim" : "Não"}</strong>
            </p>

            <div className="account-balances-header">
              <span>
                Ativos com saldo &gt; 0: <strong>{balancesCount}</strong>
              </span>
              {balancesCount > 0 && (
                <button
                  className="btn btn-secondary btn-xs"
                  onClick={() => setShowBalances((v) => !v)}
                >
                  {showBalances ? "Ocultar" : "Mostrar"}
                </button>
              )}
            </div>

            {showBalances && balancesCount > 0 && (
              <div className="account-balances">
                <table className="bot-table">
                  <thead>
                    <tr>
                      <th>Ativo</th>
                      <th>Free</th>
                      <th>Locked</th>
                    </tr>
                  </thead>
                  <tbody>
                    {account.balances.map((b) => (
                      <tr key={b.asset}>
                        <td>{b.asset}</td>
                        <td>{Number(b.free).toFixed(6)}</td>
                        <td>{Number(b.locked).toFixed(6)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <p style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>
              API base: <code>{apiBase}</code>
            </p>
          </>
        )}
      </section>

      {/* ROW 2: Resumo dos bots (virtual) */}
      <section className="account-info">
        <BotsSummary />
      </section>

      {/* ROW 3: Teste de ordens Binance */}
      <section className="account-info">
        <BinanceOrderTester account={account} />
      </section>

      {/* ROW 4: Histórico de trades */}
      <section className="account-info">
        <TradesBoard />
      </section>

      {loading && (
        <p style={{ padding: "0.5rem 1.25rem" }}>Carregando dados...</p>
      )}
      {error && (
        <p className="error" style={{ padding: "0 1.25rem" }}>
          {error}
        </p>
      )}

      {/* Layout principal: esquerda (form + lista), direita (cards ativos) */}
      <main className="main-layout">
        <div className="left-panel">
          <section className="panel">
            <h2>Criar novo bot</h2>
            <BotForm onCreate={handleCreateBot} loading={creating} />
          </section>

          <section className="panel">
            <h2>Lista de bots</h2>
            <BotList
              bots={bots}
              onStart={handleStartBot}
              onStop={handleStopBot}
              onBlock={handleBlockBot}
              onUnblock={handleUnblockBot}
              onDelete={handleDeleteBot}
              onStartAll={handleStartAllBots}
              onStopAll={handleStopAllBots}
              onClosePosition={handleClosePosition}
            />
          </section>
        </div>

        <div className="right-panel">
          <section className="panel">
            <h2>Bots ativos</h2>
            <ActiveBotsPanel bots={activeBots} />
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
