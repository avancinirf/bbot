import { useEffect, useState } from "react";
import { getStatsByBot } from "../api/stats";
import { getBotTrades } from "../api/bots";

function ActiveBotsPanel({ bots }) {
  const [statsByBot, setStatsByBot] = useState({});
  const [loadingStats, setLoadingStats] = useState(false);
  const [errorStats, setErrorStats] = useState(null);

  const [tradesByBot, setTradesByBot] = useState({});
  const [openTradesBotId, setOpenTradesBotId] = useState(null);
  const [loadingTradesBotId, setLoadingTradesBotId] = useState(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        setLoadingStats(true);
        setErrorStats(null);
        const data = await getStatsByBot();
        const map = {};
        data.forEach((row) => {
          map[row.bot_id] = row;
        });
        setStatsByBot(map);
      } catch (err) {
        console.error(err);
        setErrorStats("Erro ao carregar estatísticas por bot.");
      } finally {
        setLoadingStats(false);
      }
    };

    loadStats();
  }, []);

  const handleToggleTrades = async (botId) => {
    if (openTradesBotId === botId) {
      setOpenTradesBotId(null);
      return;
    }

    // se já temos trades em memória, só abre
    if (tradesByBot[botId]) {
      setOpenTradesBotId(botId);
      return;
    }

    try {
      setLoadingTradesBotId(botId);
      const trades = await getBotTrades(botId);
      setTradesByBot((prev) => ({
        ...prev,
        [botId]: trades,
      }));
      setOpenTradesBotId(botId);
    } catch (err) {
      console.error(err);
      alert("Erro ao carregar trades do bot.");
    } finally {
      setLoadingTradesBotId(null);
    }
  };

  if (!bots || bots.length === 0) {
    return <p>Não há bots ativos no momento.</p>;
  }

  return (
    <div className="active-bots-grid">
      {bots.map((bot) => {
        const stats = statsByBot[bot.id];
        const botTrades = tradesByBot[bot.id] || [];

        return (
          <div key={bot.id} className="bot-card">
            <div className="bot-card-header">
              <div>
                <h3 style={{ margin: 0 }}>{bot.name}</h3>
                <div className="bot-subtitle">
                  ID: {bot.id} — Símbolo: {bot.symbol}
                </div>
              </div>
              <div className="bot-status-pill">
                {bot.status === "online" ? "Online" : "Offline"}
                {bot.blocked && " (bloqueado)"}
              </div>
            </div>

            <div className="bot-card-body">
              <div className="bot-row">
                <span>Saldo virtual total (limite):</span>
                <strong>{Number(bot.saldo_usdt_limit).toFixed(2)} USDT</strong>
              </div>
              <div className="bot-row">
                <span>Saldo virtual livre:</span>
                <strong>{Number(bot.saldo_usdt_livre).toFixed(2)} USDT</strong>
              </div>
              <div className="bot-row">
                <span>Posição aberta?</span>
                <strong>{bot.has_open_position ? "Sim" : "Não"}</strong>
              </div>
              <div className="bot-row">
                <span>Qtd moeda:</span>
                <strong>{Number(bot.qty_moeda || 0).toFixed(8)}</strong>
              </div>
              <div className="bot-row">
                <span>Último preço de compra:</span>
                <strong>
                  {bot.last_buy_price != null
                    ? Number(bot.last_buy_price).toFixed(2)
                    : "-"}
                </strong>
              </div>
              <div className="bot-row">
                <span>Último preço de venda:</span>
                <strong>
                  {bot.last_sell_price != null
                    ? Number(bot.last_sell_price).toFixed(2)
                    : "-"}
                </strong>
              </div>
              <div className="bot-row">
                <span>Valor inicial do ciclo:</span>
                <strong>
                  {bot.valor_inicial != null
                    ? Number(bot.valor_inicial).toFixed(2)
                    : "-"}
                </strong>
              </div>

              {/* Estatísticas agregadas por bot (stats/by_bot) */}
              <div className="bot-section-divider" />

              <div className="bot-row">
                <span>Trades (total / buy / sell):</span>
                <strong>
                  {stats
                    ? `${stats.num_trades} / ${stats.num_buys} / ${stats.num_sells}`
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div className="bot-row">
                <span>P/L realizado (USDT):</span>
                <strong>
                  {stats
                    ? Number(stats.realized_pnl || 0).toFixed(6)
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div className="bot-row">
                <span>Taxas pagas (USDT):</span>
                <strong>
                  {stats
                    ? Number(stats.total_fees_usdt || 0).toFixed(6)
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div className="bot-row">
                <span>Último trade:</span>
                <strong>
                  {stats && stats.last_trade_at
                    ? new Date(stats.last_trade_at).toLocaleString()
                    : "-"}
                </strong>
              </div>

              {errorStats && (
                <p className="error" style={{ fontSize: "0.7rem" }}>
                  {errorStats}
                </p>
              )}

              {/* Botão para ver trades desse bot */}
              <div
                style={{
                  marginTop: "0.4rem",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: "0.4rem",
                  flexWrap: "wrap",
                }}
              >
                <button
                  type="button"
                  className="btn btn-secondary btn-xs"
                  onClick={() => handleToggleTrades(bot.id)}
                  disabled={loadingTradesBotId === bot.id}
                >
                  {openTradesBotId === bot.id
                    ? "Ocultar trades"
                    : loadingTradesBotId === bot.id
                    ? "Carregando..."
                    : "Ver trades"}
                </button>
              </div>

              {/* Lista de trades desse bot, com scroll interno */}
              {openTradesBotId === bot.id && (
                <div
                  style={{
                    marginTop: "0.4rem",
                    maxHeight: "160px",
                    overflow: "auto",
                    borderRadius: "0.3rem",
                    border: "1px solid #e5e7eb",
                  }}
                >
                  <table className="bot-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Lado</th>
                        <th>Preço</th>
                        <th>Qtd</th>
                        <th>Quote</th>
                        <th>Taxa</th>
                        <th>P/L</th>
                        <th>Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {botTrades.length === 0 && (
                        <tr>
                          <td
                            colSpan={8}
                            style={{
                              textAlign: "center",
                              fontSize: "0.75rem",
                            }}
                          >
                            Nenhum trade encontrado para este bot.
                          </td>
                        </tr>
                      )}

                      {botTrades.map((t) => (
                        <tr key={t.id}>
                          <td>{t.id}</td>
                          <td>{t.side}</td>
                          <td>{Number(t.price).toFixed(2)}</td>
                          <td>{Number(t.qty).toFixed(8)}</td>
                          <td>{Number(t.quote_qty).toFixed(6)}</td>
                          <td>
                            {t.fee_amount != null
                              ? `${Number(t.fee_amount).toFixed(6)} ${
                                  t.fee_asset || ""
                                }`
                              : "-"}
                          </td>
                          <td>
                            {t.realized_pnl != null
                              ? Number(t.realized_pnl).toFixed(6)
                              : "-"}
                          </td>
                          <td>
                            {t.created_at
                              ? new Date(t.created_at).toLocaleString()
                              : "-"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default ActiveBotsPanel;
