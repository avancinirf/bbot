import { apiGet } from "./client";

export function getStatsSummary() {
  return apiGet("/stats/summary");
}

export function getStatsByBot() {
  return apiGet("/stats/by_bot");
}
