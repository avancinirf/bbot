import { useEffect, useState } from "react";
import { getLatestIndicator } from "../api/indicators";

function buildAnalysis(bot, ind) {
  if (!ind) {
    return "Sem indicadores suficientes para análise neste símbolo.";
  }

  const parts = [];

  // 1) Sinal de mercado
  if (ind.market_signal_compra) {
    parts.push(
      "Sinal de COMPRA ativo: modelo indica viés altista no curto prazo."
    );
  } else if (ind.market_signal_venda) {
    parts.push(
      "Sinal de VENDA ativo: modelo indica viés baixista no curto prazo."
    );
  } else {
    parts.push("Sem sinal claro de compra ou venda neste momento.");
  }

  // 2) Tendência geral
  const trend = (ind.trend_label || "").toLowerCase();
  if (trend === "bullish") {
    parts.push(
      "Tendência: bullish (alta). Preço acima das médias, viés positivo."
    );
  } else if (trend === "bearish") {
    parts.push(
      "Tendência: bearish (baixa). Preço abaixo das médias, viés negativo."
    );
  } else if (trend === "neutral") {
    parts.push(
      "Tendência: neutra. Mercado mais lateral ou sem direção definida."
    );
  } else {
    parts.push("Tendência: não determinada pelos indicadores atuais.");
  }

  // 3) RSI
  if (ind.rsi14 != null) {
    const rsi = Number(ind.rsi14);
    if (rsi >= 70) {
      parts.push(
        `RSI em zona de sobrecompra (${rsi.toFixed(
          2
        )}). Pode haver risco de correção.`
      );
    } else if (rsi <= 30) {
      parts.push(
        `RSI em zona de sobrevenda (${rsi.toFixed(
          2
        )}). Mercado pode estar esticado para baixo.`
      );
    } else {
      parts.push(
        `RSI em zona neutra (${rsi.toFixed(
          2
        )}). Sem excesso claro de compra ou venda.`
      );
    }
  }

  // 4) MACD hist (força/momentum)
  if (ind.macd_hist != null) {
    const h = Number(ind.macd_hist);
    const absH = Math.abs(h);

    if (absH < 20) {
      parts.push(
        "MACD hist próximo de zero: momentum fraco, movimentos podem estar perdendo força."
      );
    } else if (h > 0) {
      parts.push(
        "MACD hist positivo: momentum comprador predominando no momento."
      );
    } else if (h < 0) {
      parts.push(
        "MACD hist negativo: momentum vendedor predominando no momento."
      );
    }
  }

  // 5) Estado da posição do bot
  if (bot.has_open_position) {
    parts.push(
      "Bot está com posição aberta. Acompanhe stop loss e take profit configurados."
    );
  } else {
    parts.push(
      "Bot sem posição aberta neste momento. Próxima operação dependerá dos sinais do modelo."
    );
  }

  return parts.join(" ");
}

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

        // Texto e cor do "Mercado"
        let signalText = "Sem sinal";
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

        const analysisText = buildAnalysis(bot, ind);

        return (
          <div key={bot.id} className="bot-card">
            {/* Cabeçalho do card */}
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
                Status: <strong>{bot.status}</strong>
              </div>
            </div>

            {/* Info básica do bot */}
            <div style={{ fontSize: "0.8rem" }}>
              <div>
                Saldo virtual livre: {bot.saldo_usdt_livre.toFixed(2)} USDT
              </div>
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
                <div className="error">Erro: {indState.error}</div>
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

            {/* Bloco de análise automática */}
            <div
              style={{
                marginTop: "0.35rem",
                paddingTop: "0.3rem",
                borderTop: "1px dashed #d1d5db",
                fontSize: "0.75rem",
                color: "#374151",
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  marginBottom: "0.18rem",
                  fontSize: "0.75rem",
                  opacity: 0.9,
                }}
              >
                Análise automática (beta)
              </div>
              <div style={{ lineHeight: 1.3 }}>{analysisText}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default ActiveBotsPanel;
