import { apiGet } from "./client";

export function getStatsSummary() {
  return apiGet("/stats/summary");
}
