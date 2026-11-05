import { lazy, Suspense, useEffect } from "react";
import { Navigate, Route, Routes, useParams } from "react-router-dom";
import { MainLayout } from "@/layouts/MainLayout";
import { ProtectedRoute } from "@/components/routing/ProtectedRoute";
import { HomePage } from "@/pages/HomePage";
import { CatalogPage, CatalogSearchPage, CategoryPage } from "@/pages/CatalogPage";
import { CartPage } from "@/pages/CartPage";
import {
  AccountPage,
  RegisterPage,
  SignOnPage,
} from "@/pages/AuthPages";
import { CheckoutPage, OrderConfirmationPage, OrdersPage } from "@/pages/CheckoutOrdersPages";
import { HelpPage } from "@/pages/HelpPage";
import { useAuthStore } from "@/store/authStore";

const ProductDetailPage = lazy(() =>
  import("@/pages/ProductDetailPage").then((m) => ({ default: m.ProductDetailPage })),
);

function CategoryRoute() {
  const { categoryId = "" } = useParams();
  return <CategoryPage categoryId={categoryId} />;
}

function ProductRoute() {
  const { productId = "" } = useParams();
  return (
    <Suspense fallback={<p className="p-10 text-muted-foreground">Loading…</p>}>
      <ProductDetailPage productId={productId} />
    </Suspense>
  );
}

function OrderRoute() {
  const { orderId = "" } = useParams();
  return <OrderConfirmationPage orderId={orderId} />;
}

export function AppRoutes() {
  const loadProfile = useAuthStore((s) => s.loadProfile);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="catalog" element={<CatalogPage />} />
        <Route path="catalog/search" element={<CatalogSearchPage />} />
        <Route path="categories/:categoryId" element={<CategoryRoute />} />
        <Route path="catalog/products/:productId" element={<ProductRoute />} />
        <Route path="cart" element={<CartPage />} />
        <Route path="checkout" element={<CheckoutPage />} />
        <Route path="signon" element={<SignOnPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route
          path="account"
          element={
            <ProtectedRoute>
              <AccountPage />
            </ProtectedRoute>
          }
        />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="orders/:orderId" element={<OrderRoute />} />
        <Route path="help" element={<HelpPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
