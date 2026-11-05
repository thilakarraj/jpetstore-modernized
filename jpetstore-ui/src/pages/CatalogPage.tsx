import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CatalogStatus } from "@/components/catalog/CatalogStatus";
import { StoreProductCard } from "@/components/product/StoreProductCard";
import { Select } from "@/components/ui/Select";
import {
  enrichProduct,
  fetchAllProducts,
  fetchCategories,
  fetchCategory,
  fetchProductsByCategory,
  getApiErrorMessage,
  searchProducts,
} from "@/services/api/catalogService";
import type { Category, Product } from "@/types/api";

const PAGE_SIZE = 8;

type SortKey = "name-asc" | "name-desc" | "id";

export function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const categoryFilter = searchParams.get("category") ?? "";
  const sort = (searchParams.get("sort") as SortKey) || "name-asc";
  const page = Number(searchParams.get("page") ?? "1");

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCatalog = useCallback(async (signal: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const cats = await fetchCategories();
      if (signal.aborted) return;
      const list = await fetchAllProducts(cats);
      if (signal.aborted) return;
      setCategories(cats);
      setProducts(list.map(enrichProduct));
    } catch (e) {
      if (signal.aborted) return;
      setCategories([]);
      setProducts([]);
      setError(getApiErrorMessage(e));
    } finally {
      if (!signal.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void loadCatalog(controller.signal);
    return () => controller.abort();
  }, [loadCatalog]);

  const filtered = useMemo(() => {
    let list = [...products];
    if (categoryFilter) {
      list = list.filter((p) => p.category_id === categoryFilter);
    }
    list.sort((a, b) => {
      if (sort === "name-desc") return b.name.localeCompare(a.name);
      if (sort === "id") return a.product_id.localeCompare(b.product_id);
      return a.name.localeCompare(b.name);
    });
    return list;
  }, [products, categoryFilter, sort]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const slice = filtered.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  const updateParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page") next.set("page", "1");
    setSearchParams(next);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="font-display text-4xl">Catalog</h1>
          <p className="mt-2 text-muted-foreground">
            Product listing with category filters, sorting, and pagination.
          </p>
        </div>
        <Link to="/catalog/search" className="text-sm text-accent hover:underline">
          Advanced search
        </Link>
      </div>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <Select
          id="catalog-category"
          label="Category"
          value={categoryFilter}
          onChange={(e) => updateParam("category", e.target.value)}
          className="sm:max-w-xs"
          disabled={loading || Boolean(error)}
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.category_id} value={c.category_id}>
              {c.name}
            </option>
          ))}
        </Select>
        <Select
          id="catalog-sort"
          label="Sort"
          value={sort}
          onChange={(e) => updateParam("sort", e.target.value)}
          className="sm:max-w-xs"
        >
          <option value="name-asc">Name (A–Z)</option>
          <option value="name-desc">Name (Z–A)</option>
          <option value="id">Product ID</option>
        </Select>
      </div>

      {loading || error ? (
        <CatalogStatus
          loading={loading}
          error={error}
          onRetry={() => {
            const controller = new AbortController();
            void loadCatalog(controller.signal);
          }}
        />
      ) : null}

      {!loading && !error && slice.length === 0 ? (
        <CatalogStatus
          loading={false}
          error={null}
          empty
          emptyMessage={
            products.length === 0
              ? "No products in the catalog. Seed the backend database (jpetstore-seed)."
              : "No products match your filters."
          }
          onRetry={
            products.length === 0
              ? () => {
                  const controller = new AbortController();
                  void loadCatalog(controller.signal);
                }
              : undefined
          }
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {slice.map((product) => (
            <StoreProductCard key={product.product_id} product={product} />
          ))}
        </div>
      )}

      {!loading && !error && totalPages > 1 ? (
        <div className="mt-10 flex items-center justify-center gap-2">
          <button
            type="button"
            className="cursor-pointer rounded-lg border border-border px-3 py-2 text-sm disabled:opacity-40"
            disabled={currentPage <= 1}
            onClick={() => updateParam("page", String(currentPage - 1))}
          >
            Previous
          </button>
          <span className="text-sm text-muted-foreground">
            Page {currentPage} of {totalPages}
          </span>
          <button
            type="button"
            className="cursor-pointer rounded-lg border border-border px-3 py-2 text-sm disabled:opacity-40"
            disabled={currentPage >= totalPages}
            onClick={() => updateParam("page", String(currentPage + 1))}
          >
            Next
          </button>
        </div>
      ) : null}
    </div>
  );
}

export function CatalogSearchPage() {
  const [params] = useSearchParams();
  const initial = params.get("q") ?? "";
  const [keyword, setKeyword] = useState(initial);
  const [results, setResults] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const runSearch = async (value: string) => {
    setLoading(true);
    setError(null);
    try {
      const list = await searchProducts(value);
      setResults(list.map(enrichProduct));
    } catch (e) {
      setResults([]);
      setError(getApiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initial) void runSearch(initial);
  }, [initial]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="font-display text-4xl">Search</h1>
      <form
        className="mt-6 flex flex-col gap-3 sm:flex-row"
        onSubmit={(e) => {
          e.preventDefault();
          void runSearch(keyword);
        }}
      >
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Enter a keyword…"
          className="h-11 flex-1 rounded-lg border border-input-border bg-input px-3"
          aria-label="Search keyword"
        />
        <button
          type="submit"
          className="h-11 cursor-pointer rounded-lg bg-accent px-5 text-sm font-medium text-accent-foreground"
        >
          Search
        </button>
      </form>
      {error ? (
        <div className="mt-4 rounded-xl border border-error/40 bg-error/5 p-4 text-error" role="alert">
          {error}
        </div>
      ) : null}
      {loading ? <p className="mt-6 text-muted-foreground">Searching…</p> : null}
      {!loading && !error && results.length === 0 && initial ? (
        <p className="mt-6 text-muted-foreground">No products matched your search.</p>
      ) : null}
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {results.map((product) => (
          <StoreProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </div>
  );
}

export function CategoryPage({ categoryId }: { categoryId: string }) {
  const [category, setCategory] = useState<Category | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCategory = useCallback(
    async (signal: AbortSignal) => {
      if (!categoryId.trim()) {
        setError("Missing category ID.");
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const [cat, list] = await Promise.all([
          fetchCategory(categoryId),
          fetchProductsByCategory(categoryId),
        ]);
        if (signal.aborted) return;
        setCategory(cat);
        setProducts(list.map(enrichProduct));
      } catch (e) {
        if (signal.aborted) return;
        setCategory(null);
        setProducts([]);
        setError(getApiErrorMessage(e));
      } finally {
        if (!signal.aborted) setLoading(false);
      }
    },
    [categoryId],
  );

  useEffect(() => {
    const controller = new AbortController();
    void loadCategory(controller.signal);
    return () => controller.abort();
  }, [loadCategory]);

  if (loading || error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <CatalogStatus
          loading={loading}
          error={error}
          onRetry={() => {
            const controller = new AbortController();
            void loadCategory(controller.signal);
          }}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm uppercase tracking-widest text-accent">{category?.category_id}</p>
      <h1 className="font-display text-4xl">{category?.name}</h1>
      <p className="mt-2 max-w-2xl text-muted-foreground">{category?.description}</p>
      {products.length === 0 ? (
        <div className="mt-8">
          <CatalogStatus
            loading={false}
            error={null}
            empty
            emptyMessage="No products in this category."
            onRetry={() => {
              const controller = new AbortController();
              void loadCategory(controller.signal);
            }}
          />
        </div>
      ) : (
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {products.map((product) => (
            <StoreProductCard key={product.product_id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
}
