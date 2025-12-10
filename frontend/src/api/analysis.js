// frontend/src/api/analysis.js
import { apiGet } from "./client";

export function getBotAnalysis(botId) {
  return apiGet(`/analysis/bot/${botId}`);
}
