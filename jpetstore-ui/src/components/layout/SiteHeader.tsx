import { useEffect } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Menu, PawPrint, Search, ShoppingBag, User, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { Button } from "@/components/ui/Button";
import { useAuthStore } from "@/store/authStore";
import { useCartStore } from "@/store/cartStore";
import { cn } from "@/utils/cn";
import { useState } from "react";

const navLinks = [
  { to: "/catalog", label: "Catalog" },
  { to: "/categories/FISH", label: "Fish" },
  { to: "/categories/DOGS", label: "Dogs" },
  { to: "/categories/CATS", label: "Cats" },
];

export function SiteHeader() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const itemCount = useCartStore((s) => s.cart.item_count);
  const cartBump = useCartStore((s) => s.cartBump);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const logout = useAuthStore((s) => s.logout);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    navigate(`/catalog/search?q=${encodeURIComponent(q)}`);
    setOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          className="flex shrink-0 items-center gap-2 font-display text-xl tracking-tight"
        >
          <PawPrint className="h-6 w-6 text-accent" aria-hidden />
          JPetStore
        </Link>

        <nav className="hidden items-center gap-1 lg:flex" aria-label="Primary">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  "cursor-pointer rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive ? "bg-muted text-foreground" : "text-muted-foreground hover:text-foreground",
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <form onSubmit={onSearch} className="ml-auto hidden max-w-sm flex-1 md:flex">
          <div className="relative w-full">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search products…"
              className="h-10 w-full rounded-lg border border-input-border bg-input pl-9 pr-3 text-sm"
              aria-label="Search products"
            />
          </div>
        </form>

        <div className="flex items-center gap-1 sm:gap-2">
          <ThemeToggle />
          <Link to={isAuthenticated ? "/account" : "/signon"} aria-label="Account">
            <Button variant="ghost" size="icon">
              <User className="h-5 w-5" />
            </Button>
          </Link>
          <Link to="/cart" className="relative" aria-label={`Cart, ${itemCount} items`}>
            <Button variant="ghost" size="icon">
              <ShoppingBag className={cn("h-5 w-5", cartBump && "animate-cart-bump")} />
              {itemCount > 0 ? (
                <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-accent px-1 text-[10px] font-semibold text-accent-foreground">
                  {itemCount}
                </span>
              ) : null}
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <AnimatePresence>
        {open ? (
          <>
            <motion.button
              type="button"
              className="fixed inset-0 z-40 cursor-pointer bg-overlay lg:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              aria-label="Close menu overlay"
            />
            <motion.div
              className="fixed inset-y-0 right-0 z-50 flex w-[min(100%,20rem)] flex-col border-l border-border bg-surface shadow-elevated lg:hidden"
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", damping: 28, stiffness: 320 }}
            >
              <div className="flex items-center justify-between border-b border-border p-4">
                <span className="font-display text-lg">Menu</span>
                <div className="flex items-center gap-1">
                  <ThemeToggle />
                  <Button variant="ghost" size="icon" onClick={() => setOpen(false)} aria-label="Close menu">
                    <X className="h-5 w-5" />
                  </Button>
                </div>
              </div>
              <form onSubmit={onSearch} className="border-b border-border p-4">
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search…"
                  className="h-11 w-full rounded-lg border border-input-border bg-input px-3 text-sm"
                />
              </form>
              <nav className="flex flex-col gap-1 p-4" aria-label="Mobile">
                {navLinks.map((link) => (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) =>
                      cn(
                        "cursor-pointer rounded-lg px-3 py-3 text-base",
                        isActive ? "bg-muted font-medium" : "text-muted-foreground",
                      )
                    }
                  >
                    {link.label}
                  </NavLink>
                ))}
                <Link
                  to={isAuthenticated ? "/account" : "/signon"}
                  className="rounded-lg px-3 py-3 text-muted-foreground"
                  onClick={() => setOpen(false)}
                >
                  {isAuthenticated ? "My account" : "Sign in"}
                </Link>
                {isAuthenticated ? (
                  <button
                    type="button"
                    className="cursor-pointer rounded-lg px-3 py-3 text-left text-muted-foreground"
                    onClick={() => {
                      logout();
                      setOpen(false);
                    }}
                  >
                    Sign out
                  </button>
                ) : null}
              </nav>
            </motion.div>
          </>
        ) : null}
      </AnimatePresence>
    </header>
  );
}
