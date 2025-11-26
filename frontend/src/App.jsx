// ==== BLOCK: APP_IMPORTS - START ====
import React, { useEffect, useState } from "react";
import ActiveBotPanel from "./components/ActiveBotPanel.jsx";
import ActiveBotAssets from "./components/ActiveBotAssets.jsx";
import ActiveBotMarketStatus from "./components/ActiveBotMarketStatus.jsx";
import ActiveBotOpportunity from "./components/ActiveBotOpportunity.jsx";
import ActiveBotLogs from "./components/ActiveBotLogs.jsx";
import BotsList from "./components/BotsList.jsx";
import FooterInfo from "./components/FooterInfo.jsx";
import BotForms from "./components/BotForms.jsx";
// ==== BLOCK: APP_IMPORTS - END ====



// ==== BLOCK: APP_COMPONENT - START ====
const App = () => {
  const [healthStatus, setHealthStatus] = useState("verificando...");
  const [healthError, setHealthError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const triggerRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("/api/health");
        if (!res.ok) throw new Error("Erro na resposta da API");
        const data = await res.json();
        setHealthStatus(data.status === "ok" ? "online" : "offline");
        setHealthError(null);
      } catch (err) {
        console.error("Erro ao verificar saúde da API:", err);
        setHealthStatus("offline");
        setHealthError("Não foi possível conectar ao backend.");
      }
    };

    checkHealth();
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "radial-gradient(circle at top, #0f172a 0, #020617 45%, #000 100%)",
        color: "#e5e7eb",
      }}
    >
      {/* ==== BLOCK: HEADER - START ==== */}
      <header
        style={{
          padding: "1rem 2rem",
          borderBottom: "1px solid rgba(148, 163, 184, 0.2)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 600 }}>
            Binance Trade Bot
          </h1>
          <p style={{ margin: 0, fontSize: "0.85rem", color: "#9ca3af" }}>
            Ambiente local · Testnet · Apenas trade (sem saques)
          </p>
        </div>
        <div style={{ textAlign: "right", fontSize: "0.85rem" }}>
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.25rem 0.6rem",
              borderRadius: "9999px",
              background:
                healthStatus === "online"
                  ? "rgba(22, 163, 74, 0.15)"
                  : "rgba(220, 38, 38, 0.15)",
              color: healthStatus === "online" ? "#22c55e" : "#f97373",
              border:
                healthStatus === "online"
                  ? "1px solid rgba(22, 163, 74, 0.4)"
                  : "1px solid rgba(220, 38, 38, 0.4)",
            }}
          >
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "9999px",
                backgroundColor:
                  healthStatus === "online" ? "#22c55e" : "#ef4444",
              }}
            />
            <span>Backend: {healthStatus}</span>
          </span>
          {healthError && (
            <div style={{ marginTop: "0.25rem", color: "#f97373" }}>
              {healthError}
            </div>
          )}
        </div>
      </header>
      {/* ==== BLOCK: HEADER - END ==== */}

      {/* ==== BLOCK: MAIN_LAYOUT - START ==== */}
      <main
        style={{
          padding: "1.5rem 2rem 2rem",
          display: "grid",
          gridTemplateColumns: "minmax(0, 2.2fr) minmax(0, 1.3fr)",
          gap: "1.5rem",
        }}
      >
        <section>
          <ActiveBotPanel refreshKey={refreshKey} />
          <ActiveBotAssets refreshKey={refreshKey} />
          <ActiveBotMarketStatus refreshKey={refreshKey} />
          <ActiveBotOpportunity refreshKey={refreshKey} />
          <ActiveBotLogs refreshKey={refreshKey} />
        </section>
        <aside>
          <BotsList onRefresh={triggerRefresh} refreshKey={refreshKey} />
          <BotForms onRefresh={triggerRefresh} />
        </aside>
      </main>
      {/* ==== BLOCK: MAIN_LAYOUT - END ==== */}

      {/* ==== BLOCK: MAIN_LAYOUT - END ==== */}

      {/* ==== BLOCK: FOOTER - START ==== */}
      <FooterInfo />
      {/* ==== BLOCK: FOOTER - END ==== */}
    </div>
  );
};

export default App;
// ==== BLOCK: APP_COMPONENT - END ====
