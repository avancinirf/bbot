import { useEffect, useState } from "react";
import { getLatestIndicator } from "../api/indicators";

function ActiveBotsPanel({ bots }) {
  const activeBots = bots || [];

  const [indicatorsBySymbol, setIndicatorsBySymbol] = useState({}); // { [symbol]: { loading, error, data } }

  // Carrega o último indicador (5m) para cada símbolo dos bots ativos
  useEffect(() => {
    if (!activeBots.length) return;

    const symbols = Array.from(new Set(activeBots.map((b) => b.symbol)));

    symbols.forEach((symbol) => {
      setIndicatorsBySymbol((prev) => {
        const current = prev[symbol];
        // Se já temos loading/data/error, não dispara outra requisição
        if (current && (current.loading || current.data || current.error)) {
          return prev;
        }

        const next = {
          ...prev,
          [symbol]: { loading: true, error: null, data: current?.data || null },
        };

        // Dispara fetch assíncrono
        getLatestIndicator(symbol)
          .then((data) => {
            setIndicatorsBySymbol((prev2) => ({
              ...prev2,
              [symbol]: { loading: false, error: null, data },
            }));
          })
          .catch((err) => {
            setIndicatorsBySymbol((prev2) => ({
              ...prev2,
              [symbol]: {
                loading: false,
                error:
                  err?.message || "Erro ao carregar indicadores para o símbolo.",
                data: null,
              },
            }));
          });

        return next;
      });
    });
  }, [activeBots]);

  if (!activeBots.length) {
    return <p>Nenhum bot ativo no momento.</p>;
  }

  return (
    <div className="bot-cards">
      {activeBots.map((bot) => {
        const indState = indicatorsBySymbol[bot.symbol] || {};
        const ind = indState.data || null;

        let signalText = "-";
        let signalColor = "#374151";

        if (ind?.market_signal_compra) {
          signalText = "Sinal de COMPRA";
          signalColor = "#16a34a"; // verde
        } else if (ind?.market_signal_venda) {
          signalText = "Sinal de VENDA";
          signalColor = "#b91c1c"; // vermelho
        }

        const trendLabel = ind?.trend_label || "desconhecido";
        const rsi =
          ind?.rsi14 != null ? Number(ind.rsi14).toFixed(2) : "–";
        const macdHist =
          ind?.macd_hist != null ? Number(ind.macd_hist).toFixed(2) : "–";

        return (
          <div key={bot.id} className="bot-card">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: "0.25rem",
              }}
            >
              <div>
                <strong>{bot.name}</strong>{" "}
                <span style={{ fontSize: "0.75rem", color: "#6b7280" }}>
                  ({bot.symbol})
                </span>
              </div>
              <div style={{ fontSize: "0.75rem" }}>
                Status:{" "}
                <strong>{bot.status}</strong>
              </div>
            </div>

            <div style={{ fontSize: "0.8rem" }}>
              <div>Saldo virtual livre: {bot.saldo_usdt_livre.toFixed(2)} USDT</div>
              <div>
                Posição aberta: {bot.has_open_position ? "Sim" : "Não"}
              </div>
              {bot.has_open_position && (
                <>
                  <div>Qtd moeda (virtual): {bot.qty_moeda}</div>
                  <div>
                    Última compra:{" "}
                    {bot.last_buy_price != null ? bot.last_buy_price : "-"}
                  </div>
                  <div>
                    Última venda:{" "}
                    {bot.last_sell_price != null ? bot.last_sell_price : "-"}
                  </div>
                </>
              )}
            </div>

            {/* Bloco de indicadores */}
            <div
              style={{
                marginTop: "0.4rem",
                paddingTop: "0.35rem",
                borderTop: "1px solid #e5e7eb",
                fontSize: "0.75rem",
              }}
            >
              <div style={{ fontWeight: 600, marginBottom: "0.2rem" }}>
                Indicadores (5m)
              </div>

              {indState.loading && <div>Carregando indicadores...</div>}

              {indState.error && (
                <div className="error">
                  Erro: {indState.error}
                </div>
              )}

              {!indState.loading && !indState.error && ind && (
                <>
                  <div>Tendência: {trendLabel}</div>
                  <div>RSI 14: {rsi}</div>
                  <div>MACD hist: {macdHist}</div>
                  <div style={{ marginTop: "0.15rem" }}>
                    Mercado:{" "}
                    <span style={{ color: signalColor, fontWeight: 600 }}>
                      {signalText}
                    </span>
                  </div>
                </>
              )}

              {!indState.loading && !indState.error && !ind && (
                <div>Nenhum indicador disponível para este símbolo.</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default ActiveBotsPanel;
