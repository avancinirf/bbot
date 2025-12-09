import { apiGet } from "./client";

export function getLatestIndicator(symbol) {
  if (!symbol) {
    throw new Error("Símbolo é obrigatório para buscar indicadores.");
  }

  return apiGet(`/indicators/latest/${symbol.toUpperCase()}`);
}
