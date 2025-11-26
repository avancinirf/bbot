// ==== BLOCK: BOTS_LIST - START ====
import React, { useEffect, useState } from "react";

const BotsList = ({ refreshKey = 0, onRefresh = () => {} }) => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activatingId, setActivatingId] = useState(null);

  const loadBots = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch("/api/bots/");
      if (!res.ok) throw new Error("Erro ao carregar bots");
      const data = await res.json();
      setBots(data);
    } catch (err) {
      console.error("Erro ao listar bots:", err);
      setError("Não foi possível carregar a lista de bots.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBots();
    // recarrega a lista quando o refreshKey muda (novo bot ou mudança de modo)
  }, [refreshKey]);

  const handleActivate = async (botId) => {
    try {
      setActivatingId(botId);
      setError(null);
      const res = await fetch(`/api/bots/${botId}/activate`, {
        method: "PATCH",
      });
      if (!res.ok) throw new Error("Erro ao ativar o bot");
      await res.json();
      // Recarregamos lista de bots
      await loadBots();
      onRefresh();
    } catch (err) {
      console.error("Erro ao ativar bot:", err);
      setError("Não foi possível ativar o bot.");
    } finally {
      setActivatingId(null);
    }
  };

  return (
    <div
      style={{
        borderRadius: "0.75rem",
        padding: "1rem 1.25rem",
        border: "1px solid rgba(148, 163, 184, 0.3)",
        background:
          "linear-gradient(135deg, rgba(15,23,42,0.85), rgba(15,23,42,0.6))",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: "0.5rem", fontSize: "1.1rem" }}>
        Bots configurados
      </h2>

      {loading && (
        <p style={{ fontSize: "0.9rem", color: "#9ca3af", margin: 0 }}>
          Carregando bots...
        </p>
      )}

      {error && (
        <p style={{ fontSize: "0.9rem", color: "#f97373", marginTop: "0.25rem" }}>
          {error}
        </p>
      )}

      {!loading && !error && bots.length === 0 && (
        <p style={{ fontSize: "0.9rem", color: "#9ca3af", margin: 0 }}>
          Ainda não existem bots cadastrados. Crie um bot via API por enquanto.
        </p>
      )}

      {!loading && !error && bots.length > 0 && (
        <ul
          style={{
            listStyle: "none",
            margin: "0.5rem 0 0",
            padding: 0,
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
          }}
        >
          {bots.map((bot) => (
            <li
              key={bot.id}
              style={{
                padding: "0.6rem 0.75rem",
                borderRadius: "0.6rem",
                border: "1px solid rgba(148, 163, 184, 0.35)",
                backgroundColor: "rgba(15,23,42,0.9)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "0.75rem",
              }}
            >
              <div>
                <div
                  style={{
                    fontSize: "0.95rem",
                    fontWeight: 500,
                    marginBottom: "0.15rem",
                  }}
                >
                  {bot.name}
                </div>
                <div
                  style={{
                    fontSize: "0.8rem",
                    color: "#9ca3af",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.1rem",
                  }}
                >
                  <span>
                    Saldo inicial:{" "}
                    <strong>{bot.initial_balance_usdt.toFixed(2)} USDT</strong>
                  </span>
                  <span>
                    Saldo atual:{" "}
                    <strong>{bot.current_balance_usdt.toFixed(2)} USDT</strong>
                  </span>
                  <span>
                    Stop loss:{" "}
                    <strong>{bot.stop_loss_percent.toFixed(1)}%</strong> ·{" "}
                    <span
                      style={{
                        textTransform: "none",
                        opacity: 0.8,
                      }}
                    >
                      modo: {bot.stop_behavior}
                    </span>
                  </span>
                </div>
              </div>

              <div style={{ textAlign: "right", fontSize: "0.8rem" }}>
                <span
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.35rem",
                    padding: "0.25rem 0.5rem",
                    borderRadius: "9999px",
                    border: bot.is_active
                      ? "1px solid rgba(34,197,94,0.5)"
                      : "1px solid rgba(148,163,184,0.4)",
                    backgroundColor: bot.is_active
                      ? "rgba(22,163,74,0.18)"
                      : "rgba(15,23,42,0.7)",
                    color: bot.is_active ? "#4ade80" : "#e5e7eb",
                  }}
                >
                  <span
                    style={{
                      width: "8px",
                      height: "8px",
                      borderRadius: "9999px",
                      backgroundColor: bot.is_active ? "#22c55e" : "#6b7280",
                    }}
                  />
                  <span>{bot.is_active ? "Ativo" : "Inativo"}</span>
                </span>

                <div
                  style={{
                    marginTop: "0.35rem",
                    display: "flex",
                    justifyContent: "flex-end",
                  }}
                >
                  <button
                    onClick={() => handleActivate(bot.id)}
                    disabled={activatingId === bot.id}
                    style={{
                      fontSize: "0.8rem",
                      padding: "0.25rem 0.65rem",
                      borderRadius: "9999px",
                      border: "none",
                      cursor: activatingId === bot.id ? "default" : "pointer",
                      opacity: activatingId === bot.id ? 0.7 : 1,
                      backgroundColor: bot.is_active
                        ? "#374151"
                        : "#22c55e",
                      color: "#f9fafb",
                    }}
                  >
                    {activatingId === bot.id
                      ? "Ativando..."
                      : bot.is_active
                      ? "Já ativo"
                      : "Ativar"}
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default BotsList;
// ==== BLOCK: BOTS_LIST - END ====
