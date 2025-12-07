import { useState } from "react";

function BotForm({ onCreate, creating }) {
  const [form, setForm] = useState({
    name: "",
    symbol: "BTCUSDT",
    saldo_usdt_limit: 100,
    stop_loss_percent: 20,
    vender_stop_loss: true,
    comprar_ao_iniciar: false,
    compra_mercado: true,
    venda_mercado: true,
    valor_de_trade_usdt: 10,
    porcentagem_compra: 0,
    porcentagem_venda: 0,
  });

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]:
        type === "checkbox"
          ? checked
          : type === "number"
          ? Number(value)
          : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreate(form);
  };

  return (
    <form className="bot-form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label>Nome do bot</label>
        <input
          type="text"
          name="name"
          value={form.name}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-row">
        <label>Par (símbolo Binance)</label>
        <input
          type="text"
          name="symbol"
          value={form.symbol}
          onChange={handleChange}
          required
        />
        <small>Ex: BTCUSDT, ETHUSDT, etc.</small>
      </div>

      <div className="form-row">
        <label>Saldo virtual máximo (USDT)</label>
        <input
          type="number"
          name="saldo_usdt_limit"
          value={form.saldo_usdt_limit}
          onChange={handleChange}
          min={0}
          step="0.01"
          required
        />
      </div>

      <div className="form-row">
        <label>Valor de cada trade (USDT)</label>
        <input
          type="number"
          name="valor_de_trade_usdt"
          value={form.valor_de_trade_usdt}
          onChange={handleChange}
          min={1}
          step="0.01"
          required
        />
      </div>

      <div className="form-row form-row-inline">
        <label>
          <input
            type="checkbox"
            name="comprar_ao_iniciar"
            checked={form.comprar_ao_iniciar}
            onChange={handleChange}
          />{" "}
          Comprar ao iniciar
        </label>
        <label>
          <input
            type="checkbox"
            name="vender_stop_loss"
            checked={form.vender_stop_loss}
            onChange={handleChange}
          />{" "}
          Vender no stop loss
        </label>
      </div>

      <div className="form-row">
        <label>Stop loss (%)</label>
        <input
          type="number"
          name="stop_loss_percent"
          value={form.stop_loss_percent}
          onChange={handleChange}
          min={0}
          step="0.1"
        />
        <small>Ex: 20 = -20% em relação ao valor inicial.</small>
      </div>

      <div className="form-row">
        <label>Porcentagem de compra (%)</label>
        <input
          type="number"
          name="porcentagem_compra"
          value={form.porcentagem_compra}
          onChange={handleChange}
          min={0}
          step="0.1"
        />
        <small>
          0 desativa. Ex: 5 = só compra se o preço estiver &le; -5% abaixo do
          valor inicial.
        </small>
      </div>

      <div className="form-row">
        <label>Porcentagem de venda (take profit) (%)</label>
        <input
          type="number"
          name="porcentagem_venda"
          value={form.porcentagem_venda}
          onChange={handleChange}
          min={0}
          step="0.1"
        />
        <small>
          0 desativa. Ex: 5 = vende quando o preço estiver &ge; +5% acima do
          valor inicial.
        </small>
      </div>

      <div className="form-row form-row-inline">
        <label>
          <input
            type="checkbox"
            name="compra_mercado"
            checked={form.compra_mercado}
            onChange={handleChange}
          />{" "}
          Usar sinal de mercado na compra (futuro)
        </label>
        <label>
          <input
            type="checkbox"
            name="venda_mercado"
            checked={form.venda_mercado}
            onChange={handleChange}
          />{" "}
          Usar sinal de mercado na venda (futuro)
        </label>
      </div>

      <div className="form-actions">
        <button className="btn" type="submit" disabled={creating}>
          {creating ? "Criando..." : "Criar bot"}
        </button>
      </div>
    </form>
  );
}

export default BotForm;
