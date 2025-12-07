import { useState } from "react";
import { getBotTrades } from "../api/bots";

function BotList({
  bots,
  onStart,
  onStop,
  onBlock,
  onUnblock,
  onDelete,
  onStartAll,
  onStopAll,
  onClosePosition,
}) {
  const [openTrades, setOpenTrades] = useState({}); // { [id]: true/false }
  const [tradesData, setTradesData] = useState({}); // { [id]: { loading, error, trades } }

  if (!bots.length) {
    return <p>Nenhum bot cadastrado ainda.</p>;
  }

  const handleToggleTrades = async (bot) => {
    const id = bot.id;
    const isOpen = !!openTrades[id];

    // Se já está aberto, só fecha
    if (isOpen) {
      setOpenTrades((prev) => ({ ...prev, [id]: false }));
      return;
    }

    // Abre e carrega trades
    setOpenTrades((prev) => ({ ...prev, [id]: true }));
    setTradesData((prev) => ({
      ...prev,
      [id]: { ...(prev[id] || {}), loading: true, error: null },
    }));

    try {
      const trades = await getBotTrades(id);
      setTradesData((prev) => ({
        ...prev,
        [id]: {
          ...(prev[id] || {}),
          loading: false,
          error: null,
          trades,
        },
      }));
    } catch (err) {
      setTradesData((prev) => ({
        ...prev,
        [id]: {
          ...(prev[id] || {}),
          loading: false,
          trades: [],
          error: err?.message || "Erro ao carregar trades.",
        },
      }));
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "0.5rem", display: "flex", gap: "0.5rem" }}>
        <button className="btn" type="button" onClick={onStartAll}>
          Ligar todos
        </button>
        <button className="btn btn-secondary" type="button" onClick={onStopAll}>
          Desligar todos
        </button>
      </div>

      <table className="bot-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Par</th>
            <th>Saldo virtual (USDT)</th>
            <th>Status</th>
            <th>Bloqueado</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {bots.map((bot) => {
            const actions = [];

            if (!bot.blocked) {
              if (bot.status === "online") {
                actions.push({
                  label: "Desligar",
                  type: "secondary",
                  onClick: () => onStop(bot.id),
                });
              } else {
                actions.push({
                  label: "Ligar",
                  type: "primary",
                  onClick: () => onStart(bot.id),
                });
              }

              actions.push({
                label: "Bloquear",
                type: "secondary",
                onClick: () => onBlock(bot.id),
              });
            } else {
              actions.push({
                label: "Desbloquear",
                type: "primary",
                onClick: () => onUnblock(bot.id),
              });
            }

            // Fechar posição só aparece se tiver posição aberta
            if (bot.has_open_position) {
              actions.push({
                label: "Fechar posição",
                type: "secondary",
                onClick: () => onClosePosition(bot.id),
              });
            }

            const isOpen = !!openTrades[bot.id];
            const data = tradesData[bot.id] || {};

            // Ver trades sempre
            actions.push({
              label: isOpen ? "Ocultar trades" : "Ver trades",
              type: "secondary",
              onClick: () => handleToggleTrades(bot),
            });

            // Remover sempre
            actions.push({
              label: "Remover",
              type: "secondary",
              onClick: () => onDelete(bot.id),
            });

            // P/L realizado acumulado para este bot (só SELL tem realized_pnl)
            const realizedPnl =
              data.trades && data.trades.length
                ? data.trades.reduce(
                    (sum, t) =>
                      sum + (t.realized_pnl != null ? t.realized_pnl : 0),
                    0
                  )
                : 0;

            return (
              <>
                <tr key={bot.id}>
                  <td>{bot.id}</td>
                  <td>{bot.name}</td>
                  <td>{bot.symbol}</td>
                  <td>{bot.saldo_usdt_livre.toFixed(2)}</td>
                  <td>{bot.status}</td>
                  <td>{bot.blocked ? "Sim" : "Não"}</td>
                  <td>
                    <div className="bot-actions">
                      {actions.map((action, idx) => (
                        <button
                          key={idx}
                          className={
                            "btn " +
                            (action.type === "secondary" ? "btn-secondary" : "")
                          }
                          type="button"
                          onClick={action.onClick}
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  </td>
                </tr>

                {isOpen && (
                  <tr key={`${bot.id}-trades`}>
                    <td colSpan={7}>
                      <div className="bot-trades-container">
                        <p
                          style={{
                            fontSize: "0.78rem",
                            marginBottom: "0.2rem",
                          }}
                        >
                          Trades de <strong>{bot.name}</strong> ({bot.symbol})
                        </p>

                        <p
                          style={{
                            fontSize: "0.78rem",
                            marginBottom: "0.3rem",
                          }}
                        >
                          P/L realizado:{" "}
                          <strong>{realizedPnl.toFixed(4)} USDT</strong>
                        </p>

                        {data.loading && <p>Carregando trades...</p>}
                        {data.error && (
                          <p className="error">
                            Erro ao carregar trades: {data.error}
                          </p>
                        )}
                        {!data.loading &&
                          !data.error &&
                          (!data.trades || data.trades.length === 0) && (
                            <p style={{ fontSize: "0.8rem" }}>
                              Nenhum trade registrado para este bot.
                            </p>
                          )}

                        {!data.loading && !data.error && data.trades && (
                          <div className="bot-trades-table-wrapper">
                            <table className="bot-table">
                              <thead>
                                <tr>
                                  <th>Data</th>
                                  <th>Lado</th>
                                  <th>Preço</th>
                                  <th>Qtd</th>
                                  <th>Valor (USDT)</th>
                                  <th>Simulado</th>
                                </tr>
                              </thead>
                              <tbody>
                                {data.trades.map((t) => (
                                  <tr key={t.id}>
                                    <td>
                                      {t.created_at
                                        ? new Date(
                                            t.created_at
                                          ).toLocaleString()
                                        : "-"}
                                    </td>
                                    <td>{t.side}</td>
                                    <td>{t.price.toFixed(4)}</td>
                                    <td>{t.qty}</td>
                                    <td>{t.quote_qty}</td>
                                    <td>{t.is_simulated ? "Sim" : "Não"}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default BotList;
