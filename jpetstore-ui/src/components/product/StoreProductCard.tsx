/**
 * Adapted from 21st.dev Product Card (beratberkayg/product-card-1).
 * Simplified for JPetStore catalog items; uses semantic theme tokens only.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Check, Loader2, ShoppingCart } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { useCartStore } from "@/store/cartStore";
import type { Item, Product } from "@/types/api";
import { cn, formatCurrency } from "@/utils/cn";
import {
  fetchProductItems,
  getDefaultInStockItem,
  getLowestPrice,
  getLowestPriceFromItems,
} from "@/services/api/catalogService";
import { useMockApi } from "@/services/api/client";
import { getItemsForProduct } from "@/services/mocks/catalogFixtures";

export interface StoreProductCardProps {
  product: Product;
  badge?: "new" | "featured";
  className?: string;
  onAdd?: () => void;
}

export function StoreProductCard({
  product,
  badge,
  className,
  onAdd,
}: StoreProductCardProps) {
  const addItem = useCartStore((s) => s.addItem);
  const [loading, setLoading] = useState(false);
  const [added, setAdded] = useState(false);
  const [items, setItems] = useState<Item[]>(() =>
    useMockApi ? getItemsForProduct(product.product_id) : [],
  );

  useEffect(() => {
    if (useMockApi) {
      setItems(getItemsForProduct(product.product_id));
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        const liveItems = await fetchProductItems(product.product_id);
        if (!cancelled) setItems(liveItems);
      } catch {
        if (!cancelled) setItems([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [product.product_id]);

  const price = useMockApi
    ? getLowestPrice(product.product_id)
    : getLowestPriceFromItems(items);
  const defaultItem = getDefaultInStockItem(items);

  const handleAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!defaultItem || added) return;
    setLoading(true);
    try {
      let itemId = defaultItem.item_id;
      if (!useMockApi && items.length === 0) {
        const liveItems = await fetchProductItems(product.product_id);
        itemId = getDefaultInStockItem(liveItems)?.item_id ?? itemId;
      }
      if (!itemId) return;
      await addItem(itemId, 1);
      onAdd?.();
      setAdded(true);
      window.setTimeout(() => setAdded(false), 1800);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.article
      layout
      className={cn("group h-full", className)}
      whileHover={{ y: -4 }}
      transition={{ duration: 0.25 }}
    >
      <Card className="flex h-full flex-col overflow-hidden bg-surface hover:shadow-elevated">
        <Link
          to={`/catalog/products/${product.product_id}`}
          className="relative block aspect-[4/5] overflow-hidden"
        >
          <motion.img
            src={product.image_url}
            alt={product.name}
            className="h-full w-full object-cover"
            whileHover={{ scale: 1.04 }}
            transition={{ duration: 0.35 }}
            loading="lazy"
          />
          <div className="absolute left-3 top-3 flex flex-col gap-2">
            {badge === "new" ? <Badge tone="accent">New arrival</Badge> : null}
            {badge === "featured" ? <Badge tone="default">Featured</Badge> : null}
          </div>
        </Link>
        <CardContent className="flex flex-1 flex-col gap-3 pt-4">
          <div className="space-y-1">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">
              {product.category_id}
            </p>
            <Link
              to={`/catalog/products/${product.product_id}`}
              className="font-display text-xl leading-tight text-foreground transition-opacity hover:opacity-80"
            >
              {product.name}
            </Link>
            <p className="line-clamp-2 text-sm text-muted-foreground">{product.description}</p>
          </div>
          <div className="mt-auto flex items-center justify-between gap-3 pt-2">
            <span className="text-lg font-semibold text-foreground">
              {price != null ? formatCurrency(price) : "—"}
            </span>
            <Button
              size="sm"
              variant="secondary"
              disabled={!defaultItem || loading || added}
              onClick={handleAdd}
              aria-label={`Add ${product.name} to cart`}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : added ? (
                <>
                  <Check className="h-4 w-4" />
                  Added
                </>
              ) : (
                <>
                  <ShoppingCart className="h-4 w-4" />
                  Add
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.article>
  );
}
