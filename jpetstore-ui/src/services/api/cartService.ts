import { apiClient } from "@/services/api/client";
import { mapCartResponse, type BackendCartResponse } from "@/services/api/mappers";
import type { Cart } from "@/types/api";

export async function fetchCart(): Promise<Cart> {
  const { data } = await apiClient.get<BackendCartResponse>("/api/v1/cart");
  return mapCartResponse(data);
}

export async function addCartItem(itemId: string, quantity = 1): Promise<Cart> {
  const { data } = await apiClient.post<BackendCartResponse>("/api/v1/cart/items", {
    item_id: itemId,
    quantity,
  });
  return mapCartResponse(data);
}

export async function updateCartItem(itemId: string, quantity: number): Promise<Cart> {
  const { data } = await apiClient.put<BackendCartResponse>(
    `/api/v1/cart/items/${encodeURIComponent(itemId)}`,
    { quantity },
  );
  return mapCartResponse(data);
}

export async function removeCartItem(itemId: string): Promise<Cart> {
  const { data } = await apiClient.delete<BackendCartResponse>(
    `/api/v1/cart/items/${encodeURIComponent(itemId)}`,
  );
  return mapCartResponse(data);
}

export async function clearCartApi(): Promise<Cart> {
  const { data } = await apiClient.delete<BackendCartResponse>("/api/v1/cart");
  return mapCartResponse(data);
}
