import { useEffect, useState } from "react";
import { getRecentTrades } from "../api/trades";

function TradesBoard() {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [limit, setLimit] = useState(50);
  const [botId, setBotId] = useState("");
  const [symbol, setSymbol] = useState("BTCUSDT");

  const loadTrades = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await getRecentTrades({
        limit: Number(limit) || 50,
        botId: botId !== "" ? Number(botId) : undefined,
        symbol: symbol || undefined,
      });

      setTrades(data);
    } catch (err) {
      console.error(err);
      setError(err?.message || "Erro ao carregar trades.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrades();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    loadTrades();
  };

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "0.4rem",
        }}
      >
        <h2 style={{ margin: 0 }}>Histórico de trades</h2>
        <button
          className="btn btn-secondary btn-xs"
          onClick={loadTrades}
          disabled={loading}
        >
          {loading ? "Atualizando..." : "Atualizar"}
        </button>
      </div>

      <p style={{ fontSize: "0.75rem", color: "#6b7280", marginBottom: "0.4rem" }}>
        Lista os trades mais recentes de todos os bots. Você pode filtrar por
        bot e símbolo. Os dados vêm diretamente da tabela de trades da API.
      </p>

      {error && (
        <p className="error" style={{ fontSize: "0.8rem" }}>
          {error}
        </p>
      )}

      <form
        onSubmit={handleSubmit}
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "0.4rem",
          fontSize: "0.8rem",
          marginBottom: "0.4rem",
        }}
      >
        <div>
          <label>
            Limite
            <input
              type="number"
              min={1}
              max={500}
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
            />
          </label>
        </div>
        <div>
          <label>
            Bot ID (opcional)
            <input
              type="number"
              min={1}
              value={botId}
              onChange={(e) => setBotId(e.target.value)}
            />
          </label>
        </div>
        <div>
          <label>
            Símbolo (opcional)
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
            />
          </label>
        </div>
        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button
            type="submit"
            className="btn btn-secondary btn-xs"
            disabled={loading}
          >
            Aplicar filtros
          </button>
        </div>
      </form>

      <div
        style={{
          maxHeight: "260px",
          overflow: "auto",
          borderRadius: "0.4rem",
          border: "1px solid #e5e7eb",
        }}
      >
        <table className="bot-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Bot</th>
              <th>Símbolo</th>
              <th>Lado</th>
              <th>Preço</th>
              <th>Qtd</th>
              <th>Quote (USDT)</th>
              <th>Taxa</th>
              <th>P/L</th>
              <th>Simulado</th>
              <th>Data</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 && (
              <tr>
                <td colSpan={11} style={{ textAlign: "center", fontSize: "0.8rem" }}>
                  Nenhum trade encontrado.
                </td>
              </tr>
            )}

            {trades.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>{t.bot_id}</td>
                <td>{t.symbol}</td>
                <td>{t.side}</td>
                <td>{Number(t.price).toFixed(2)}</td>
                <td>{Number(t.qty).toFixed(8)}</td>
                <td>{Number(t.quote_qty).toFixed(6)}</td>
                <td>
                  {t.fee_amount != null
                    ? `${Number(t.fee_amount).toFixed(6)} ${
                        t.fee_asset || ""
                      }`
                    : "-"}
                </td>
                <td>
                  {t.realized_pnl != null
                    ? Number(t.realized_pnl).toFixed(6)
                    : "-"}
                </td>
                <td>{t.is_simulated ? "Sim" : "Não"}</td>
                <td>
                  {t.created_at
                    ? new Date(t.created_at).toLocaleString()
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TradesBoard;
