import { useReducedMotion } from "framer-motion";

export function useMotionSafe() {
  const reduce = useReducedMotion();
  return {
    reduce: Boolean(reduce),
    transition: reduce ? { duration: 0 } : { duration: 0.35, ease: [0.22, 1, 0.36, 1] },
    stagger: reduce ? 0 : 0.06,
  };
}
