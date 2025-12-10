import { useEffect, useState } from "react";
import { getStatsSummary } from "../api/stats";

function StatsSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getStatsSummary();
        setSummary(data);
      } catch (err) {
        console.error(err);
        setError("Erro ao carregar resumo dos bots.");
      } finally {
        setLoading(false);
      }
    };

    loadSummary();
  }, []);

  const handleExportTrades = async () => {
    try {
      setExporting(true);
      const baseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/trades/export?limit=1000`);

      if (!res.ok) {
        throw new Error("Falha ao exportar trades.");
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "trades_export.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("Erro ao exportar trades.");
    } finally {
      setExporting(false);
    }
  };

  if (loading && !summary) {
    return (
      <div className="text-sm text-slate-500 mb-2">
        Carregando resumo dos bots...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-sm text-red-600 mb-2">
        {error}
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="text-sm text-slate-500 mb-2">
        Resumo dos bots indisponível.
      </div>
    );
  }

  return (
    <div
      className="bg-white"
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "0.6rem",
        padding: "0.75rem",
        marginBottom: "0.85rem",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.06)",
      }}
    >
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-semibold text-sm">
          Resumo dos bots (virtual)
        </h2>
        <button
          type="button"
          className="px-2 py-1 text-xs rounded border border-slate-300 hover:bg-slate-50"
          onClick={handleExportTrades}
          disabled={exporting}
        >
          {exporting ? "Exportando..." : "Exportar trades (CSV)"}
        </button>
      </div>

      <div className="grid grid-cols-3 gap-x-4 gap-y-1 text-xs">
        <div>
          <div>Total de bots:</div>
          <div className="font-mono">
            {summary.total_bots}
          </div>
        </div>
        <div>
          <div>Bots online:</div>
          <div className="font-mono">
            {summary.total_bots_online}
          </div>
        </div>
        <div>
          <div>Bots bloqueados:</div>
          <div className="font-mono">
            {summary.total_bots_blocked}
          </div>
        </div>
        <div>
          <div>Bots com posição aberta:</div>
          <div className="font-mono">
            {summary.total_bots_with_open_position}
          </div>
        </div>
        <div>
          <div>Saldo virtual livre total (USDT):</div>
          <div className="font-mono">
            {Number(summary.total_saldo_usdt_livre || 0).toFixed(6)}
          </div>
        </div>
        <div>
          <div>P/L realizado total (USDT):</div>
          <div className="font-mono">
            {Number(summary.total_realized_pnl || 0).toFixed(6)}
          </div>
        </div>
        <div>
          <div>Taxas totais (USDT):</div>
          <div className="font-mono">
            {Number(summary.total_fees_usdt || 0).toFixed(6)}
          </div>
        </div>
        <div className="col-span-2">
          <div>Gerado em:</div>
          <div className="font-mono">
            {summary.generated_at
              ? new Date(summary.generated_at).toLocaleString()
              : "-"}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatsSummary;
