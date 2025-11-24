// ==== BLOCK: ACTIVE_BOT_MARKET_STATUS - START ====
import React, { useEffect, useState } from "react";

const ActiveBotMarketStatus = () => {
  const [bot, setBot] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loadingBot, setLoadingBot] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [error, setError] = useState(null);

  const loadActiveBot = async () => {
    try {
      setLoadingBot(true);
      setError(null);
      const res = await fetch("/api/bots/active");
      if (!res.ok) throw new Error("Erro ao carregar bot ativo");
      const data = await res.json();
      setBot(data); // pode ser null
      return data;
    } catch (err) {
      console.error("Erro ao carregar bot ativo (market):", err);
      setError("Não foi possível carregar o bot ativo.");
      return null;
    } finally {
      setLoadingBot(false);
    }
  };

  const loadAnalysis = async (botId) => {
    try {
      setLoadingAnalysis(true);
      setError(null);
      const res = await fetch(`/api/bots/${botId}/analysis/`);
      if (!res.ok) throw new Error("Erro ao carregar análise do bot");
      const data = await res.json();
      setAnalysis(data);
    } catch (err) {
      console.error("Erro ao carregar análise do bot:", err);
      setError("Não foi possível carregar a análise de mercado.");
    } finally {
      setLoadingAnalysis(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      const active = await loadActiveBot();
      if (active && active.id) {
        await loadAnalysis(active.id);
      } else {
        setAnalysis(null);
      }
    };
    init();
  }, []);

  const hasNoBot = !loadingBot && !error && !bot;

  return (
    <div
      style={{
        marginTop: "1rem",
        borderRadius: "0.75rem",
        padding: "0.9rem 1rem",
        border: "1px solid rgba(148, 163, 184, 0.35)",
        background:
          "linear-gradient(135deg, rgba(15,23,42,0.9), rgba(15,23,42,0.75))",
      }}
    >
      <h3
        style={{
          marginTop: 0,
          marginBottom: "0.5rem",
          fontSize: "1rem",
          fontWeight: 500,
        }}
      >
        Estado de mercado do bot
      </h3>

      {loadingBot && (
        <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
          Verificando bot ativo...
        </p>
      )}

      {error && (
        <p style={{ margin: 0, fontSize: "0.85rem", color: "#f97373" }}>
          {error}
        </p>
      )}

      {hasNoBot && (
        <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
          Nenhum bot ativo. Ative um bot para ver o estado de mercado aqui.
        </p>
      )}

      {bot && !loadingBot && !error && (
        <>
          {loadingAnalysis && (
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
              Calculando análise de mercado para o bot{" "}
              <strong>{bot.name}</strong>...
            </p>
          )}

          {analysis && !loadingAnalysis && (
            <>
              {/* Resumo de candidatos */}
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.75rem",
                  marginBottom: "0.6rem",
                  fontSize: "0.8rem",
                }}
              >
                <div>
                  <div
                    style={{
                      textTransform: "uppercase",
                      fontSize: "0.7rem",
                      color: "#9ca3af",
                      marginBottom: "0.2rem",
                    }}
                  >
                    Candidatas para compra
                  </div>
                  {analysis.buy_candidates.length === 0 ? (
                    <span style={{ color: "#9ca3af" }}>Nenhuma no momento</span>
                  ) : (
                    <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                      {analysis.buy_candidates.map((symbol) => (
                        <span
                          key={symbol}
                          style={{
                            padding: "0.15rem 0.4rem",
                            borderRadius: "9999px",
                            border: "1px solid rgba(34,197,94,0.5)",
                            color: "#4ade80",
                            fontSize: "0.75rem",
                          }}
                        >
                          {symbol}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <div
                    style={{
                      textTransform: "uppercase",
                      fontSize: "0.7rem",
                      color: "#9ca3af",
                      marginBottom: "0.2rem",
                    }}
                  >
                    Candidatas para venda
                  </div>
                  {analysis.sell_candidates.length === 0 ? (
                    <span style={{ color: "#9ca3af" }}>Nenhuma no momento</span>
                  ) : (
                    <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                      {analysis.sell_candidates.map((symbol) => (
                        <span
                          key={symbol}
                          style={{
                            padding: "0.15rem 0.4rem",
                            borderRadius: "9999px",
                            border: "1px solid rgba(248,113,113,0.6)",
                            color: "#fecaca",
                            fontSize: "0.75rem",
                          }}
                        >
                          {symbol}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Tabela detalhada */}
              <div
                style={{
                  borderRadius: "0.5rem",
                  border: "1px solid rgba(148,163,184,0.4)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns:
                      "1.1fr 1.2fr 1.2fr 1.1fr 1.1fr 1.1fr",
                    padding: "0.35rem 0.6rem",
                    fontSize: "0.75rem",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    backgroundColor: "rgba(15,23,42,0.95)",
                    color: "#9ca3af",
                  }}
                >
                  <span>Moeda</span>
                  <span>Preço inicial</span>
                  <span>Preço atual</span>
                  <span>Variação</span>
                  <span>Trigger buy / sell</span>
                  <span>Decisão</span>
                </div>

                {analysis.assets.map((asset) => {
                  const change = asset.change_percent;
                  const changeStr = `${change.toFixed(2)}%`;
                  const changeColor =
                    change > 0 ? "#22c55e" : change < 0 ? "#f97373" : "#9ca3af";

                  const buyStr = `${asset.buy_threshold_percent.toFixed(2)}%`;
                  const sellStr = `${asset.sell_threshold_percent.toFixed(2)}%`;

                  return (
                    <div
                      key={asset.symbol}
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "1.1fr 1.2fr 1.2fr 1.1fr 1.1fr 1.1fr",
                        padding: "0.35rem 0.6rem",
                        fontSize: "0.78rem",
                        borderTop: "1px solid rgba(31,41,55,0.9)",
                        backgroundColor: "rgba(15,23,42,0.9)",
                      }}
                    >
                      <span
                        style={{
                          fontWeight: 500,
                          color: "#e5e7eb",
                        }}
                      >
                        {asset.symbol}
                      </span>

                      <span>{asset.initial_price_usdt.toFixed(4)} USDT</span>
                      <span>{asset.current_price_usdt.toFixed(4)} USDT</span>

                      <span style={{ color: changeColor }}>{changeStr}</span>

                      <span
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.1rem",
                        }}
                      >
                        <span style={{ color: "#9ca3af", fontSize: "0.72rem" }}>
                          Buy: {buyStr}
                        </span>
                        <span style={{ color: "#9ca3af", fontSize: "0.72rem" }}>
                          Sell: {sellStr}
                        </span>
                      </span>

                      <span
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          gap: "0.15rem",
                          fontSize: "0.72rem",
                        }}
                      >
                        <span
                          style={{
                            padding: "0.15rem 0.4rem",
                            borderRadius: "9999px",
                            border: asset.can_buy_now
                              ? "1px solid rgba(34,197,94,0.6)"
                              : "1px solid rgba(55,65,81,0.8)",
                            backgroundColor: asset.can_buy_now
                              ? "rgba(34,197,94,0.12)"
                              : "rgba(15,23,42,0.9)",
                            color: asset.can_buy_now ? "#4ade80" : "#9ca3af",
                          }}
                        >
                          Buy now: {asset.can_buy_now ? "SIM" : "não"}
                        </span>
                        <span
                          style={{
                            padding: "0.15rem 0.4rem",
                            borderRadius: "9999px",
                            border: asset.can_sell_now
                              ? "1px solid rgba(248,113,113,0.7)"
                              : "1px solid rgba(55,65,81,0.8)",
                            backgroundColor: asset.can_sell_now
                              ? "rgba(248,113,113,0.12)"
                              : "rgba(15,23,42,0.9)",
                            color: asset.can_sell_now ? "#fecaca" : "#9ca3af",
                          }}
                        >
                          Sell now: {asset.can_sell_now ? "SIM" : "não"}
                        </span>
                      </span>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default ActiveBotMarketStatus;
// ==== BLOCK: ACTIVE_BOT_MARKET_STATUS - END ====
