// ==== BLOCK: ACTIVE_BOT_ASSETS - START ====
import React, { useEffect, useState } from "react";

const ActiveBotAssets = () => {
  const [bot, setBot] = useState(null);
  const [assets, setAssets] = useState([]);
  const [loadingBot, setLoadingBot] = useState(true);
  const [loadingAssets, setLoadingAssets] = useState(false);
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
      console.error("Erro ao carregar bot ativo (assets):", err);
      setError("Não foi possível carregar o bot ativo.");
      return null;
    } finally {
      setLoadingBot(false);
    }
  };

  const loadAssets = async (botId) => {
    try {
      setLoadingAssets(true);
      setError(null);
      const res = await fetch(`/api/bots/${botId}/assets/`);
      if (!res.ok) throw new Error("Erro ao carregar moedas do bot");
      const data = await res.json();
      setAssets(data);
    } catch (err) {
      console.error("Erro ao carregar assets do bot:", err);
      setError("Não foi possível carregar as moedas do bot.");
    } finally {
      setLoadingAssets(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      const active = await loadActiveBot();
      if (active && active.id) {
        await loadAssets(active.id);
      } else {
        setAssets([]);
      }
    };
    init();
  }, []);

  const hasNoBot = !loadingBot && !error && !bot;
  const hasNoAssets = bot && !loadingAssets && assets.length === 0;

  return (
    <div
      style={{
        marginTop: "1rem",
        borderRadius: "0.75rem",
        padding: "0.9rem 1rem",
        border: "1px solid rgba(148, 163, 184, 0.35)",
        background:
          "linear-gradient(135deg, rgba(15,23,42,0.85), rgba(15,23,42,0.75))",
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
        Moedas do bot ativo
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
          Nenhum bot ativo. Ative um bot para visualizar as moedas aqui.
        </p>
      )}

      {bot && !loadingBot && !error && (
        <>
          {loadingAssets && (
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
              Carregando moedas do bot <strong>{bot.name}</strong>...
            </p>
          )}

          {hasNoAssets && (
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
              Nenhuma moeda configurada para o bot{" "}
              <strong>{bot.name}</strong>.
              <br />
              Adicione moedas via API por enquanto (em breve, via interface).
            </p>
          )}

          {!loadingAssets && assets.length > 0 && (
            <div
              style={{
                marginTop: "0.35rem",
                borderRadius: "0.5rem",
                border: "1px solid rgba(148,163,184,0.4)",
                overflow: "hidden",
              }}
            >
              {/* Cabeçalho da tabela */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "1.1fr 1.3fr 1fr 1fr 1.3fr 1.3fr 1.3fr",
                  padding: "0.35rem 0.6rem",
                  fontSize: "0.75rem",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  backgroundColor: "rgba(15,23,42,0.95)",
                  color: "#9ca3af",
                }}
              >
                <span>Moeda</span>
                <span>Preço inicial (USDT)</span>
                <span>Compra (%)</span>
                <span>Venda (%)</span>
                <span>Qtd reservada</span>
                <span>Valor reservado (USDT)</span>
                <span>Flags</span>
              </div>

              {/* Linhas da tabela */}
              {assets.map((asset) => {
                const reservedAmount = asset.reserved_amount || 0;
                const price = asset.initial_price_usdt || 0;
                const reservedValueUsdt = reservedAmount * price;

                return (
                  <div
                    key={asset.id}
                    style={{
                      display: "grid",
                      gridTemplateColumns:
                        "1.1fr 1.3fr 1fr 1fr 1.3fr 1.3fr 1.3fr",
                      padding: "0.35rem 0.6rem",
                      fontSize: "0.8rem",
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

                    <span>{price.toFixed(4)}</span>

                    <span
                      style={{
                        color:
                          asset.buy_percent < 0
                            ? "#22c55e"
                            : asset.buy_percent > 0
                            ? "#f97316"
                            : "#9ca3af",
                      }}
                    >
                      {asset.buy_percent.toFixed(2)}%
                    </span>

                    <span
                      style={{
                        color:
                          asset.sell_percent > 0
                            ? "#22c55e"
                            : asset.sell_percent < 0
                            ? "#f97316"
                            : "#9ca3af",
                      }}
                    >
                      {asset.sell_percent.toFixed(2)}%
                    </span>

                    <span>
                      {reservedAmount > 0
                        ? reservedAmount.toFixed(8)
                        : "0"}
                    </span>

                    <span>
                      {reservedValueUsdt > 0
                        ? reservedValueUsdt.toFixed(4)
                        : "0.0000"}
                    </span>

                    <span
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        gap: "0.25rem",
                      }}
                    >
                      <span
                        style={{
                          padding: "0.05rem 0.4rem",
                          borderRadius: "9999px",
                          border: "1px solid rgba(148,163,184,0.5)",
                          fontSize: "0.7rem",
                          backgroundColor: asset.can_buy
                            ? "rgba(34,197,94,0.1)"
                            : "rgba(55,65,81,0.7)",
                          color: asset.can_buy ? "#4ade80" : "#9ca3af",
                        }}
                      >
                        buy {asset.can_buy ? "on" : "off"}
                      </span>
                      <span
                        style={{
                          padding: "0.05rem 0.4rem",
                          borderRadius: "9999px",
                          border: "1px solid rgba(148,163,184,0.5)",
                          fontSize: "0.7rem",
                          backgroundColor: asset.can_sell
                            ? "rgba(34,197,94,0.1)"
                            : "rgba(55,65,81,0.7)",
                          color: asset.can_sell ? "#4ade80" : "#9ca3af",
                        }}
                      >
                        sell {asset.can_sell ? "on" : "off"}
                      </span>
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ActiveBotAssets;
// ==== BLOCK: ACTIVE_BOT_ASSETS - END ====
