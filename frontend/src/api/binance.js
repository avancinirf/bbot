import { apiGet } from "./client";

export function getAccountSummary() {
  return apiGet("/binance/account/summary");
}
