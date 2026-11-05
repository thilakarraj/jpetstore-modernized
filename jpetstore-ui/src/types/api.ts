export interface Category {
  category_id: string;
  name: string;
  description: string;
}

export interface Product {
  product_id: string;
  category_id: string;
  name: string;
  description: string;
  image_url?: string;
}

export interface Item {
  item_id: string;
  product_id: string;
  list_price: string;
  unit_cost?: string;
  supplier_id?: number;
  status: string;
  attribute1?: string | null;
  attribute2?: string | null;
  in_stock: boolean;
  quantity?: number;
  product?: Product;
}

export interface CartLine {
  item_id: string;
  quantity: number;
  unit_price: string;
  product_name: string;
  attribute1?: string | null;
  image_url?: string;
}

export interface Cart {
  cart_id: string;
  lines: CartLine[];
  subtotal: string;
  item_count: number;
}

export interface OrderLine {
  item_id: string;
  quantity: number;
  unit_price: string;
  product_name: string;
}

export type OrderStatus = "P" | "S" | "C";

export interface Order {
  order_id: number;
  order_date: string;
  status: OrderStatus;
  total: string;
  lines: OrderLine[];
  ship_addr1?: string;
  ship_city?: string;
  ship_state?: string;
  ship_zip?: string;
  ship_country?: string;
}

export interface AccountProfile {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  address1: string;
  address2?: string | null;
  city: string;
  state: string;
  zip: string;
  country: string;
  phone: string;
  language_preference: "english" | "japanese";
  favourite_category_id: string;
  list_option?: boolean;
  banner_option?: boolean;
  banner_name?: string | null;
}

export interface AuthLoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiErrorBody {
  error?: {
    code: string;
    message: string;
  };
  request_id?: string;
}

export interface RegisterPayload {
  username: string;
  password: string;
  email: string;
  first_name: string;
  last_name: string;
  address1: string;
  address2?: string | null;
  city: string;
  state: string;
  zip: string;
  country: string;
  phone: string;
  language_preference: "english" | "japanese";
  favourite_category_id: string;
  list_option: boolean;
  banner_option: boolean;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface CheckoutPayload {
  ship_addr1: string;
  ship_addr2?: string;
  ship_city: string;
  ship_state: string;
  ship_zip: string;
  ship_country: string;
  bill_addr1?: string;
  bill_city?: string;
  bill_state?: string;
  bill_zip?: string;
  bill_country?: string;
}
