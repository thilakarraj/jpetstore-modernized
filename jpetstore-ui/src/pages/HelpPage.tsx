export function HelpPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-4xl">Help</h1>
      <p className="mt-4 text-muted-foreground">
        This storefront mirrors JPetStore flows: browse categories, view item SKUs, manage a cart,
        sign on, and place orders. Catalog and cart APIs use fixtures until backend catalog routes
        are available; set <code>VITE_USE_MOCK_API=false</code> and configure{" "}
        <code>VITE_API_BASE_URL</code> for live auth integration.
      </p>
    </div>
  );
}
