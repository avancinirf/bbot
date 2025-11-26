// ==== BLOCK: BOT_FORMS - START ====
import React, { useEffect, useMemo, useState } from "react";

const BotForms = () => {
  const [bots, setBots] = useState([]);
  const [loadingBots, setLoadingBots] = useState(true);
  const [botsError, setBotsError] = useState(null);

  const [creating, setCreating] = useState(false);
  const [createMessage, setCreateMessage] = useState(null);
  const [createError, setCreateError] = useState(null);

  const [name, setName] = useState("");
  const [initialBalance, setInitialBalance] = useState("100");
  const [stopLossPercent, setStopLossPercent] = useState("40");
  const [tradeMode, setTradeMode] = useState("SIMULATED");

  const [assetBotId, setAssetBotId] = useState("");
  const [symbol, setSymbol] = useState("");
  const [buyPercent, setBuyPercent] = useState("-3");
  const [sellPercent, setSellPercent] = useState("5");
  const [addingAsset, setAddingAsset] = useState(false);
  const [assetMessage, setAssetMessage] = useState(null);
  const [assetError, setAssetError] = useState(null);

  const loadBots = async () => {
    try {
      setLoadingBots(true);
      setBotsError(null);
      const res = await fetch("/api/bots/");
      if (!res.ok) throw new Error("Erro ao carregar bots");
      const data = await res.json();
      setBots(data);
      if (!assetBotId && data.length > 0) {
        setAssetBotId(String(data[0].id));
      }
    } catch (err) {
      console.error("Erro ao buscar bots:", err);
      setBotsError("Não foi possível carregar os bots.");
    } finally {
      setLoadingBots(false);
    }
  };

  useEffect(() => {
    loadBots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreateBot = async (evt) => {
    evt.preventDefault();
    setCreating(true);
    setCreateMessage(null);
    setCreateError(null);

    const initial = parseFloat(initialBalance);
    const stopLoss = parseFloat(stopLossPercent);

    if (Number.isNaN(initial) || initial <= 0) {
      setCreateError("Informe um saldo inicial válido (maior que zero).");
      setCreating(false);
      return;
    }

    if (Number.isNaN(stopLoss) || stopLoss <= 0) {
      setCreateError("Informe um stop-loss válido.");
      setCreating(false);
      return;
    }

    try {
      const resCreate = await fetch("/api/bots/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name || "Bot sem nome",
          initial_balance_usdt: initial,
          current_balance_usdt: initial,
        }),
      });

      if (!resCreate.ok) {
        throw new Error("Falha ao criar o bot.");
      }

      const created = await resCreate.json();

      const patchPromises = [];

      patchPromises.push(
        fetch(`/api/bots/${created.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stop_loss_percent: stopLoss }),
        })
      );

      if (tradeMode !== created.trade_mode) {
        patchPromises.push(
          fetch(`/api/bots/${created.id}/trade-mode`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ trade_mode: tradeMode }),
          })
        );
      }

      await Promise.all(patchPromises);

      setCreateMessage(`Bot "${created.name}" criado com sucesso!`);
      setName("");
      setInitialBalance("100");
      setStopLossPercent("40");
      setTradeMode("SIMULATED");

      await loadBots();
      window.location.reload();
    } catch (err) {
      console.error("Erro ao criar bot:", err);
      setCreateError("Erro ao criar o bot. Confira os dados e tente novamente.");
    } finally {
      setCreating(false);
    }
  };

  const handleAddAsset = async (evt) => {
    evt.preventDefault();
    setAddingAsset(true);
    setAssetMessage(null);
    setAssetError(null);

    if (!assetBotId) {
      setAssetError("Selecione um bot para adicionar a moeda.");
      setAddingAsset(false);
      return;
    }

    const buy = parseFloat(buyPercent);
    const sell = parseFloat(sellPercent);

    if (Number.isNaN(buy) || Number.isNaN(sell)) {
      setAssetError("Percentuais de compra e venda devem ser números.");
      setAddingAsset(false);
      return;
    }

    try {
      const res = await fetch(`/api/bots/${assetBotId}/assets/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: (symbol || "").toUpperCase(),
          buy_percent: buy,
          sell_percent: sell,
        }),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        const message = detail?.detail || "Erro ao adicionar moeda.";
        throw new Error(message);
      }

      const asset = await res.json();
      setAssetMessage(
        `Moeda ${asset.symbol} adicionada ao bot com buy=${asset.buy_percent}% e sell=${asset.sell_percent}%.`
      );
      setSymbol("");
      setBuyPercent("-3");
      setSellPercent("5");

      await loadBots();
      window.location.reload();
    } catch (err) {
      console.error("Erro ao adicionar moeda:", err);
      setAssetError(err.message || "Erro ao adicionar a moeda ao bot.");
    } finally {
      setAddingAsset(false);
    }
  };

  const botOptions = useMemo(
    () =>
      bots.map((bot) => (
        <option key={bot.id} value={bot.id}>
          {bot.name} {bot.is_active ? "(ativo)" : "(inativo)"}
        </option>
      )),
    [bots]
  );

  return (
    <div
      style={{
        marginTop: "1rem",
        borderRadius: "0.75rem",
        padding: "1rem 1.1rem",
        border: "1px solid rgba(148, 163, 184, 0.35)",
        background: "linear-gradient(135deg, rgba(15,23,42,0.8), rgba(15,23,42,0.65))",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      <div>
        <h3 style={{ margin: 0, marginBottom: "0.35rem", fontSize: "1rem" }}>
          Criar novo bot
        </h3>
        <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
          Preencha os campos abaixo para criar um bot e já configurar stop-loss e modo
          de trade.
        </p>

        <form
          onSubmit={handleCreateBot}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.45rem",
            marginTop: "0.6rem",
          }}
        >
          <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
            Nome do bot
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex.: Bot RSI"
              style={{
                width: "100%",
                marginTop: "0.2rem",
                padding: "0.45rem",
                borderRadius: "0.45rem",
                border: "1px solid rgba(148,163,184,0.35)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
              }}
            />
          </label>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
            <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
              Saldo inicial (USDT)
              <input
                type="number"
                step="0.01"
                value={initialBalance}
                onChange={(e) => setInitialBalance(e.target.value)}
                style={{
                  width: "100%",
                  marginTop: "0.2rem",
                  padding: "0.45rem",
                  borderRadius: "0.45rem",
                  border: "1px solid rgba(148,163,184,0.35)",
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#e5e7eb",
                }}
              />
            </label>

            <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
              Stop-loss (%)
              <input
                type="number"
                step="0.1"
                value={stopLossPercent}
                onChange={(e) => setStopLossPercent(e.target.value)}
                style={{
                  width: "100%",
                  marginTop: "0.2rem",
                  padding: "0.45rem",
                  borderRadius: "0.45rem",
                  border: "1px solid rgba(148,163,184,0.35)",
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#e5e7eb",
                }}
              />
            </label>
          </div>

          <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
            Modo de trade
            <select
              value={tradeMode}
              onChange={(e) => setTradeMode(e.target.value)}
              style={{
                width: "100%",
                marginTop: "0.2rem",
                padding: "0.45rem",
                borderRadius: "0.45rem",
                border: "1px solid rgba(148,163,184,0.35)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
              }}
            >
              <option value="SIMULATED">SIMULATED</option>
              <option value="REAL">REAL (MARKET SPOT)</option>
            </select>
          </label>

          <button
            type="submit"
            disabled={creating}
            style={{
              padding: "0.45rem 0.7rem",
              borderRadius: "0.5rem",
              border: "none",
              backgroundColor: creating ? "#475569" : "#22c55e",
              color: "#0f172a",
              fontWeight: 700,
              cursor: creating ? "default" : "pointer",
            }}
          >
            {creating ? "Criando bot..." : "Criar bot"}
          </button>

          {createError && (
            <div style={{ color: "#f97373", fontSize: "0.85rem" }}>{createError}</div>
          )}
          {createMessage && (
            <div style={{ color: "#a7f3d0", fontSize: "0.85rem" }}>{createMessage}</div>
          )}
        </form>
      </div>

      <div
        style={{
          borderTop: "1px solid rgba(148,163,184,0.25)",
          paddingTop: "0.75rem",
        }}
      >
        <h3 style={{ margin: 0, marginBottom: "0.35rem", fontSize: "1rem" }}>
          Adicionar moeda ao bot
        </h3>
        <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
          Só é possível adicionar moedas em bots inativos (o backend valida isso).
        </p>

        <form
          onSubmit={handleAddAsset}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.45rem",
            marginTop: "0.6rem",
          }}
        >
          <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
            Bot
            <select
              value={assetBotId}
              onChange={(e) => setAssetBotId(e.target.value)}
              disabled={loadingBots}
              style={{
                width: "100%",
                marginTop: "0.2rem",
                padding: "0.45rem",
                borderRadius: "0.45rem",
                border: "1px solid rgba(148,163,184,0.35)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
              }}
            >
              {loadingBots && <option>Carregando bots...</option>}
              {!loadingBots && bots.length === 0 && <option>Nenhum bot cadastrado</option>}
              {!loadingBots && bots.length > 0 && botOptions}
            </select>
          </label>

          <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
            Símbolo (ex.: ETH)
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="Moeda que será adicionada"
              style={{
                width: "100%",
                marginTop: "0.2rem",
                padding: "0.45rem",
                borderRadius: "0.45rem",
                border: "1px solid rgba(148,163,184,0.35)",
                backgroundColor: "rgba(15,23,42,0.9)",
                color: "#e5e7eb",
              }}
            />
          </label>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
            <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
              Percentual de compra (%)
              <input
                type="number"
                step="0.1"
                value={buyPercent}
                onChange={(e) => setBuyPercent(e.target.value)}
                style={{
                  width: "100%",
                  marginTop: "0.2rem",
                  padding: "0.45rem",
                  borderRadius: "0.45rem",
                  border: "1px solid rgba(148,163,184,0.35)",
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#e5e7eb",
                }}
              />
            </label>

            <label style={{ fontSize: "0.85rem", color: "#e5e7eb" }}>
              Percentual de venda (%)
              <input
                type="number"
                step="0.1"
                value={sellPercent}
                onChange={(e) => setSellPercent(e.target.value)}
                style={{
                  width: "100%",
                  marginTop: "0.2rem",
                  padding: "0.45rem",
                  borderRadius: "0.45rem",
                  border: "1px solid rgba(148,163,184,0.35)",
                  backgroundColor: "rgba(15,23,42,0.9)",
                  color: "#e5e7eb",
                }}
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={addingAsset}
            style={{
              padding: "0.45rem 0.7rem",
              borderRadius: "0.5rem",
              border: "none",
              backgroundColor: addingAsset ? "#475569" : "#60a5fa",
              color: "#0f172a",
              fontWeight: 700,
              cursor: addingAsset ? "default" : "pointer",
            }}
          >
            {addingAsset ? "Adicionando..." : "Adicionar moeda"}
          </button>

          {assetError && (
            <div style={{ color: "#f97373", fontSize: "0.85rem" }}>{assetError}</div>
          )}
          {assetMessage && (
            <div style={{ color: "#a7f3d0", fontSize: "0.85rem" }}>{assetMessage}</div>
          )}
          {botsError && (
            <div style={{ color: "#f97373", fontSize: "0.85rem" }}>{botsError}</div>
          )}
        </form>
      </div>
    </div>
  );
};

export default BotForms;
// ==== BLOCK: BOT_FORMS - END ====
