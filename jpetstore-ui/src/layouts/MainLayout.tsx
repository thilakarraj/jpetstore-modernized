import { Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { SiteFooter } from "@/components/layout/SiteFooter";
import { SiteHeader } from "@/components/layout/SiteHeader";
import { useMotionSafe } from "@/hooks/useMotionSafe";

export function MainLayout() {
  const location = useLocation();
  const { transition, reduce } = useMotionSafe();

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          initial={reduce ? false : { opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={reduce ? undefined : { opacity: 0, y: -8 }}
          transition={transition}
          className="flex-1"
        >
          <Outlet />
        </motion.main>
      </AnimatePresence>
      <SiteFooter />
    </div>
  );
}
