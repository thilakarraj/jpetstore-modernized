import { apiClient } from "@/services/api/client";
import {
  mapOrderDetail,
  mapOrderSummary,
  type BackendOrderDetail,
  type BackendOrderSummary,
} from "@/services/api/mappers";
import type { AccountProfile, CheckoutPayload, Order } from "@/types/api";

export interface CheckoutApiPayload {
  ship_to_first_name: string;
  ship_to_last_name: string;
  ship_address1: string;
  ship_address2?: string | null;
  ship_city: string;
  ship_state: string;
  ship_zip: string;
  ship_country: string;
  bill_to_first_name: string;
  bill_to_last_name: string;
  bill_address1: string;
  bill_address2?: string | null;
  bill_city: string;
  bill_state: string;
  bill_zip: string;
  bill_country: string;
  courier: string;
  locale: string;
  card_type: "Visa" | "MasterCard" | "American Express";
  card_last_four: string;
  expiry_date: string;
}

export function buildCheckoutPayload(
  user: AccountProfile,
  shipping: CheckoutPayload,
  payment?: { card_type?: CheckoutApiPayload["card_type"]; card_last_four?: string; expiry_date?: string },
): CheckoutApiPayload {
  const billAddr1 = shipping.bill_addr1 ?? shipping.ship_addr1;
  const billCity = shipping.bill_city ?? shipping.ship_city;
  const billState = shipping.bill_state ?? shipping.ship_state;
  const billZip = shipping.bill_zip ?? shipping.ship_zip;
  const billCountry = shipping.bill_country ?? shipping.ship_country;
  return {
    ship_to_first_name: user.first_name,
    ship_to_last_name: user.last_name,
    ship_address1: shipping.ship_addr1,
    ship_address2: shipping.ship_addr2 ?? null,
    ship_city: shipping.ship_city,
    ship_state: shipping.ship_state,
    ship_zip: shipping.ship_zip,
    ship_country: shipping.ship_country,
    bill_to_first_name: user.first_name,
    bill_to_last_name: user.last_name,
    bill_address1: billAddr1,
    bill_address2: shipping.ship_addr2 ?? null,
    bill_city: billCity,
    bill_state: billState,
    bill_zip: billZip,
    bill_country: billCountry,
    courier: "UPS",
    locale: user.language_preference === "japanese" ? "ja_JP" : "en_US",
    card_type: payment?.card_type ?? "Visa",
    card_last_four: payment?.card_last_four ?? "9999",
    expiry_date: payment?.expiry_date ?? "12/30",
  };
}

export async function checkoutOrder(
  user: AccountProfile,
  shipping: CheckoutPayload,
  idempotencyKey: string,
): Promise<Order> {
  const body = buildCheckoutPayload(user, shipping);
  const { data } = await apiClient.post<{ order: BackendOrderDetail }>(
    "/api/v1/orders/checkout",
    body,
    { headers: { "Idempotency-Key": idempotencyKey } },
  );
  return mapOrderDetail(data.order);
}

export async function fetchOrders(): Promise<Order[]> {
  const { data } = await apiClient.get<{ orders: BackendOrderSummary[] }>("/api/v1/orders");
  return data.orders.map(mapOrderSummary);
}

export async function fetchOrder(orderId: number): Promise<Order> {
  const { data } = await apiClient.get<BackendOrderDetail>(`/api/v1/orders/${orderId}`);
  return mapOrderDetail(data);
}
