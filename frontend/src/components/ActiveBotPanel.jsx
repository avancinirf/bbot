// ==== BLOCK: ACTIVE_BOT_PANEL - START ====
import React, { useEffect, useState } from "react";

const ActiveBotPanel = () => {
  const [bot, setBot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [rebalancing, setRebalancing] = useState(false);
  const [rebalanceMessage, setRebalanceMessage] = useState(null);

  const loadActiveBot = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch("/api/bots/active");
      if (!res.ok) throw new Error("Erro ao carregar bot ativo");
      const data = await res.json();
      setBot(data);
    } catch (err) {
      console.error("Erro ao carregar bot ativo:", err);
      setError("Não foi possível carregar o bot ativo.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadActiveBot();
  }, []);

  const formatDateTime = (value) => {
    if (!value) return "Ainda não executado";
    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  };

  const handleRebalanceNow = async () => {
    if (!bot) return;
    try {
      setRebalancing(true);
      setRebalanceMessage(null);

      const res = await fetch(`/api/bots/${bot.id}/rebalance/`, {
        method: "POST",
      });

      if (!res.ok) {
        throw new Error("Erro ao rebalancear o bot.");
      }

      const data = await res.json();

      setRebalanceMessage(
        data.insufficient_funds
          ? "Rebalance concluído com saldo insuficiente (nem todas as moedas chegaram em 10 USDT)."
          : "Rebalance concluído com sucesso."
      );

      loadActiveBot();
    } catch (err) {
      console.error("Erro ao rebalancear:", err);
      setRebalanceMessage("Erro ao rebalancear o bot.");
    } finally {
      setRebalancing(false);
    }
  };

  // ===== NOVA FUNÇÃO: ALTERAR MODO REAL / SIMULATED =====
  const toggleTradeMode = async () => {
    if (!bot) return;

    const newMode = bot.trade_mode === "REAL" ? "SIMULATED" : "REAL";

    try {
      const res = await fetch(`/api/bots/${bot.id}/trade-mode`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trade_mode: newMode }),
      });

      if (!res.ok) {
        console.error("Erro ao trocar trade_mode:", res.status);
        return;
      }

      const updated = await res.json();
      setBot(updated);
    } catch (err) {
      console.error("Erro ao trocar trade_mode:", err);
    }
  };
  // ===== FIM NOVA FUNÇÃO =====

  return (
    <div
      style={{
        borderRadius: "0.75rem",
        padding: "1rem 1.25rem",
        border: "1px solid rgba(148, 163, 184, 0.3)",
        background:
          "linear-gradient(135deg, rgba(15,23,42,0.95), rgba(15,23,42,0.75))",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: "0.75rem", fontSize: "1.1rem" }}>
        Bot ativo
      </h2>

      {loading && (
        <p style={{ margin: 0, fontSize: "0.9rem", color: "#9ca3af" }}>
          Carregando informações do bot ativo...
        </p>
      )}

      {error && (
        <p style={{ margin: 0, fontSize: "0.9rem", color: "#f97373" }}>
          {error}
        </p>
      )}

      {!loading && !error && !bot && (
        <p style={{ margin: 0, fontSize: "0.9rem", color: "#9ca3af" }}>
          Nenhum bot está ativo no momento.
          <br />
          Ative um bot pela API (ou futuramente pela interface) para ver os
          detalhes aqui.
        </p>
      )}

      {!loading && !error && bot && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
          }}
        >
          {/* Cabeçalho com nome, ID e botões */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "0.75rem",
            }}
          >
            <div>
              <div
                style={{
                  fontSize: "1rem",
                  fontWeight: 600,
                  marginBottom: "0.25rem",
                }}
              >
                {bot.name}
              </div>
              <div
                style={{
                  fontSize: "0.85rem",
                  color: "#9ca3af",
                }}
              >
                ID: {bot.id}
              </div>
            </div>

            <div
              style={{
                display: "flex",
                gap: "0.5rem",
                alignItems: "center",
              }}
            >
              {/* Botão de Rebalancear */}
              <button
                onClick={handleRebalanceNow}
                disabled={rebalancing || !bot.is_active}
                style={{
                  padding: "0.3rem 0.8rem",
                  borderRadius: "999px",
                  border: "1px solid rgba(96,165,250,0.7)",
                  backgroundColor: rebalancing
                    ? "rgba(37, 99, 235, 0.2)"
                    : "rgba(37, 99, 235, 0.15)",
                  color: "#bfdbfe",
                  fontSize: "0.75rem",
                  fontWeight: 500,
                  cursor:
                    rebalancing || !bot.is_active ? "not-allowed" : "pointer",
                  opacity: bot.is_active ? 1 : 0.6,
                }}
              >
                {rebalancing ? "Rebalanceando..." : "Rebalancear agora"}
              </button>

              {/* Indicador de ativo/parado */}
              <span
                style={{
                  padding: "0.15rem 0.5rem",
                  borderRadius: "999px",
                  fontSize: "0.75rem",
                  fontWeight: 500,
                  border: "1px solid rgba(34,197,94,0.4)",
                  backgroundColor: bot.is_active
                    ? "rgba(22,163,74,0.15)"
                    : "rgba(148,163,184,0.15)",
                  color: bot.is_active ? "#4ade80" : "#e5e7eb",
                }}
              >
                {bot.is_active ? "Ativo" : "Parado"}
              </span>
            </div>
          </div>

          {/* NOVO BLOCO: Modo REAL/SIMULATED */}
          <div
            style={{
              fontSize: "0.9rem",
              color: "#e5e7eb",
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              marginTop: "0.25rem",
            }}
          >
            <strong>Modo de Trade:</strong>

            {bot.trade_mode === "REAL" ? (
              <span style={{ color: "#4ade80", fontWeight: 600 }}>
                REAL ●
              </span>
            ) : (
              <span style={{ color: "#facc15", fontWeight: 600 }}>
                SIMULATED ●
              </span>
            )}

            <button
              onClick={toggleTradeMode}
              style={{
                padding: "0.25rem 0.65rem",
                borderRadius: "0.5rem",
                backgroundColor: "rgba(71,85,105,0.4)",
                border: "1px solid rgba(148,163,184,0.4)",
                color: "#e5e7eb",
                fontSize: "0.75rem",
                cursor: "pointer",
              }}
            >
              {bot.trade_mode === "REAL"
                ? "Mudar para SIMULATED"
                : "Mudar para REAL"}
            </button>
          </div>

          {/* Linha de saldos e stop-loss */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "1rem",
              fontSize: "0.9rem",
            }}
          >
            <div>
              <div style={{ color: "#9ca3af", fontSize: "0.8rem" }}>
                Saldo inicial
              </div>
              <div style={{ fontWeight: 500 }}>
                {bot.initial_balance_usdt.toFixed(2)} USDT
              </div>
            </div>
            <div>
              <div style={{ color: "#9ca3af", fontSize: "0.8rem" }}>
                Saldo atual
              </div>
              <div style={{ fontWeight: 500 }}>
                {bot.current_balance_usdt.toFixed(2)} USDT
              </div>
            </div>
            <div>
              <div style={{ color: "#9ca3af", fontSize: "0.8rem" }}>
                Stop loss
              </div>
              <div style={{ fontWeight: 500 }}>
                {bot.stop_loss_percent.toFixed(1)}%
                <span
                  style={{
                    marginLeft: "0.35rem",
                    fontSize: "0.8rem",
                    opacity: 0.8,
                  }}
                >
                  ({bot.stop_behavior})
                </span>
              </div>
            </div>
          </div>

          {/* Linha com informações de rebalance */}
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.75rem",
              fontSize: "0.8rem",
              color: "#9ca3af",
            }}
          >
            <div>
              Último rebalance:{" "}
              <span style={{ fontWeight: 500 }}>
                {formatDateTime(bot.last_rebalance_at)}
              </span>
            </div>

            <span
              style={{
                padding: "0.15rem 0.6rem",
                borderRadius: "999px",
                border: bot.last_rebalance_insufficient
                  ? "1px solid rgba(245,158,11,0.6)"
                  : "1px solid rgba(16,185,129,0.6)",
                backgroundColor: bot.last_rebalance_insufficient
                  ? "rgba(251,191,36,0.08)"
                  : "rgba(16,185,129,0.08)",
                color: bot.last_rebalance_insufficient ? "#fbbf24" : "#6ee7b7",
                fontSize: "0.75rem",
                fontWeight: 500,
              }}
            >
              {bot.last_rebalance_insufficient
                ? "Último rebalance com saldo insuficiente"
                : "Último rebalance ok"}
            </span>
          </div>

          {/* Mensagem do rebalance manual */}
          {rebalanceMessage && (
            <div
              style={{
                marginTop: "0.25rem",
                fontSize: "0.8rem",
                color: "#e5e7eb",
                backgroundColor: "rgba(15,23,42,0.8)",
                borderRadius: "0.5rem",
                padding: "0.35rem 0.6rem",
                border: "1px solid rgba(148,163,184,0.4)",
              }}
            >
              {rebalanceMessage}
            </div>
          )}

          {/* Placeholder para futuras informações */}
          <div
            style={{
              marginTop: "0.25rem",
              fontSize: "0.8rem",
              color: "#9ca3af",
              borderTop: "1px solid rgba(148,163,184,0.35)",
              paddingTop: "0.5rem",
            }}
          >
            Em breve aqui vamos mostrar:
            <ul
              style={{
                margin: "0.25rem 0 0",
                paddingLeft: "1.1rem",
              }}
            >
              <li>Lista de moedas configuradas para este bot</li>
              <li>Indicadores de compra/venda por moeda</li>
              <li>Resumo das últimas operações do bot</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActiveBotPanel;
// ==== BLOCK: ACTIVE_BOT_PANEL - END ====
