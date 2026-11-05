import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { HomeHero } from "@/components/home/HomeHero";
import { StoreProductCard } from "@/components/product/StoreProductCard";
import { Button } from "@/components/ui/Button";
import {
  enrichProduct,
  fetchAllProducts,
  fetchCategories,
} from "@/services/api/catalogService";
import type { Category, Product } from "@/types/api";
import { useMotionSafe } from "@/hooks/useMotionSafe";
import { useRecentStore } from "@/store/recentStore";

export function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [featured, setFeatured] = useState<Product[]>([]);
  const [newArrivals, setNewArrivals] = useState<Product[]>([]);
  const recent = useRecentStore((s) => s.products);
  const { stagger, transition, reduce } = useMotionSafe();

  useEffect(() => {
    void (async () => {
      const [cats, products] = await Promise.all([fetchCategories(), fetchAllProducts()]);
      const enriched = products.map(enrichProduct);
      setCategories(cats);
      setFeatured(enriched.slice(0, 4));
      setNewArrivals([...enriched].reverse().slice(0, 4));
    })();
  }, []);

  return (
    <>
      <HomeHero />

      <section className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <h2 className="font-display text-3xl">Featured categories</h2>
            <p className="mt-2 text-muted-foreground">Browse the classic JPetStore departments.</p>
          </div>
          <Link to="/catalog" className="hidden sm:block">
            <Button variant="outline">View all</Button>
          </Link>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((cat, index) => (
            <motion.div
              key={cat.category_id}
              initial={reduce ? false : { opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ ...transition, delay: index * stagger }}
            >
              <Link
                to={`/categories/${cat.category_id}`}
                className="group block cursor-pointer rounded-xl border border-border bg-surface p-6 shadow-card transition-shadow hover:shadow-elevated"
              >
                <p className="text-xs uppercase tracking-widest text-accent">{cat.category_id}</p>
                <h3 className="mt-2 font-display text-2xl">{cat.name}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{cat.description}</p>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      <PromoBand />

      <ProductSection title="Featured products" products={featured} badge="featured" />
      <ProductSection title="New arrivals" products={newArrivals} badge="new" />

      {recent.length > 0 ? (
        <ProductSection title="Recently viewed" products={recent} />
      ) : null}
    </>
  );
}

function ProductSection({
  title,
  products,
  badge,
}: {
  title: string;
  products: Product[];
  badge?: "new" | "featured";
}) {
  const { stagger, transition, reduce } = useMotionSafe();

  return (
    <section className="border-t border-border bg-surface/40 py-14">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <h2 className="font-display text-3xl">{title}</h2>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {products.map((product, index) => (
            <motion.div
              key={product.product_id}
              initial={reduce ? false : { opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ ...transition, delay: index * stagger }}
            >
              <StoreProductCard product={product} badge={badge} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PromoBand() {
  const { transition, reduce } = useMotionSafe();
  return (
    <motion.section
      className="border-y border-border bg-muted/40"
      initial={reduce ? false : { opacity: 0 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={transition}
    >
      <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 px-4 py-12 sm:px-6 md:flex-row md:items-center lg:px-8">
        <div>
          <p className="text-sm font-medium uppercase tracking-widest text-accent">Promotion</p>
          <h2 className="mt-2 font-display text-3xl">Member list &amp; banner preferences</h2>
          <p className="mt-2 max-w-xl text-muted-foreground">
            Register for a JPetStore account to enable My List and category banner options — just
            like the original application workflow.
          </p>
        </div>
        <Link to="/register">
          <Button>Create account</Button>
        </Link>
      </div>
    </motion.section>
  );
}
