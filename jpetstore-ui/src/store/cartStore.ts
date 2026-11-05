import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  addCartItem,
  clearCartApi,
  fetchCart,
  removeCartItem,
  updateCartItem,
} from "@/services/api/cartService";
import { useMockApi } from "@/services/api/client";
import { checkoutOrder, fetchOrder, fetchOrders } from "@/services/api/orderService";
import {
  getProductById,
  getProductImage,
  mockItems,
  mockOrders,
  nextMockOrderId,
} from "@/services/mocks/catalogFixtures";
import type { AccountProfile, Cart, CartLine, CheckoutPayload, Order } from "@/types/api";
import { STORAGE_KEYS } from "@/utils/cn";

function computeSubtotal(lines: CartLine[]): string {
  const total = lines.reduce(
    (sum, line) => sum + parseFloat(line.unit_price) * line.quantity,
    0,
  );
  return total.toFixed(2);
}

function emptyCart(): Cart {
  return {
    cart_id: "0",
    lines: [],
    subtotal: "0.00",
    item_count: 0,
  };
}

function ensureCartId(): string {
  let id = localStorage.getItem(STORAGE_KEYS.cartId);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.cartId, id);
  }
  return id;
}

function buildLine(itemId: string, quantity: number): CartLine | null {
  const item = mockItems.find((i) => i.item_id === itemId);
  if (!item) return null;
  const product = getProductById(item.product_id);
  if (!product) return null;
  return {
    item_id: itemId,
    quantity,
    unit_price: item.list_price,
    product_name: product.name,
    attribute1: item.attribute1,
    image_url: getProductImage(product),
  };
}

interface CartState {
  cart: Cart;
  orders: Order[];
  cartBump: boolean;
  cartError: string | null;
  ordersLoading: boolean;
  refreshCart: () => Promise<void>;
  loadOrders: () => Promise<void>;
  loadOrderDetail: (orderId: number) => Promise<Order | null>;
  addItem: (itemId: string, quantity?: number) => Promise<void>;
  updateQuantity: (itemId: string, quantity: number) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  clearCart: () => Promise<void>;
  placeOrder: (payload: CheckoutPayload, user: AccountProfile) => Promise<Order>;
  triggerCartBump: () => void;
  clearCartError: () => void;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      cart: useMockApi
        ? {
            cart_id: ensureCartId(),
            lines: [],
            subtotal: "0.00",
            item_count: 0,
          }
        : emptyCart(),
      orders: mockOrders,
      cartBump: false,
      cartError: null,
      ordersLoading: false,
      clearCartError: () => set({ cartError: null }),
      triggerCartBump: () => {
        set({ cartBump: true });
        setTimeout(() => set({ cartBump: false }), 400);
      },
      refreshCart: async () => {
        if (useMockApi) return;
        try {
          const cart = await fetchCart();
          set({ cart, cartError: null });
        } catch (e) {
          set({ cartError: e instanceof Error ? e.message : "Failed to load cart" });
        }
      },
      loadOrders: async () => {
        if (useMockApi) return;
        set({ ordersLoading: true });
        try {
          const orders = await fetchOrders();
          set({ orders, ordersLoading: false });
        } catch (e) {
          set({
            ordersLoading: false,
            cartError: e instanceof Error ? e.message : "Failed to load orders",
          });
        }
      },
      loadOrderDetail: async (orderId: number) => {
        const cached = get().orders.find((o) => o.order_id === orderId);
        if (cached?.lines.length) return cached;
        if (useMockApi) return cached ?? null;
        try {
          const order = await fetchOrder(orderId);
          set((state) => ({
            orders: [order, ...state.orders.filter((o) => o.order_id !== orderId)],
          }));
          return order;
        } catch {
          return null;
        }
      },
      addItem: async (itemId, quantity = 1) => {
        if (useMockApi) {
          set((state) => {
            const lines = [...state.cart.lines];
            const existing = lines.find((l) => l.item_id === itemId);
            if (existing) {
              existing.quantity += quantity;
            } else {
              const line = buildLine(itemId, quantity);
              if (line) lines.push(line);
            }
            const item_count = lines.reduce((n, l) => n + l.quantity, 0);
            return {
              cart: {
                cart_id: ensureCartId(),
                lines,
                subtotal: computeSubtotal(lines),
                item_count,
              },
            };
          });
          get().triggerCartBump();
          return;
        }
        try {
          const cart = await addCartItem(itemId, quantity);
          set({ cart, cartError: null });
          get().triggerCartBump();
        } catch (e) {
          const message = e instanceof Error ? e.message : "Could not add item";
          set({ cartError: message });
          throw e;
        }
      },
      updateQuantity: async (itemId, quantity) => {
        if (useMockApi) {
          set((state) => {
            let lines = state.cart.lines.map((l) =>
              l.item_id === itemId ? { ...l, quantity: Math.max(1, quantity) } : l,
            );
            if (quantity < 1) {
              lines = lines.filter((l) => l.item_id !== itemId);
            }
            const item_count = lines.reduce((n, l) => n + l.quantity, 0);
            return {
              cart: {
                ...state.cart,
                lines,
                subtotal: computeSubtotal(lines),
                item_count,
              },
            };
          });
          return;
        }
        try {
          const cart =
            quantity < 1
              ? await removeCartItem(itemId)
              : await updateCartItem(itemId, quantity);
          set({ cart, cartError: null });
        } catch (e) {
          set({ cartError: e instanceof Error ? e.message : "Could not update cart" });
          throw e;
        }
      },
      removeItem: async (itemId) => {
        if (useMockApi) {
          set((state) => {
            const lines = state.cart.lines.filter((l) => l.item_id !== itemId);
            const item_count = lines.reduce((n, l) => n + l.quantity, 0);
            return {
              cart: {
                ...state.cart,
                lines,
                subtotal: computeSubtotal(lines),
                item_count,
              },
            };
          });
          return;
        }
        const cart = await removeCartItem(itemId);
        set({ cart, cartError: null });
      },
      clearCart: async () => {
        if (useMockApi) {
          set({
            cart: {
              cart_id: ensureCartId(),
              lines: [],
              subtotal: "0.00",
              item_count: 0,
            },
          });
          return;
        }
        const cart = await clearCartApi();
        set({ cart });
      },
      placeOrder: async (payload, user) => {
        if (useMockApi) {
          const { cart } = get();
          const order: Order = {
            order_id: nextMockOrderId(),
            order_date: new Date().toISOString(),
            status: "P",
            total: cart.subtotal,
            lines: cart.lines.map((l) => ({
              item_id: l.item_id,
              quantity: l.quantity,
              unit_price: l.unit_price,
              product_name: l.product_name,
            })),
            ship_addr1: payload.ship_addr1,
            ship_city: payload.ship_city,
            ship_state: payload.ship_state,
            ship_zip: payload.ship_zip,
            ship_country: payload.ship_country,
          };
          mockOrders.unshift(order);
          set((state) => ({
            orders: [order, ...state.orders.filter((o) => o.order_id !== order.order_id)],
          }));
          await get().clearCart();
          return order;
        }
        const order = await checkoutOrder(user, payload, crypto.randomUUID());
        await get().refreshCart();
        set((state) => ({
          orders: [order, ...state.orders.filter((o) => o.order_id !== order.order_id)],
        }));
        return order;
      },
    }),
    {
      name: "jpetstore-cart",
      partialize: (state) =>
        useMockApi
          ? { cart: state.cart, orders: state.orders }
          : { orders: state.orders },
    },
  ),
);
