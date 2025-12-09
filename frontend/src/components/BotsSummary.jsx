import { useEffect, useState } from "react";
import { getStatsSummary } from "../api/stats";

function BotsSummary() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStatsSummary();
      setStats(data);
    } catch (err) {
      setError(err?.message || "Erro ao carregar resumo dos bots.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const formatPnlClass = (value) => {
    if (value > 0) return "text-green";
    if (value < 0) return "text-red";
    return "";
  };

  return (
    <div className="account-box" style={{ marginTop: "0.5rem" }}>
      <div className="account-box-header">
        <div>Resumo dos bots (virtual)</div>
        <button
          className="btn btn-secondary"
          style={{ fontSize: "0.75rem", padding: "0.2rem 0.5rem" }}
          onClick={loadStats}
          disabled={loading}
        >
          {loading ? "Atualizando..." : "Atualizar"}
        </button>
      </div>

      {error && (
        <p className="error" style={{ marginTop: "0.25rem" }}>
          {error}
        </p>
      )}

      {!stats && !loading && !error && (
        <p style={{ fontSize: "0.8rem", marginTop: "0.25rem" }}>
          Nenhum dado de resumo disponível ainda.
        </p>
      )}

      {stats && (
        <div
          className="account-box-body"
          style={{ fontSize: "0.8rem", display: "grid", gap: "0.15rem" }}
        >
          <div>
            Bots cadastrados: <strong>{stats.total_bots}</strong>{" "}
            (online: <strong>{stats.total_bots_online}</strong>, bloqueados:{" "}
            <strong>{stats.total_bots_blocked}</strong>)
          </div>
          <div>
            Bots com posição aberta:{" "}
            <strong>{stats.total_bots_with_open_position}</strong>
          </div>
          <div>
            Saldo virtual livre (soma):{" "}
            <strong>{stats.total_saldo_usdt_livre.toFixed(4)} USDT</strong>
          </div>
          <div className={formatPnlClass(stats.total_realized_pnl)}>
            P/L realizado total:{" "}
            <strong>{stats.total_realized_pnl.toFixed(6)} USDT</strong>
          </div>
          <div>
            Taxas totais (USDT):{" "}
            <strong>{stats.total_fees_usdt.toFixed(6)} USDT</strong>
          </div>
          {stats.generated_at && (
            <div style={{ fontSize: "0.7rem", color: "#6b7280" }}>
              Atualizado em:{" "}
              {new Date(stats.generated_at).toLocaleString()}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default BotsSummary;
