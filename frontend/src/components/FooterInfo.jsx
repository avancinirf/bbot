// ==== BLOCK: FOOTER_INFO - START ====
import React from "react";

const FooterInfo = () => {
  return (
    <footer
      style={{
        padding: "0.75rem 2rem 1rem",
        borderTop: "1px solid rgba(148, 163, 184, 0.2)",
        fontSize: "0.8rem",
        color: "#9ca3af",
        backgroundColor: "#020617",
      }}
    >
      <div
        style={{
          maxWidth: "960px",
          margin: "0 auto",
          display: "flex",
          flexDirection: "column",
          gap: "0.35rem",
        }}
      >
        <div>
          <strong>Notas do sistema:</strong>
        </div>
        <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
          <li>
            Ambiente de{" "}
            <strong>testnet da Binance, apenas operações de trade</strong>, sem
            saques ou depósitos.
          </li>
          <li>
            Cada operação de trade utilizará, por padrão, o equivalente a{" "}
            <strong>10 USDT</strong>, ajustando para o valor mínimo permitido
            pela Binance quando necessário.
          </li>
          <li>
            No futuro, cada bot poderá ter um valor de trade próprio e
            independente.
          </li>
          <li>
            Indicadores de mercado (RSI, EMAs, etc.) serão exibidos aqui com
            resumo da avaliação de compra/venda assim que forem implementados.
          </li>
        </ul>
      </div>
    </footer>
  );
};

export default FooterInfo;
// ==== BLOCK: FOOTER_INFO - END ====
