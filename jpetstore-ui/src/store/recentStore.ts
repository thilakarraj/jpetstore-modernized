import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Product } from "@/types/api";
import { STORAGE_KEYS } from "@/utils/cn";

const MAX_RECENT = 8;

interface RecentState {
  products: Product[];
  addRecent: (product: Product) => void;
}

export const useRecentStore = create<RecentState>()(
  persist(
    (set) => ({
      products: [],
      addRecent: (product) =>
        set((state) => {
          const filtered = state.products.filter((p) => p.product_id !== product.product_id);
          return { products: [product, ...filtered].slice(0, MAX_RECENT) };
        }),
    }),
    { name: STORAGE_KEYS.recentProducts },
  ),
);
