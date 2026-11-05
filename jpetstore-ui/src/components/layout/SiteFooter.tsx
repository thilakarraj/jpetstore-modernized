import { Link } from "react-router-dom";

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-border bg-surface">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <div>
          <p className="font-display text-xl">JPetStore</p>
          <p className="mt-1 max-w-md text-sm text-muted-foreground">
            Modern storefront UI for the JPetStore modernization program. Catalog, cart, and
            checkout flows follow legacy terminology.
          </p>
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
          <Link className="cursor-pointer hover:text-foreground" to="/catalog">
            Catalog
          </Link>
          <Link className="cursor-pointer hover:text-foreground" to="/orders">
            Orders
          </Link>
          <Link className="cursor-pointer hover:text-foreground" to="/help">
            Help
          </Link>
        </div>
      </div>
    </footer>
  );
}
