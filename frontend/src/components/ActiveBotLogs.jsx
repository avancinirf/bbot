// ==== BLOCK: ACTIVE_BOT_LOGS - START ====
import React, { useEffect, useState } from "react";

const ActiveBotLogs = ({ refreshKey = 0 }) => {
  const [bot, setBot] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loadingBot, setLoadingBot] = useState(true);
  const [loadingLogs, setLoadingLogs] = useState(false);
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
      console.error("Erro ao carregar bot ativo (logs):", err);
      setError("Não foi possível carregar o bot ativo.");
      return null;
    } finally {
      setLoadingBot(false);
    }
  };

  const loadLogs = async (botId) => {
    try {
      setLoadingLogs(true);
      setError(null);
      const res = await fetch(`/api/bots/${botId}/logs/`);
      if (!res.ok) throw new Error("Erro ao carregar logs do bot");
      const data = await res.json();
      setLogs(data);
    } catch (err) {
      console.error("Erro ao carregar logs do bot:", err);
      setError("Não foi possível carregar o histórico de operações.");
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      const active = await loadActiveBot();
      if (active && active.id) {
        await loadLogs(active.id);
      } else {
        setLogs([]);
      }
    };
    init();
    // recarrega logs quando o bot ativo muda
  }, [refreshKey]);

  const hasNoBot = !loadingBot && !error && !bot;
  const hasNoLogs = bot && !loadingLogs && logs.length === 0;

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
        Histórico de operações do bot
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
          Nenhum bot ativo. Ative um bot para visualizar o histórico aqui.
        </p>
      )}

      {bot && !loadingBot && !error && (
        <>
          {loadingLogs && (
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
              Carregando histórico de operações do bot{" "}
              <strong>{bot.name}</strong>...
            </p>
          )}

          {hasNoLogs && (
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
              Nenhuma operação registrada ainda para o bot{" "}
              <strong>{bot.name}</strong>.
            </p>
          )}

          {!loadingLogs && logs.length > 0 && (
            <div
              style={{
                marginTop: "0.35rem",
                borderRadius: "0.5rem",
                border: "1px solid rgba(148,163,184,0.4)",
                maxHeight: "220px",
                overflowY: "auto",
              }}
            >
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1.1fr 0.9fr 1.1fr 1.2fr",
                  padding: "0.35rem 0.6rem",
                  fontSize: "0.75rem",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  backgroundColor: "rgba(15,23,42,0.95)",
                  color: "#9ca3af",
                  position: "sticky",
                  top: 0,
                  zIndex: 1,
                }}
              >
                <span>Data / hora</span>
                <span>Par</span>
                <span>Side</span>
                <span>Quantidade</span>
                <span>Preço / Detalhe</span>
              </div>
              {logs.map((log) => {
                const date = new Date(log.created_at);
                const dateStr = date.toLocaleString("pt-BR", {
                  day: "2-digit",
                  month: "2-digit",
                  hour: "2-digit",
                  minute: "2-digit",
                });

                const pair = `${log.from_symbol}/${log.to_symbol}`;
                const amountStr = `${log.amount_from.toFixed(8)} → ${log.amount_to.toFixed(4)}`;

                return (
                  <div
                    key={log.id}
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1.1fr 0.9fr 1.1fr 1.2fr",
                      padding: "0.35rem 0.6rem",
                      fontSize: "0.78rem",
                      borderTop: "1px solid rgba(31,41,55,0.9)",
                      backgroundColor: "rgba(15,23,42,0.9)",
                    }}
                  >
                    <span style={{ color: "#9ca3af" }}>{dateStr}</span>
                    <span>{pair}</span>
                    <span
                      style={{
                        textTransform: "uppercase",
                        color:
                          log.side === "BUY"
                            ? "#22c55e"
                            : log.side === "SELL"
                            ? "#f97373"
                            : "#e5e7eb",
                      }}
                    >
                      {log.side}
                    </span>
                    <span>{amountStr}</span>
                    <span>
                      {log.price_usdt > 0
                        ? `${log.price_usdt.toFixed(4)} USDT`
                        : "-"}
                      {log.message && (
                        <span
                          style={{
                            display: "block",
                            fontSize: "0.7rem",
                            color: "#9ca3af",
                            marginTop: "0.1rem",
                          }}
                        >
                          {log.message}
                        </span>
                      )}
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

export default ActiveBotLogs;
// ==== BLOCK: ACTIVE_BOT_LOGS - END ====
