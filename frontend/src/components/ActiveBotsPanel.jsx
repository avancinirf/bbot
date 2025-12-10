// frontend/src/components/ActiveBotsPanel.jsx
import { useEffect, useState } from "react";
import { getStatsByBot } from "../api/stats";
import { getBotTrades } from "../api/bots";
import { getBotAnalysis } from "../api/analysis";

function formatRecomendacao(code) {
  if (!code) return "-";
  switch (code) {
    case "avaliar_entrada":
      return "Avaliar entrada";
    case "manter_posicao":
      return "Manter posição";
    case "avaliar_saida":
      return "Avaliar saída";
    default:
      return code;
  }
}

function getRecomendacaoClasses(code) {
  switch (code) {
    case "avaliar_entrada":
      return "px-1.5 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800";
    case "manter_posicao":
      return "px-1.5 py-0.5 rounded text-xs bg-slate-100 text-slate-800";
    case "avaliar_saida":
      return "px-1.5 py-0.5 rounded text-xs bg-rose-100 text-rose-800";
    default:
      return "px-1.5 py-0.5 rounded text-xs bg-slate-100 text-slate-800";
  }
}

function ActiveBotsPanel({ bots }) {
  const [statsByBot, setStatsByBot] = useState({});
  const [loadingStats, setLoadingStats] = useState(false);
  const [errorStats, setErrorStats] = useState(null);

  const [tradesByBot, setTradesByBot] = useState({});
  const [openTradesBotId, setOpenTradesBotId] = useState(null);
  const [loadingTradesBotId, setLoadingTradesBotId] = useState(null);

  const [analysisByBot, setAnalysisByBot] = useState({});
  const [openAnalysisBotId, setOpenAnalysisBotId] = useState(null);
  const [loadingAnalysisBotId, setLoadingAnalysisBotId] = useState(null);

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

  const handleToggleAnalysis = async (botId) => {
    if (openAnalysisBotId === botId) {
      setOpenAnalysisBotId(null);
      return;
    }

    if (analysisByBot[botId]) {
      setOpenAnalysisBotId(botId);
      return;
    }

    try {
      setLoadingAnalysisBotId(botId);
      const data = await getBotAnalysis(botId);
      setAnalysisByBot((prev) => ({
        ...prev,
        [botId]: data,
      }));
      setOpenAnalysisBotId(botId);
    } catch (err) {
      console.error(err);
      alert("Erro ao carregar análise do bot.");
    } finally {
      setLoadingAnalysisBotId(null);
    }
  };

  if (!bots || bots.length === 0) {
    return (
      <div className="text-sm text-slate-500">
        Não há bots ativos no momento.
      </div>
    );
  }

  return (
    <div>
      {bots.map((bot) => {
        const stats = statsByBot[bot.id];
        const botTrades = tradesByBot[bot.id] || [];
        const analysis = analysisByBot[bot.id];

        return (
          <div
            key={bot.id}
            className="bg-white"
            style={{
              border: "1px solid #e5e7eb",
              borderRadius: "0.6rem",
              padding: "0.75rem",
              marginBottom: "0.85rem",
              boxShadow: "0 1px 2px rgba(15, 23, 42, 0.06)",
            }}
          >
            {/* Cabeçalho do card */}
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-sm">
                  {bot.name}{" "}
                  <span className="text-xs text-slate-500">
                    (ID {bot.id} · {bot.symbol})
                  </span>
                </h3>
                <p className="text-xs text-slate-500">
                  {bot.status === "online" ? "Online" : "Offline"}
                  {bot.blocked && " (bloqueado)"}
                </p>
              </div>
              <div className="text-xs text-slate-500 text-right">
                Limite virtual:{" "}
                <span className="font-mono">
                  {Number(bot.saldo_usdt_limit).toFixed(2)} USDT
                </span>
                <br />
                Livre:{" "}
                <span className="font-mono">
                  {Number(bot.saldo_usdt_livre).toFixed(2)} USDT
                </span>
              </div>
            </div>

            {/* Dados do bot */}
            <div className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
              <div>
                Posição aberta?{" "}
                <span className="font-mono">
                  {bot.has_open_position ? "Sim" : "Não"}
                </span>
              </div>
              <div>
                Qtd moeda:{" "}
                <span className="font-mono">
                  {Number(bot.qty_moeda || 0).toFixed(8)}
                </span>
              </div>
              <div>
                Último preço de compra:{" "}
                <span className="font-mono">
                  {bot.last_buy_price != null
                    ? Number(bot.last_buy_price).toFixed(2)
                    : "-"}
                </span>
              </div>
              <div>
                Último preço de venda:{" "}
                <span className="font-mono">
                  {bot.last_sell_price != null
                    ? Number(bot.last_sell_price).toFixed(2)
                    : "-"}
                </span>
              </div>
              <div>
                Valor inicial do ciclo:{" "}
                <span className="font-mono">
                  {bot.valor_inicial != null
                    ? Number(bot.valor_inicial).toFixed(2)
                    : "-"}
                </span>
              </div>
              <div>
                Stop loss:{" "}
                <span className="font-mono">
                  {Number(bot.stop_loss_percent).toFixed(2)}% (
                  {bot.vender_stop_loss ? "vende ao acionar" : "não vende"})
                </span>
              </div>
              <div>
                % compra:{" "}
                <span className="font-mono">
                  {Number(bot.porcentagem_compra || 0).toFixed(2)}%
                </span>
              </div>
              <div>
                % venda (take profit):{" "}
                <span className="font-mono">
                  {Number(bot.porcentagem_venda || 0).toFixed(2)}%
                </span>
              </div>
            </div>

            {/* Estatísticas + botões */}
            <div className="mt-2 flex items-start justify-between gap-4 text-xs">
              <div className="space-y-1">
                <div className="font-semibold">Estatísticas de trades</div>
                <div>
                  Trades (total / buy / sell):{" "}
                  {stats
                    ? `${stats.num_trades} / ${stats.num_buys} / ${stats.num_sells}`
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </div>
                <div>
                  P/L realizado (USDT):{" "}
                  {stats
                    ? Number(stats.realized_pnl || 0).toFixed(6)
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </div>
                <div>
                  Taxas pagas (USDT):{" "}
                  {stats
                    ? Number(stats.total_fees_usdt || 0).toFixed(6)
                    : loadingStats
                    ? "Carregando..."
                    : "-"}
                </div>
                <div>
                  Último trade:{" "}
                  {stats && stats.last_trade_at
                    ? new Date(stats.last_trade_at).toLocaleString()
                    : "-"}
                </div>
                {errorStats && (
                  <p className="text-xs text-red-600 mt-1">{errorStats}</p>
                )}
              </div>

              <div className="flex flex-col gap-2 items-end">
                <button
                  className="px-2 py-1 text-xs rounded border border-slate-300 hover:bg-slate-50"
                  onClick={() => handleToggleTrades(bot.id)}
                  disabled={loadingTradesBotId === bot.id}
                >
                  {openTradesBotId === bot.id
                    ? "Ocultar trades"
                    : loadingTradesBotId === bot.id
                    ? "Carregando trades..."
                    : "Ver trades"}
                </button>

                <button
                  className="px-2 py-1 text-xs rounded border border-indigo-300 hover:bg-indigo-50"
                  onClick={() => handleToggleAnalysis(bot.id)}
                  disabled={loadingAnalysisBotId === bot.id}
                >
                  {openAnalysisBotId === bot.id
                    ? "Ocultar análise"
                    : loadingAnalysisBotId === bot.id
                    ? "Carregando análise..."
                    : "Ver análise"}
                </button>
              </div>
            </div>

            {/* Bloco de análise do bot */}
            {openAnalysisBotId === bot.id && (
              <div className="mt-2 border rounded bg-slate-50 p-2 text-xs space-y-1 max-h-40 overflow-y-auto">
                {!analysis && loadingAnalysisBotId === bot.id && (
                  <p className="text-slate-500">Carregando análise...</p>
                )}

                {analysis && (
                  <>
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="font-semibold mr-1">
                          Recomendação:
                        </span>
                        <span
                          className={getRecomendacaoClasses(
                            analysis.analysis?.recomendacao
                          )}
                        >
                          {formatRecomendacao(
                            analysis.analysis?.recomendacao
                          )}
                        </span>
                      </div>
                    </div>

                    {Array.isArray(analysis.analysis?.motivos) &&
                      analysis.analysis.motivos.length > 0 && (
                        <div>
                          <div className="font-semibold">Motivos:</div>
                          <ul className="list-disc list-inside space-y-0.5">
                            {analysis.analysis.motivos.map((m, idx) => (
                              <li key={idx}>{m}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                    {analysis.indicator && (
                      <div className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1">
                        <div>
                          Preço close:{" "}
                          <span className="font-mono">
                            {Number(analysis.indicator.close).toFixed(2)}
                          </span>
                        </div>
                        <div>
                          RSI14:{" "}
                          <span className="font-mono">
                            {Number(analysis.indicator.rsi14).toFixed(2)}
                          </span>
                        </div>
                        <div>
                          MACD:{" "}
                          <span className="font-mono">
                            {Number(analysis.indicator.macd).toFixed(2)}
                          </span>
                        </div>
                        <div>
                          MACD signal:{" "}
                          <span className="font-mono">
                            {Number(
                              analysis.indicator.macd_signal
                            ).toFixed(2)}
                          </span>
                        </div>
                        <div>
                          Sinal mercado:{" "}
                          <span className="font-mono">
                            {analysis.indicator.market_signal_compra
                              ? "COMPRA"
                              : analysis.indicator.market_signal_venda
                              ? "VENDA"
                              : "Neutro"}
                          </span>
                        </div>
                      </div>
                    )}

                    {analysis.position &&
                      (analysis.position.current_position_value != null ||
                        analysis.position.unrealized_pnl != null) && (
                        <div className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1">
                          <div>
                            Valor posição:{" "}
                            <span className="font-mono">
                              {analysis.position.current_position_value != null
                                ? `${Number(
                                    analysis.position.current_position_value
                                  ).toFixed(4)} USDT`
                                : "-"}
                            </span>
                          </div>
                          <div>
                            P/L não realizado:{" "}
                            <span className="font-mono">
                              {analysis.position.unrealized_pnl != null
                                ? `${Number(
                                    analysis.position.unrealized_pnl
                                  ).toFixed(6)} USDT`
                                : "-"}
                            </span>
                          </div>
                        </div>
                      )}

                    <p className="mt-1 text-[10px] text-slate-500">
                      Esta análise é apenas informativa e não constitui
                      recomendação financeira.
                    </p>
                  </>
                )}
              </div>
            )}

            {/* Lista de trades do bot */}
            {openTradesBotId === bot.id && (
              <div className="mt-2 border rounded bg-slate-50 max-h-40 overflow-y-auto">
                <table className="w-full text-[11px]">
                  <thead className="bg-slate-100 sticky top-0">
                    <tr>
                      <th className="px-2 py-1 text-left">ID</th>
                      <th className="px-2 py-1 text-left">Lado</th>
                      <th className="px-2 py-1 text-right">Preço</th>
                      <th className="px-2 py-1 text-right">Qtd</th>
                      <th className="px-2 py-1 text-right">Quote</th>
                      <th className="px-2 py-1 text-right">Taxa</th>
                      <th className="px-2 py-1 text-right">P/L</th>
                      <th className="px-2 py-1 text-left">Data</th>
                    </tr>
                  </thead>
                  <tbody>
                    {botTrades.length === 0 && (
                      <tr>
                        <td
                          colSpan={8}
                          className="px-2 py-2 text-center text-slate-500"
                        >
                          Nenhum trade encontrado para este bot.
                        </td>
                      </tr>
                    )}
                    {botTrades.map((t) => (
                      <tr key={t.id}>
                        <td className="px-2 py-1">{t.id}</td>
                        <td className="px-2 py-1">{t.side}</td>
                        <td className="px-2 py-1 text-right">
                          {Number(t.price).toFixed(2)}
                        </td>
                        <td className="px-2 py-1 text-right">
                          {Number(t.qty).toFixed(8)}
                        </td>
                        <td className="px-2 py-1 text-right">
                          {Number(t.quote_qty).toFixed(6)}
                        </td>
                        <td className="px-2 py-1 text-right">
                          {t.fee_amount != null
                            ? `${Number(t.fee_amount).toFixed(6)} ${
                                t.fee_asset || ""
                              }`
                            : "-"}
                        </td>
                        <td className="px-2 py-1 text-right">
                          {t.realized_pnl != null
                            ? Number(t.realized_pnl).toFixed(6)
                            : "-"}
                        </td>
                        <td className="px-2 py-1">
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
        );
      })}
    </div>
  );
}

export default ActiveBotsPanel;
