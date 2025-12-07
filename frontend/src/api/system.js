import { apiGet, apiPost } from "./client";

export function getSystemHealth() {
  return apiGet("/system/health");
}

export function getSystemState() {
  return apiGet("/system/state");
}

export function toggleSystemState() {
  return apiPost("/system/state/toggle");
}
