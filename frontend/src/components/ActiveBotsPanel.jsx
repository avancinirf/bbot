import { useEffect, useState } from "react";
import { getStatsByBot } from "../api/stats";
import { getBotTrades } from "../api/bots";
import { getLatestIndicator } from "../api/indicators";

function ActiveBotsPanel({ bots }) {
  const [statsByBot, setStatsByBot] = useState({});
  const [loadingStats, setLoadingStats] = useState(false);
  const [errorStats, setErrorStats] = useState(null);

  const [tradesByBot, setTradesByBot] = useState({});
  const [openTradesBotId, setOpenTradesBotId] = useState(null);
  const [loadingTradesBotId, setLoadingTradesBotId] = useState(null);

  const [indicatorsBySymbol, setIndicatorsBySymbol] = useState({});
  const [loadingIndicators, setLoadingIndicators] = useState(false);
  const [errorIndicators, setErrorIndicators] = useState(null);

  // Stats agregadas por bot (/stats/by_bot)
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

  // Indicadores mais recentes por símbolo (/indicators/latest/{symbol})
  useEffect(() => {
    if (!bots || bots.length === 0) {
      setIndicatorsBySymbol({});
      setErrorIndicators(null);
      return;
    }

    const loadIndicators = async () => {
      try {
        setLoadingIndicators(true);
        setErrorIndicators(null);

        const symbols = Array.from(
          new Set(bots.map((b) => b.symbol).filter(Boolean))
        );

        const results = await Promise.all(
          symbols.map(async (sym) => {
            try {
              const data = await getLatestIndicator(sym);
              return { sym, data, isError: false };
            } catch (err) {
              // 404 = backend dizendo "nenhum indicador para esse símbolo"
              if (err.status === 404) {
                // não loga como erro, só considera "sem dados"
                return { sym, data: null, isError: false };
              }

              console.error(
                "[ActiveBotsPanel] Erro ao buscar indicador de",
                sym,
                err
              );
              return { sym, data: null, isError: true };
            }
          })
        );

        const map = {};
        let hadError = false;

        results.forEach(({ sym, data, isError }) => {
          if (data) {
            map[sym] = data;
          }
          if (isError) {
            hadError = true;
          }
        });

        setIndicatorsBySymbol(map);

        if (hadError) {
          setErrorIndicators(
            "Erro ao carregar indicadores para alguns bots."
          );
        }
      } finally {
        setLoadingIndicators(false);
      }
    };

    loadIndicators();
  }, [bots]);

  const handleToggleTrades = async (botId) => {
    if (openTradesBotId === botId) {
      setOpenTradesBotId(null);
      return;
    }

    // Se já temos trades em memória, só abre
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
    <div className="bot-cards">
      {bots.map((bot) => {
        const stats = statsByBot[bot.id];
        const botTrades = tradesByBot[bot.id] || [];
        const indicator = indicatorsBySymbol[bot.symbol];

        return (
          <div key={bot.id} className="bot-card">
            {/* Cabeçalho */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                marginBottom: "0.25rem",
              }}
            >
              <div>
                <h3 style={{ margin: 0, fontSize: "0.95rem" }}>{bot.name}</h3>
                <div
                  style={{
                    fontSize: "0.75rem",
                    color: "#4b5563",
                    marginTop: "0.1rem",
                  }}
                >
                  ID: {bot.id} — Símbolo: {bot.symbol}
                </div>
              </div>

              <div
                style={{
                  fontSize: "0.7rem",
                  padding: "0.15rem 0.45rem",
                  borderRadius: "999px",
                  backgroundColor:
                    bot.status === "online" ? "#dcfce7" : "#fee2e2",
                  color: bot.status === "online" ? "#166534" : "#b91c1c",
                }}
              >
                {bot.status === "online" ? "Online" : "Offline"}
                {bot.blocked && " (bloqueado)"}
              </div>
            </div>

            {/* Linha 1: saldo e posição */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                gap: "0.25rem",
                fontSize: "0.8rem",
              }}
            >
              <div>
                <div>Saldo virtual (limite):</div>
                <strong>
                  {Number(bot.saldo_usdt_limit).toFixed(2)} USDT
                </strong>
              </div>
              <div>
                <div>Saldo virtual livre:</div>
                <strong>
                  {Number(bot.saldo_usdt_livre).toFixed(2)} USDT
                </strong>
              </div>
              <div>
                <div>Posição aberta?</div>
                <strong>{bot.has_open_position ? "Sim" : "Não"}</strong>
              </div>
              <div>
                <div>Qtd moeda:</div>
                <strong>{Number(bot.qty_moeda || 0).toFixed(8)}</strong>
              </div>
              <div>
                <div>Último preço de compra:</div>
                <strong>
                  {bot.last_buy_price != null
                    ? Number(bot.last_buy_price).toFixed(2)
                    : "-"}
                </strong>
              </div>
              <div>
                <div>Último preço de venda:</div>
                <strong>
                  {bot.last_sell_price != null
                    ? Number(bot.last_sell_price).toFixed(2)
                    : "-"}
                </strong>
              </div>
              <div>
                <div>Valor inicial do ciclo:</div>
                <strong>
                  {bot.valor_inicial != null
                    ? Number(bot.valor_inicial).toFixed(2)
                    : "-"}
                </strong>
              </div>
            </div>

            {/* Separador */}
            <div
              style={{
                margin: "0.35rem 0",
                borderTop: "1px dashed #e5e7eb",
              }}
            />

            {/* Stats por bot */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                gap: "0.25rem",
                fontSize: "0.8rem",
              }}
            >
              <div>
                <div>Trades (total / buy / sell):</div>
                <strong>
                  {stats
                    ? `${stats.num_trades} / ${stats.num_buys} / ${stats.num_sells}`
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div>
                <div>P/L realizado (USDT):</div>
                <strong>
                  {stats
                    ? Number(stats.realized_pnl || 0).toFixed(6)
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div>
                <div>Taxas pagas (USDT):</div>
                <strong>
                  {stats
                    ? Number(stats.total_fees_usdt || 0).toFixed(6)
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div>
                <div>Último trade:</div>
                <strong>
                  {stats && stats.last_trade_at
                    ? new Date(stats.last_trade_at).toLocaleString()
                    : "-"}
                </strong>
              </div>
            </div>

            {errorStats && (
              <p className="error" style={{ fontSize: "0.7rem" }}>
                {errorStats}
              </p>
            )}

            {/* Separador */}
            <div
              style={{
                margin: "0.35rem 0",
                borderTop: "1px dashed #e5e7eb",
              }}
            />

            {/* Indicadores técnicos */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                gap: "0.25rem",
                fontSize: "0.8rem",
              }}
            >
              <div>
                <div>Preço (close):</div>
                <strong>
                  {indicator && indicator.close != null
                    ? Number(indicator.close).toFixed(2)
                    : loadingIndicators
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div>
                <div>EMA9 / EMA21:</div>
                <strong>
                  {indicator
                    ? `${indicator.ema9 != null
                        ? Number(indicator.ema9).toFixed(2)
                        : "-"
                      } / ${
                        indicator.ema21 != null
                          ? Number(indicator.ema21).toFixed(2)
                          : "-"
                      }`
                    : loadingIndicators
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div>
                <div>RSI14:</div>
                <strong>
                  {indicator && indicator.rsi14 != null
                    ? Number(indicator.rsi14).toFixed(2)
                    : loadingIndicators
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
              <div>
                <div>Tendência / Sinal mercado:</div>
                <strong>
                  {indicator
                    ? `${indicator.trend_label || "-"} / ${
                        indicator.market_signal_compra
                          ? "COMPRA"
                          : indicator.market_signal_venda
                          ? "VENDA"
                          : "-"
                      }`
                    : loadingIndicators
                    ? "Carregando..."
                    : "-"}
                </strong>
              </div>
            </div>

            {errorIndicators && (
              <p className="error" style={{ fontSize: "0.7rem" }}>
                {errorIndicators}
              </p>
            )}

            {/* Botão / trades */}
            <div
              style={{
                marginTop: "0.4rem",
                display: "flex",
                justifyContent: "flex-end",
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

            {openTradesBotId === bot.id && (
              <div className="bot-trades-container">
                <div className="bot-trades-table-wrapper">
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
                          <td colSpan={8} style={{ textAlign: "center" }}>
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
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default ActiveBotsPanel;
