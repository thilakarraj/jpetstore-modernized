import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Minus, Plus } from "lucide-react";
import { CatalogStatus } from "@/components/catalog/CatalogStatus";
import { StoreProductCard } from "@/components/product/StoreProductCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  enrichProduct,
  fetchAllProducts,
  fetchProduct,
  fetchProductItems,
  getApiErrorMessage,
} from "@/services/api/catalogService";
import type { Item, Product } from "@/types/api";
import { useCartStore } from "@/store/cartStore";
import { useRecentStore } from "@/store/recentStore";
import { formatCurrency } from "@/utils/cn";

export function ProductDetailPage({ productId }: { productId: string }) {
  const [product, setProduct] = useState<Product | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [selectedItemId, setSelectedItemId] = useState<string>("");
  const [quantity, setQuantity] = useState(1);
  const [related, setRelated] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const addItem = useCartStore((s) => s.addItem);
  const addRecent = useRecentStore((s) => s.addRecent);

  const selectedItem = useMemo(
    () => items.find((i) => i.item_id === selectedItemId) ?? items[0],
    [items, selectedItemId],
  );

  const loadProduct = useCallback(
    async (signal: AbortSignal) => {
      setLoading(true);
      setError(null);
      try {
        const [p, itemList, all] = await Promise.all([
          fetchProduct(productId),
          fetchProductItems(productId),
          fetchAllProducts(),
        ]);
        if (signal.aborted) return;
        const enriched = enrichProduct(p);
        setProduct(enriched);
        setItems(itemList);
        const firstInStock = itemList.find((i) => i.in_stock) ?? itemList[0];
        if (firstInStock) setSelectedItemId(firstInStock.item_id);
        addRecent(enriched);
        setRelated(
          all
            .filter((x) => x.category_id === p.category_id && x.product_id !== p.product_id)
            .slice(0, 4)
            .map(enrichProduct),
        );
      } catch (e) {
        if (signal.aborted) return;
        setProduct(null);
        setItems([]);
        setError(getApiErrorMessage(e));
      } finally {
        if (!signal.aborted) setLoading(false);
      }
    },
    [productId, addRecent],
  );

  useEffect(() => {
    const controller = new AbortController();
    void loadProduct(controller.signal);
    return () => controller.abort();
  }, [loadProduct]);

  if (loading || error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <CatalogStatus
          loading={loading}
          error={error}
          onRetry={() => {
            const controller = new AbortController();
            void loadProduct(controller.signal);
          }}
        />
      </div>
    );
  }

  if (!product) {
    return null;
  }

  const inStock = selectedItem?.in_stock ?? false;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="grid gap-10 lg:grid-cols-2">
        <motion.div
          className="overflow-hidden rounded-2xl border border-border bg-surface shadow-card"
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.3 }}
        >
          <img
            src={product.image_url}
            alt={product.name}
            className="aspect-square w-full object-cover"
          />
        </motion.div>

        <div>
          <p className="text-sm uppercase tracking-widest text-muted-foreground">
            {product.category_id} · {product.product_id}
          </p>
          <h1 className="mt-2 font-display text-4xl">{product.name}</h1>
          <p className="mt-4 text-muted-foreground">{product.description}</p>

          <div className="mt-6 flex items-center gap-3">
            <span className="text-3xl font-semibold">
              {selectedItem ? formatCurrency(selectedItem.list_price) : "—"}
            </span>
            <Badge tone={inStock ? "success" : "warning"}>
              {inStock ? "In stock" : "Out of stock"}
            </Badge>
          </div>

          {items.length > 1 ? (
            <div className="mt-6 space-y-2">
              <p className="text-sm font-medium">Item (SKU)</p>
              <div className="flex flex-wrap gap-2">
                {items.map((item) => (
                  <button
                    key={item.item_id}
                    type="button"
                    className={`cursor-pointer rounded-lg border px-3 py-2 text-sm transition-colors ${
                      selectedItem?.item_id === item.item_id
                        ? "border-accent bg-accent/10 text-foreground"
                        : "border-border text-muted-foreground hover:border-accent/50"
                    }`}
                    onClick={() => setSelectedItemId(item.item_id)}
                  >
                    {item.item_id}
                    {item.attribute1 ? ` · ${item.attribute1}` : ""}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <div className="mt-6 flex items-center gap-3">
            <span className="text-sm font-medium">Quantity</span>
            <div className="flex items-center rounded-lg border border-border">
              <button
                type="button"
                className="cursor-pointer p-2"
                onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                aria-label="Decrease quantity"
              >
                <Minus className="h-4 w-4" />
              </button>
              <span className="min-w-10 text-center text-sm">{quantity}</span>
              <button
                type="button"
                className="cursor-pointer p-2"
                onClick={() => setQuantity((q) => q + 1)}
                aria-label="Increase quantity"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Button
              disabled={!selectedItem || !inStock}
              onClick={() => selectedItem && void addItem(selectedItem.item_id, quantity)}
            >
              Add to cart
            </Button>
            <Link to="/cart">
              <Button variant="outline">View cart</Button>
            </Link>
          </div>
        </div>
      </div>

      {related.length > 0 ? (
        <section className="mt-16 border-t border-border pt-12">
          <h2 className="font-display text-3xl">Related products</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {related.map((p) => (
              <StoreProductCard key={p.product_id} product={p} />
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
