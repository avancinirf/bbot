// ==== BLOCK: ACTIVE_BOT_OPPORTUNITY - START ====
import React, { useEffect, useState } from "react";

const ActiveBotOpportunity = () => {
  const [bot, setBot] = useState(null);
  const [opportunity, setOpportunity] = useState(null);
  const [loadingBot, setLoadingBot] = useState(true);
  const [loadingOpp, setLoadingOpp] = useState(false);
  const [simLoading, setSimLoading] = useState(false);
  const [simResult, setSimResult] = useState(null);
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
      console.error("Erro ao carregar bot ativo (opportunity):", err);
      setError("Não foi possível carregar o bot ativo.");
      return null;
    } finally {
      setLoadingBot(false);
    }
  };

  const loadOpportunity = async (botId) => {
    try {
      setLoadingOpp(true);
      setError(null);
      const res = await fetch(`/api/bots/${botId}/opportunity/`);
      if (!res.ok) throw new Error("Erro ao carregar oportunidade de trade");
      const data = await res.json();
      setOpportunity(data);
    } catch (err) {
      console.error("Erro ao carregar oportunidade:", err);
      setError("Não foi possível carregar a oportunidade de trade.");
    } finally {
      setLoadingOpp(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      const active = await loadActiveBot();
      if (active && active.id) {
        await loadOpportunity(active.id);
      } else {
        setOpportunity(null);
      }
    };
    init();
  }, []);

  const handleRefresh = async () => {
    if (!bot || !bot.id) return;
    setSimResult(null); // limpar resultado anterior ao recalcular
    await loadOpportunity(bot.id);
  };

  const handleSimulatedTrade = async () => {
    if (!bot || !bot.id) return;
    try {
      setSimLoading(true);
      setError(null);
      setSimResult(null);

      const res = await fetch(`/api/bots/${bot.id}/simulate-trade/`, {
        method: "POST",
      });
      if (!res.ok) {
        throw new Error("Erro ao executar trade simulado");
      }
      const data = await res.json();
      setSimResult(data);

      // Depois de simular trade, faz sentido recalcular oportunidade
      // (pode ter mudado a condição de mercado das moedas)
      await loadOpportunity(bot.id);
    } catch (err) {
      console.error("Erro ao executar trade simulado:", err);
      setError("Não foi possível executar o trade simulado.");
    } finally {
      setSimLoading(false);
    }
  };

  const hasNoBot = !loadingBot && !error && !bot;

  const canExecuteSimTrade =
    bot &&
    !loadingBot &&
    !loadingOpp &&
    !simLoading &&
    opportunity &&
    opportunity.has_opportunity;

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
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "0.5rem",
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: "1rem",
            fontWeight: 500,
          }}
        >
          Oportunidade de trade
        </h3>

        <div
          style={{
            display: "flex",
            gap: "0.4rem",
          }}
        >
          <button
            onClick={handleRefresh}
            disabled={!bot || loadingOpp || simLoading}
            style={{
              fontSize: "0.75rem",
              padding: "0.25rem 0.6rem",
              borderRadius: "9999px",
              border: "1px solid rgba(148,163,184,0.7)",
              backgroundColor: "rgba(15,23,42,0.9)",
              color: "#e5e7eb",
              cursor:
                !bot || loadingOpp || simLoading ? "default" : "pointer",
              opacity: !bot || loadingOpp || simLoading ? 0.6 : 1,
            }}
          >
            {loadingOpp ? "Atualizando..." : "Recalcular"}
          </button>

          <button
            onClick={handleSimulatedTrade}
            disabled={!canExecuteSimTrade}
            style={{
              fontSize: "0.75rem",
              padding: "0.25rem 0.8rem",
              borderRadius: "9999px",
              border: "1px solid rgba(34,197,94,0.7)",
              backgroundColor: canExecuteSimTrade
                ? "rgba(22,163,74,0.25)"
                : "rgba(15,23,42,0.8)",
              color: canExecuteSimTrade ? "#bbf7d0" : "#6b7280",
              cursor: canExecuteSimTrade ? "pointer" : "default",
            }}
          >
            {simLoading
              ? "Executando..."
              : "Executar trade simulado"}
          </button>
        </div>
      </div>

      {loadingBot && (
        <p style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#9ca3af" }}>
          Verificando bot ativo...
        </p>
      )}

      {error && (
        <p style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#f97373" }}>
          {error}
        </p>
      )}

      {hasNoBot && (
        <p style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#9ca3af" }}>
          Nenhum bot ativo. Ative um bot para avaliar oportunidades.
        </p>
      )}

      {bot && !loadingBot && !error && opportunity && (
        <div
          style={{
            marginTop: "0.6rem",
            fontSize: "0.85rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
        >
          <p style={{ margin: 0, color: "#d1d5db" }}>{opportunity.message}</p>

          {!opportunity.has_opportunity && (
            <p style={{ margin: 0, fontSize: "0.8rem", color: "#9ca3af" }}>
              O bot ainda não encontrou um par onde uma moeda esteja em zona de
              venda e outra em zona de compra ao mesmo tempo.
            </p>
          )}

          {opportunity.has_opportunity && (
            <div
              style={{
                marginTop: "0.3rem",
                display: "flex",
                flexWrap: "wrap",
                gap: "0.75rem",
              }}
            >
              <div
                style={{
                  flex: "0 0 auto",
                  padding: "0.5rem 0.7rem",
                  borderRadius: "0.6rem",
                  border: "1px solid rgba(248,113,113,0.6)",
                  backgroundColor: "rgba(127,29,29,0.35)",
                  minWidth: "140px",
                }}
              >
                <div
                  style={{
                    fontSize: "0.7rem",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "#fecaca",
                    marginBottom: "0.15rem",
                  }}
                >
                  Vender
                </div>
                <div style={{ fontWeight: 600 }}>
                  {opportunity.sell_symbol}
                </div>
                {opportunity.sell_change_percent !== null && (
                  <div
                    style={{
                      fontSize: "0.78rem",
                      marginTop: "0.1rem",
                      color: "#fecaca",
                    }}
                  >
                    Variação: {opportunity.sell_change_percent.toFixed(2)}%
                  </div>
                )}
              </div>

              <div
                style={{
                  flex: "0 0 auto",
                  padding: "0.5rem 0.7rem",
                  borderRadius: "0.6rem",
                  border: "1px solid rgba(34,197,94,0.6)",
                  backgroundColor: "rgba(22,101,52,0.4)",
                  minWidth: "140px",
                }}
              >
                <div
                  style={{
                    fontSize: "0.7rem",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "#bbf7d0",
                    marginBottom: "0.15rem",
                  }}
                >
                  Comprar
                </div>
                <div style={{ fontWeight: 600 }}>
                  {opportunity.buy_symbol}
                </div>
                {opportunity.buy_change_percent !== null && (
                  <div
                    style={{
                      fontSize: "0.78rem",
                      marginTop: "0.1rem",
                      color: "#bbf7d0",
                    }}
                  >
                    Variação: {opportunity.buy_change_percent.toFixed(2)}%
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Resultado do último trade simulado */}
          {simResult && (
            <div
              style={{
                marginTop: "0.4rem",
                padding: "0.4rem 0.6rem",
                borderRadius: "0.6rem",
                border: simResult.executed
                  ? "1px solid rgba(34,197,94,0.6)"
                  : "1px solid rgba(148,163,184,0.6)",
                backgroundColor: simResult.executed
                  ? "rgba(22,163,74,0.18)"
                  : "rgba(31,41,55,0.8)",
                fontSize: "0.8rem",
              }}
            >
              <div style={{ marginBottom: "0.15rem" }}>
                {simResult.message}
              </div>
              {simResult.executed && simResult.amount_from && simResult.amount_to && (
                <div style={{ fontSize: "0.78rem", color: "#d1d5db" }}>
                  {simResult.sell_symbol} vendido:{" "}
                  {simResult.amount_from.toFixed(8)}{" "}
                  ({simResult.trade_unit_usdt.toFixed(2)} USDT ref.)<br />
                  {simResult.buy_symbol} comprado:{" "}
                  {simResult.amount_to.toFixed(8)} aprox.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ActiveBotOpportunity;
// ==== BLOCK: ACTIVE_BOT_OPPORTUNITY - END ====
