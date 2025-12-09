import { apiGet } from "./client";

export function getRecentTrades({ limit = 50, botId, symbol } = {}) {
  const params = new URLSearchParams();

  if (limit) params.set("limit", String(limit));
  if (botId != null && botId !== "") params.set("bot_id", String(botId));
  if (symbol) params.set("symbol", symbol.toUpperCase().trim());

  const qs = params.toString();
  const path = qs ? `/trades/recent?${qs}` : "/trades/recent";

  return apiGet(path);
}
