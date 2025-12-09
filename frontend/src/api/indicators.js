import { apiGet } from "./client";

export function getLatestIndicator(symbol) {
  // backend já expõe /indicators/latest/{symbol}
  return apiGet(`/indicators/latest/${symbol}`);
}
