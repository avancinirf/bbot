function BotTradesPanel({ bot, trades, loading, error }) {
  if (!bot) {
    return <p>Selecione um bot na lista para ver os trades.</p>;
  }

  if (loading) {
    return <p>Carregando trades de {bot.name}...</p>;
  }

  if (error) {
    return <p className="error">Erro ao carregar trades: {error}</p>;
  }

  if (!trades || trades.length === 0) {
    return <p>Nenhum trade registrado para este bot.</p>;
  }

  return (
    <div>
      <p style={{ fontSize: "0.8rem", marginBottom: "0.4rem" }}>
        Bot: <strong>{bot.name}</strong> ({bot.symbol}) — total de trades:{" "}
        <strong>{trades.length}</strong>
      </p>
      <div style={{ maxHeight: "220px", overflowY: "auto" }}>
        <table className="bot-table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Lado</th>
              <th>Preço</th>
              <th>Quantidade</th>
              <th>Valor (USDT)</th>
              <th>Simulado</th>
              <th>PnL</th>
              <th>Taxa</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((t) => (
              <tr key={t.id}>
                <td>
                  {t.created_at
                    ? new Date(t.created_at).toLocaleString()
                    : "-"}
                </td>
                <td>{t.side}</td>
                <td>{t.price.toFixed(4)}</td>
                <td>{t.qty}</td>
                <td>{t.quote_qty}</td>
                <td>{t.is_simulated ? "Sim" : "Não"}</td>
                <td>
                  {t.realized_pnl != null ? t.realized_pnl.toFixed(4) : "-"}
                </td>
                <td>
                  {t.fee_amount != null
                    ? `${t.fee_amount} ${t.fee_asset || ""}`.trim()
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

export default BotTradesPanel;
