import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { StoreProductCard } from "@/components/product/StoreProductCard";
import { Select } from "@/components/ui/Select";
import {
  enrichProduct,
  fetchAllProducts,
  fetchCategories,
  fetchCategory,
  fetchProductsByCategory,
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

  useEffect(() => {
    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const [cats, list] = await Promise.all([fetchCategories(), fetchAllProducts()]);
        setCategories(cats);
        setProducts(list.map(enrichProduct));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load catalog");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

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

      {loading ? <p className="text-muted-foreground">Loading products…</p> : null}
      {error ? <p className="text-error">{error}</p> : null}

      {!loading && slice.length === 0 ? (
        <p className="rounded-xl border border-border bg-surface p-8 text-center text-muted-foreground">
          No products match your filters.
        </p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {slice.map((product) => (
            <StoreProductCard key={product.product_id} product={product} />
          ))}
        </div>
      )}

      {totalPages > 1 ? (
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
      setError(e instanceof Error ? e.message : "Search failed");
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
      {error ? <p className="mt-4 text-error">{error}</p> : null}
      {loading ? <p className="mt-6 text-muted-foreground">Searching…</p> : null}
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

  useEffect(() => {
    void (async () => {
      setLoading(true);
      const [cat, list] = await Promise.all([
        fetchCategory(categoryId),
        fetchProductsByCategory(categoryId),
      ]);
      setCategory(cat);
      setProducts(list.map(enrichProduct));
      setLoading(false);
    })();
  }, [categoryId]);

  if (loading) {
    return <p className="p-10 text-muted-foreground">Loading category…</p>;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm uppercase tracking-widest text-accent">{category?.category_id}</p>
      <h1 className="font-display text-4xl">{category?.name}</h1>
      <p className="mt-2 max-w-2xl text-muted-foreground">{category?.description}</p>
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {products.map((product) => (
          <StoreProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </div>
  );
}
