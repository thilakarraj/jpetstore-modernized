import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number | string): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number.isFinite(num) ? num : 0);
}

export function slugify(value: string): string {
  return value.toLowerCase().replace(/\s+/g, "-");
}

export const STORAGE_KEYS = {
  theme: "jpetstore-theme",
  cartId: "jpetstore-cart-id",
  recentProducts: "jpetstore-recent-products",
  accessToken: "jpetstore-access-token",
} as const;
