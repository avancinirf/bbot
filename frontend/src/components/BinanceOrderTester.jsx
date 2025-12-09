import { useState } from "react";
import { testOrder, placeOrder } from "../api/binanceOrders";

function BinanceOrderTester({ account }) {
  const [symbol, setSymbol] = useState("BTCUSDT");
  const [side, setSide] = useState("BUY");
  const [type, setType] = useState("MARKET");
  const [quoteQty, setQuoteQty] = useState(10);
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");
  const [loadingTest, setLoadingTest] = useState(false);
  const [loadingPlace, setLoadingPlace] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);

  const isConnected = account?.connected;
  const isTestnet = account?.testnet;
  const backendMode = account?.mode;
  const canTrade = account?.canTrade;

  const canOperate = !!(isConnected && canTrade);
  const warnMainnetSimulation =
    account && !isTestnet && backendMode !== "real";

  const buildPayload = () => {
    const payload = {
      symbol: symbol.toUpperCase().trim(),
      side,
      type,
    };

    const q = quantity ? Number(quantity) : null;
    const qq = quoteQty ? Number(quoteQty) : null;
    const p = price ? Number(price) : null;

    if (type === "MARKET") {
      // por padrão usamos quoteOrderQty (USDT)
      if (qq && !q) {
        payload.quoteOrderQty = qq;
      } else if (q && !qq) {
        payload.quantity = q;
      } else if (q && qq) {
        // deixa o backend reclamar se veio os dois
        payload.quantity = q;
        payload.quoteOrderQty = qq;
      }
    } else if (type === "LIMIT") {
      if (q) payload.quantity = q;
      if (p) payload.price = p;
    }

    if (type === "LIMIT" && !payload.price) {
      // prevenção básica no front
      throw new Error("Para ordens LIMIT é obrigatório informar o preço.");
    }

    return payload;
  };

  const handleTest = async () => {
    if (!canOperate) {
      setError("Conta não está apta a operar (connected/canTrade = false).");
      return;
    }

    try {
      setError(null);
      setLastResult(null);
      const payload = buildPayload();
      setLoadingTest(true);
      const data = await testOrder(payload);
      setLastResult({ kind: "test", data });
    } catch (err) {
      console.error(err);
      setError(err?.message || "Erro ao testar ordem.");
    } finally {
      setLoadingTest(false);
    }
  };

  const handlePlace = async () => {
    if (!canOperate) {
      setError("Conta não está apta a operar (connected/canTrade = false).");
      return;
    }

    if (
      !window.confirm(
        "ATENÇÃO: isto envia uma ORDEM REAL no ambiente configurado (testnet/mainnet). Confirmar envio?"
      )
    ) {
      return;
    }

    try {
      setError(null);
      setLastResult(null);
      const payload = buildPayload();
      setLoadingPlace(true);
      const data = await placeOrder(payload);
      setLastResult({ kind: "place", data });
    } catch (err) {
      console.error(err);
      setError(err?.message || "Erro ao enviar ordem.");
    } finally {
      setLoadingPlace(false);
    }
  };

  const renderEnvInfo = () => {
    if (!account) {
      return (
        <p style={{ fontSize: "0.8rem" }}>
          Conta ainda não carregada. Aguarde os dados da Binance.
        </p>
      );
    }

    return (
      <>
        <p style={{ fontSize: "0.8rem" }}>
          Ambiente Binance:{" "}
          <strong>{isTestnet ? "Testnet" : "Mainnet"}</strong> | Modo app:{" "}
          <strong>{backendMode}</strong> | Conectado:{" "}
          <strong>{isConnected ? "Sim" : "Não"}</strong> | Pode operar:{" "}
          <strong>{canTrade ? "Sim" : "Não"}</strong>
        </p>
        {warnMainnetSimulation && (
          <p
            style={{
              fontSize: "0.75rem",
              color: "#b91c1c",
              marginTop: "0.1rem",
            }}
          >
            Aviso: backend em <strong>mainnet</strong> com APP_MODE diferente
            de <strong>real</strong>. O envio de ordens reais será bloqueado
            pelo backend até você alterar a configuração conscientemente.
          </p>
        )}
      </>
    );
  };

  const renderLastResult = () => {
    if (!lastResult) return null;

    const { kind, data } = lastResult;

    const title =
      kind === "test" ? "Resultado do teste de ordem" : "Resultado da ordem enviada";

    return (
      <div
        style={{
          marginTop: "0.5rem",
          padding: "0.4rem",
          borderRadius: "0.35rem",
          backgroundColor: "#f9fafb",
          border: "1px solid #e5e7eb",
          fontSize: "0.75rem",
        }}
      >
        <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{title}</div>
        <div style={{ marginBottom: "0.25rem" }}>
          <div>
            Símbolo: <strong>{data.symbol}</strong>
          </div>
          <div>
            Lado: <strong>{data.side}</strong> | Tipo:{" "}
            <strong>{data.type}</strong>
          </div>
          <div>
            Qtd:{" "}
            <strong>
              {data.quantity != null ? data.quantity : "(não informado)"}
            </strong>{" "}
            | quoteOrderQty:{" "}
            <strong>
              {data.quoteOrderQty != null
                ? data.quoteOrderQty
                : "(não informado)"}
            </strong>
          </div>
          {data.price != null && (
            <div>
              Preço: <strong>{data.price}</strong>
            </div>
          )}
          {data.timeInForce && (
            <div>
              TimeInForce: <strong>{data.timeInForce}</strong>
            </div>
          )}
        </div>

        <details>
          <summary style={{ cursor: "pointer" }}>Ver resposta completa</summary>
          <pre
            style={{
              marginTop: "0.25rem",
              maxHeight: "200px",
              overflow: "auto",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {JSON.stringify(data.binance_response, null, 2)}
          </pre>
        </details>
      </div>
    );
  };

  const placeButtonLabel = () => {
    if (loadingPlace) {
      return isTestnet ? "Enviando (testnet)..." : "Enviando (mainnet)...";
    }
    return isTestnet
      ? "Enviar ordem (testnet)"
      : "Enviar ordem (mainnet - cuidado)";
  };

  return (
    <div>
      <h2>Teste de ordens na Binance</h2>

      {renderEnvInfo()}

      <p style={{ fontSize: "0.75rem", color: "#6b7280", marginBottom: "0.4rem" }}>
        Use este painel para testar parâmetros de ordens diretamente na Binance.
        Em testnet é seguro para testes. Em mainnet, tenha certeza do APP_MODE e
        dos valores antes de enviar.
      </p>

      {error && (
        <p className="error" style={{ fontSize: "0.8rem" }}>
          {error}
        </p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: "0.4rem",
          fontSize: "0.8rem",
        }}
      >
        <div>
          <label>
            Símbolo
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
            />
          </label>
        </div>

        <div>
          <label>
            Lado
            <select
              value={side}
              onChange={(e) => setSide(e.target.value)}
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </label>
        </div>

        <div>
          <label>
            Tipo
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
            >
              <option value="MARKET">MARKET</option>
              <option value="LIMIT">LIMIT</option>
            </select>
          </label>
        </div>

        {type === "MARKET" && (
          <>
            <div>
              <label>
                quoteOrderQty (USDT)
                <input
                  type="number"
                  step="0.00000001"
                  value={quoteQty}
                  onChange={(e) => setQuoteQty(e.target.value)}
                />
              </label>
            </div>
            <div>
              <label>
                Quantity (opcional)
                <input
                  type="number"
                  step="0.00000001"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />
              </label>
            </div>
          </>
        )}

        {type === "LIMIT" && (
          <>
            <div>
              <label>
                Quantity
                <input
                  type="number"
                  step="0.00000001"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />
              </label>
            </div>
            <div>
              <label>
                Preço
                <input
                  type="number"
                  step="0.00000001"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                />
              </label>
            </div>
          </>
        )}
      </div>

      <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.4rem" }}>
        <button
          className="btn btn-secondary"
          onClick={handleTest}
          disabled={loadingTest || !canOperate}
        >
          {loadingTest ? "Testando..." : "Testar na Binance"}
        </button>

        <button
          className="btn"
          style={{ backgroundColor: "#b91c1c", borderColor: "#b91c1c" }}
          onClick={handlePlace}
          disabled={loadingPlace || !canOperate}
        >
          {placeButtonLabel()}
        </button>
      </div>

      {renderLastResult()}
    </div>
  );
}

export default BinanceOrderTester;
