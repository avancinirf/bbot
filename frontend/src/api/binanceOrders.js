import { apiPost } from "./client";

export function testOrder(payload) {
  return apiPost("/binance/order/test", payload);
}

export function placeOrder(payload) {
  return apiPost("/binance/order/place", payload);
}
