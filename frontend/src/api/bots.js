import { apiGet, apiPost, apiDelete } from "./client";

export function listBots() {
  return apiGet("/bots/");
}

export function createBot(botData) {
  return apiPost("/bots/", botData);
}

export function startBot(id) {
  return apiPost(`/bots/${id}/start`);
}

export function stopBot(id) {
  return apiPost(`/bots/${id}/stop`);
}

export function blockBot(id) {
  return apiPost(`/bots/${id}/block`);
}

export function unblockBot(id) {
  return apiPost(`/bots/${id}/unblock`);
}

export function deleteBot(id) {
  return apiDelete(`/bots/${id}`);
}

export function startAllBots() {
  return apiPost("/bots/actions/start_all");
}

export function stopAllBots() {
  return apiPost("/bots/actions/stop_all");
}

export function getBotTrades(id) {
  return apiGet(`/bots/${id}/trades`);
}

export function closeBotPosition(id) {
  return apiPost(`/bots/${id}/close_position`);
}
