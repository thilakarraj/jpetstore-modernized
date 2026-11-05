import { apiClient, useMockApi } from "@/services/api/client";
import { mapItemSummary } from "@/services/api/mappers";
import {
  getItemsForProduct,
  getProductById,
  getProductImage,
  mockCategories,
  mockProducts,
  mockItems,
} from "@/services/mocks/catalogFixtures";
import type { Category, Item, Product } from "@/types/api";

export async function fetchCategories(): Promise<Category[]> {
  if (useMockApi) {
    await delay(200);
    return mockCategories;
  }
  const { data } = await apiClient.get<{ categories: Category[] }>(
    "/api/v1/catalog/categories",
  );
  return data.categories;
}

export async function fetchCategory(categoryId: string): Promise<Category> {
  if (useMockApi) {
    await delay(150);
    const cat = mockCategories.find((c) => c.category_id === categoryId);
    if (!cat) throw new Error("Category not found");
    return cat;
  }
  const { data } = await apiClient.get<Category>(
    `/api/v1/catalog/categories/${categoryId}`,
  );
  return data;
}

export async function fetchProductsByCategory(categoryId: string): Promise<Product[]> {
  if (useMockApi) {
    await delay(250);
    return mockProducts.filter((p) => p.category_id === categoryId);
  }
  const { data } = await apiClient.get<{ products: Product[] }>(
    `/api/v1/catalog/categories/${categoryId}/products`,
  );
  return data.products;
}

export async function fetchAllProducts(): Promise<Product[]> {
  if (useMockApi) {
    await delay(200);
    return mockProducts;
  }
  const categories = await fetchCategories();
  const lists = await Promise.all(
    categories.map((c) => fetchProductsByCategory(c.category_id)),
  );
  const map = new Map<string, Product>();
  lists.flat().forEach((p) => map.set(p.product_id, p));
  return [...map.values()];
}

export async function fetchProduct(productId: string): Promise<Product> {
  if (useMockApi) {
    await delay(180);
    const product = getProductById(productId);
    if (!product) throw new Error("Product not found");
    return product;
  }
  const { data } = await apiClient.get<Product>(
    `/api/v1/catalog/products/${productId}`,
  );
  return data;
}

export async function fetchProductItems(productId: string): Promise<Item[]> {
  if (useMockApi) {
    await delay(180);
    return getItemsForProduct(productId);
  }
  const { data } = await apiClient.get<{ items: Array<Omit<Item, "product_id">> }>(
    `/api/v1/catalog/products/${productId}/items`,
  );
  return data.items.map((item) => mapItemSummary(productId, item));
}

export async function searchProducts(keyword: string): Promise<Product[]> {
  const trimmed = keyword.trim();
  if (!trimmed) {
    throw new Error(
      "Please enter a keyword to search for, then press the search button.",
    );
  }
  if (useMockApi) {
    await delay(220);
    const lower = trimmed.toLowerCase();
    return mockProducts.filter(
      (p) =>
        p.name.toLowerCase().includes(lower) ||
        p.description.toLowerCase().includes(lower) ||
        p.product_id.toLowerCase().includes(lower),
    );
  }
  const { data } = await apiClient.get<{ products: Product[] }>(
    "/api/v1/catalog/products/search",
    { params: { keyword: trimmed } },
  );
  return data.products;
}

export async function fetchItem(itemId: string): Promise<Item> {
  if (useMockApi) {
    await delay(150);
    const item = mockItems.find((i) => i.item_id === itemId);
    if (!item) throw new Error("Item not found");
    const product = getProductById(item.product_id);
    return { ...item, product, quantity: item.quantity };
  }
  const { data } = await apiClient.get<Item>(`/api/v1/catalog/items/${itemId}`);
  return data;
}

export function enrichProduct(product: Product): Product {
  return {
    ...product,
    image_url: product.image_url ?? getProductImage(product),
  };
}

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function getLowestPrice(productId: string): number | null {
  const items = getItemsForProduct(productId);
  if (!items.length) return null;
  return Math.min(...items.map((i) => parseFloat(i.list_price)));
}
