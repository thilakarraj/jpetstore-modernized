import type { Cart, CartLine, Item, Order, OrderLine, OrderStatus, Product } from "@/types/api";
import { getProductImage } from "@/services/mocks/catalogFixtures";

export interface BackendCartLine {
  item_id: string;
  product_id?: string | null;
  product_name?: string | null;
  quantity: number;
  list_price?: number | string | null;
  line_total?: number | string | null;
  in_stock?: boolean;
}

export interface BackendCartResponse {
  cart_id: number;
  lines: BackendCartLine[];
  sub_total: number | string;
}

export interface BackendOrderLine {
  line_number: number;
  item_id: string;
  quantity: number;
  unit_price: number | string;
  line_total: number | string;
}

export interface BackendOrderSummary {
  order_id: number;
  order_date: string;
  total_price: number | string;
  status: string;
}

export interface BackendOrderDetail extends BackendOrderSummary {
  ship_address1: string;
  ship_address2?: string | null;
  ship_city: string;
  ship_state: string;
  ship_zip: string;
  ship_country: string;
  lines: BackendOrderLine[];
}

function money(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "0.00";
  const num = typeof value === "string" ? parseFloat(value) : value;
  return Number.isFinite(num) ? num.toFixed(2) : "0.00";
}

export function mapCartResponse(data: BackendCartResponse): Cart {
  const lines: CartLine[] = data.lines.map((line) => ({
    item_id: line.item_id,
    quantity: line.quantity,
    unit_price: money(line.list_price),
    product_name: line.product_name ?? line.item_id,
    attribute1: null,
    image_url: undefined,
  }));
  const item_count = lines.reduce((sum, line) => sum + line.quantity, 0);
  return {
    cart_id: String(data.cart_id),
    lines,
    subtotal: money(data.sub_total),
    item_count,
  };
}

export function mapOrderDetail(data: BackendOrderDetail): Order {
  const lines: OrderLine[] = data.lines.map((line) => ({
    item_id: line.item_id,
    quantity: line.quantity,
    unit_price: money(line.unit_price),
    product_name: line.item_id,
  }));
  return {
    order_id: data.order_id,
    order_date: data.order_date,
    status: data.status as OrderStatus,
    total: money(data.total_price),
    lines,
    ship_addr1: data.ship_address1,
    ship_city: data.ship_city,
    ship_state: data.ship_state,
    ship_zip: data.ship_zip,
    ship_country: data.ship_country,
  };
}

export function mapOrderSummary(data: BackendOrderSummary): Order {
  return {
    order_id: data.order_id,
    order_date: data.order_date,
    status: data.status as OrderStatus,
    total: money(data.total_price),
    lines: [],
  };
}

export function mapProductSummary(product: Product): Product {
  return {
    ...product,
    description: product.description ?? "",
    image_url: product.image_url ?? getProductImage(product),
  };
}

export function mapItemSummary(
  productId: string,
  item: Omit<Item, "product_id"> & { list_price?: number | string | null },
): Item {
  return {
    item_id: item.item_id,
    product_id: productId,
    list_price: money(item.list_price),
    status: item.status ?? "P",
    attribute1: item.attribute1 ?? null,
    attribute2: item.attribute2 ?? null,
    in_stock: item.in_stock ?? false,
    quantity: item.quantity,
  };
}
