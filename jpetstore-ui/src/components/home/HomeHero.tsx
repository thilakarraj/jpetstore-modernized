import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { useMotionSafe } from "@/hooks/useMotionSafe";

/** Hero pattern inspired by 21st.dev Commerce Hero — customized for JPetStore tokens */
export function HomeHero() {
  const { transition, reduce } = useMotionSafe();

  return (
    <section
      className="relative overflow-hidden border-b border-border"
      style={{ background: "var(--gradient-hero)" }}
    >
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 md:grid-cols-2 md:py-24 lg:px-8">
        <motion.div
          initial={reduce ? false : { opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={transition}
          className="flex flex-col justify-center"
        >
          <p className="mb-3 text-sm font-medium uppercase tracking-[0.2em] text-accent">
            JPetStore
          </p>
          <h1 className="text-balance font-display text-4xl leading-none sm:text-5xl lg:text-6xl">
            Premium care for every companion
          </h1>
          <p className="mt-5 max-w-lg text-base leading-relaxed text-muted-foreground sm:text-lg">
            Discover curated fish, dogs, cats, birds, and reptiles with the clarity and polish
            you expect from a modern marketplace — built on the classic JPetStore catalog.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/catalog">
              <Button className="inline-flex items-center gap-2">
                Shop catalog
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/categories/FISH">
              <Button variant="outline">Explore Fish</Button>
            </Link>
          </div>
        </motion.div>
        <motion.div
          initial={reduce ? false : { opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ ...transition, delay: reduce ? 0 : 0.1 }}
          className="relative min-h-[280px] overflow-hidden rounded-2xl border border-border shadow-elevated md:min-h-[420px]"
        >
          <img
            src="/images/mock/hero.svg"
            alt="Happy pets in a premium studio setting"
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent" />
        </motion.div>
      </div>
    </section>
  );
}
