import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Link, useNavigate } from "react-router-dom";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ProtectedRoute } from "@/components/routing/ProtectedRoute";
import { useAuthStore } from "@/store/authStore";
import { useCartStore } from "@/store/cartStore";
import { formatCurrency } from "@/utils/cn";
import { getApiErrorMessage } from "@/services/api/client";

const checkoutSchema = z.object({
  ship_addr1: z.string().min(1, "Address is required"),
  ship_addr2: z.string().optional(),
  ship_city: z.string().min(1),
  ship_state: z.string().min(1),
  ship_zip: z.string().min(1),
  ship_country: z.string().min(1),
});

type CheckoutForm = z.infer<typeof checkoutSchema>;

export function CheckoutPage() {
  return (
    <ProtectedRoute>
      <CheckoutFormInner />
    </ProtectedRoute>
  );
}

function CheckoutFormInner() {
  const user = useAuthStore((s) => s.user);
  const cart = useCartStore((s) => s.cart);
  const placeOrder = useCartStore((s) => s.placeOrder);
  const cartError = useCartStore((s) => s.cartError);
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CheckoutForm>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      ship_addr1: user?.address1 ?? "",
      ship_city: user?.city ?? "",
      ship_state: user?.state ?? "",
      ship_zip: user?.zip ?? "",
      ship_country: user?.country ?? "USA",
    },
  });

  useEffect(() => {
    if (!user) return;
    reset({
      ship_addr1: user.address1 ?? "",
      ship_addr2: "",
      ship_city: user.city ?? "",
      ship_state: user.state ?? "",
      ship_zip: user.zip ?? "",
      ship_country: user.country ?? "USA",
    });
  }, [user, reset]);

  if (cart.lines.length === 0) {
    return (
      <div className="mx-auto max-w-lg px-4 py-14 text-center">
        <p className="text-muted-foreground">Your cart is empty.</p>
        <Link to="/catalog">
          <Button className="mt-4">Shop catalog</Button>
        </Link>
      </div>
    );
  }

  const onSubmit = handleSubmit(async (values) => {
    if (!user) {
      setSubmitError("Please sign on before checkout.");
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      const order = await placeOrder(values, user);
      navigate(`/orders/${order.order_id}`, { replace: true });
    } catch (e) {
      setSubmitError(getApiErrorMessage(e));
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-4xl">Checkout</h1>
      <form onSubmit={onSubmit} className="mt-8 grid gap-8 lg:grid-cols-[1fr_320px]">
        <div className="space-y-4 rounded-xl border border-border bg-surface p-6">
          <h2 className="font-display text-2xl">Shipping address</h2>
          <Input label="Address line 1" error={errors.ship_addr1?.message} {...register("ship_addr1")} />
          <Input label="Address line 2" {...register("ship_addr2")} />
          <div className="grid gap-4 sm:grid-cols-2">
            <Input label="City" error={errors.ship_city?.message} {...register("ship_city")} />
            <Input label="State" error={errors.ship_state?.message} {...register("ship_state")} />
            <Input label="Zip" error={errors.ship_zip?.message} {...register("ship_zip")} />
            <Input label="Country" error={errors.ship_country?.message} {...register("ship_country")} />
          </div>
        </div>
        <aside className="h-fit rounded-xl border border-border bg-surface p-6">
          <h2 className="font-display text-2xl">Order summary</h2>
          <ul className="mt-4 space-y-2 text-sm">
            {cart.lines.map((line) => (
              <li key={line.item_id} className="flex justify-between gap-4">
                <span className="text-muted-foreground">
                  {line.product_name} × {line.quantity}
                </span>
                <span>{formatCurrency(parseFloat(line.unit_price) * line.quantity)}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 flex justify-between border-t border-border pt-4 font-semibold">
            <span>Total</span>
            <span>{formatCurrency(cart.subtotal)}</span>
          </p>
          {submitError || cartError ? (
            <p className="mt-3 text-sm text-error" role="alert">
              {submitError ?? cartError}
            </p>
          ) : null}
          <Button type="submit" className="mt-6 w-full" loading={submitting}>
            Place order
          </Button>
        </aside>
      </form>
    </div>
  );
}

export function OrderConfirmationPage({ orderId }: { orderId: string }) {
  const orders = useCartStore((s) => s.orders);
  const loadOrderDetail = useCartStore((s) => s.loadOrderDetail);
  const [loading, setLoading] = useState(true);
  const numericId = Number(orderId);
  const order = orders.find((o) => String(o.order_id) === orderId);

  useEffect(() => {
    void (async () => {
      if (order?.lines.length) {
        setLoading(false);
        return;
      }
      if (Number.isFinite(numericId)) {
        await loadOrderDetail(numericId);
      }
      setLoading(false);
    })();
  }, [orderId, numericId, loadOrderDetail, order?.lines.length]);

  if (loading) {
    return <p className="p-10 text-muted-foreground">Loading order…</p>;
  }

  const resolved = orders.find((o) => String(o.order_id) === orderId);

  if (!resolved) {
    return (
      <div className="mx-auto max-w-lg px-4 py-14 text-center">
        <p className="text-muted-foreground">Order not found.</p>
        <Link to="/orders">
          <Button className="mt-4" variant="outline">
            Order history
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-14 sm:px-6">
      <p className="text-sm uppercase tracking-widest text-success">Order confirmed</p>
      <h1 className="mt-2 font-display text-4xl">Thank you</h1>
      <p className="mt-2 text-muted-foreground">
        Order #{resolved.order_id} · Status {resolved.status} (Pending)
      </p>
      <div className="mt-8 rounded-xl border border-border bg-surface p-6">
        <p className="text-sm text-muted-foreground">Ship to</p>
        <p className="mt-1">
          {resolved.ship_addr1}, {resolved.ship_city}, {resolved.ship_state} {resolved.ship_zip},{" "}
          {resolved.ship_country}
        </p>
        <p className="mt-4 font-semibold">Total {formatCurrency(resolved.total)}</p>
      </div>
      <Link to="/orders" className="mt-6 inline-block text-accent hover:underline">
        View all orders
      </Link>
    </div>
  );
}

export function OrdersPage() {
  const orders = useCartStore((s) => s.orders);
  const loadOrders = useCartStore((s) => s.loadOrders);
  const ordersLoading = useCartStore((s) => s.ordersLoading);

  useEffect(() => {
    void loadOrders();
  }, [loadOrders]);

  return (
    <ProtectedRoute>
      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
        <h1 className="font-display text-4xl">Order history</h1>
        {ordersLoading ? (
          <p className="mt-8 text-muted-foreground">Loading orders…</p>
        ) : orders.length === 0 ? (
          <p className="mt-8 text-muted-foreground">No orders yet.</p>
        ) : (
          <ul className="mt-8 space-y-3">
            {orders.map((order) => (
              <li key={order.order_id}>
                <Link
                  to={`/orders/${order.order_id}`}
                  className="flex cursor-pointer flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-surface p-4 transition-shadow hover:shadow-card"
                >
                  <div>
                    <p className="font-medium">Order #{order.order_id}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(order.order_date).toLocaleString()} · Status {order.status}
                    </p>
                  </div>
                  <span className="font-semibold">{formatCurrency(order.total)}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </ProtectedRoute>
  );
}
