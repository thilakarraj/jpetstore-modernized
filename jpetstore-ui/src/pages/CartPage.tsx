import { Link } from "react-router-dom";
import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useCartStore } from "@/store/cartStore";
import { formatCurrency } from "@/utils/cn";

export function CartPage() {
  const cart = useCartStore((s) => s.cart);
  const updateQuantity = useCartStore((s) => s.updateQuantity);
  const removeItem = useCartStore((s) => s.removeItem);

  const cartError = useCartStore((s) => s.cartError);

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-4xl">Shopping cart</h1>
      {cartError ? (
        <p className="mt-4 text-sm text-error" role="alert">
          {cartError}
        </p>
      ) : null}
      {cart.lines.length === 0 ? (
        <div className="mt-10 rounded-xl border border-border bg-surface p-10 text-center">
          <p className="text-muted-foreground">Your cart is empty.</p>
          <Link to="/catalog" className="mt-4 inline-block">
            <Button className="mt-4">Browse catalog</Button>
          </Link>
        </div>
      ) : (
        <div className="mt-8 grid gap-8 lg:grid-cols-[1fr_320px]">
          <ul className="space-y-4">
            {cart.lines.map((line) => (
              <li
                key={line.item_id}
                className="flex flex-col gap-4 rounded-xl border border-border bg-surface p-4 sm:flex-row sm:items-center"
              >
                {line.image_url ? (
                  <img
                    src={line.image_url}
                    alt=""
                    className="h-24 w-24 rounded-lg object-cover"
                  />
                ) : null}
                <div className="flex-1">
                  <p className="font-medium">{line.product_name}</p>
                  <p className="text-sm text-muted-foreground">
                    Item {line.item_id}
                    {line.attribute1 ? ` · ${line.attribute1}` : ""}
                  </p>
                  <p className="mt-1 text-sm">{formatCurrency(line.unit_price)} each</p>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    min={1}
                    value={line.quantity}
                    onChange={(e) =>
                      void updateQuantity(line.item_id, Number(e.target.value) || 1).catch(
                        () => undefined,
                      )
                    }
                    className="h-10 w-16 rounded-lg border border-input-border bg-input px-2 text-center text-sm"
                    aria-label={`Quantity for ${line.product_name}`}
                  />
                  <button
                    type="button"
                    className="cursor-pointer rounded-lg p-2 text-muted-foreground hover:text-error"
                    onClick={() => void removeItem(line.item_id).catch(() => undefined)}
                    aria-label={`Remove ${line.product_name}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
          <aside className="h-fit rounded-xl border border-border bg-surface p-6 shadow-card">
            <h2 className="font-display text-2xl">Summary</h2>
            <p className="mt-4 flex justify-between text-sm">
              <span className="text-muted-foreground">Items</span>
              <span>{cart.item_count}</span>
            </p>
            <p className="mt-2 flex justify-between text-lg font-semibold">
              <span>Subtotal</span>
              <span>{formatCurrency(cart.subtotal)}</span>
            </p>
            <Link to="/checkout" className="mt-6 block">
              <Button className="w-full">Proceed to checkout</Button>
            </Link>
          </aside>
        </div>
      )}
    </div>
  );
}
