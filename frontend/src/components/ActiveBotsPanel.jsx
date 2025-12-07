function ActiveBotsPanel({ bots }) {
  if (!bots.length) {
    return <p>Nenhum bot ativo no momento.</p>;
  }

  return (
    <div className="bot-cards">
      {bots.map((bot) => (
        <div className="bot-card" key={bot.id}>
          <h3>{bot.name}</h3>
          <p>
            <strong>Par:</strong> {bot.symbol}
          </p>
          <p>
            <strong>Saldo virtual livre:</strong> {bot.saldo_usdt_livre.toFixed(2)} USDT
          </p>
          <p>
            <strong>Status:</strong> {bot.status}
          </p>
          <p>
            <strong>Bloqueado:</strong> {bot.blocked ? "Sim" : "Não"}
          </p>
          <p>
            <strong>Posição aberta:</strong> {bot.has_open_position ? "Sim" : "Não"}
          </p>
          <p>
            <strong>Qtd moeda (virtual):</strong> {bot.qty_moeda}
          </p>
          <p>
            <strong>Última compra:</strong>{" "}
            {bot.last_buy_price != null ? bot.last_buy_price : "-"}
          </p>
          <p>
            <strong>Última venda:</strong>{" "}
            {bot.last_sell_price != null ? bot.last_sell_price : "-"}
          </p>
        </div>
      ))}
    </div>
  );
}

export default ActiveBotsPanel;
