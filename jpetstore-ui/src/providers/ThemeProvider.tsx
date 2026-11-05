import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import {
  applyThemeToDocument,
  readStoredTheme,
  THEME_STORAGE_KEY,
  type ThemeMode,
} from "@/utils/theme";

interface ThemeContextValue {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

function subscribe(onStoreChange: () => void) {
  const handler = () => onStoreChange();
  window.addEventListener("storage", handler);
  window.addEventListener("jpetstore-theme-change", handler);
  return () => {
    window.removeEventListener("storage", handler);
    window.removeEventListener("jpetstore-theme-change", handler);
  };
}

function getThemeSnapshot(): ThemeMode {
  return readStoredTheme();
}

function getServerSnapshot(): ThemeMode {
  return "dark";
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const theme = useSyncExternalStore(subscribe, getThemeSnapshot, getServerSnapshot);

  const setTheme = useCallback((next: ThemeMode) => {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch {
      /* ignore */
    }
    applyThemeToDocument(next);
    window.dispatchEvent(new Event("jpetstore-theme-change"));
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [setTheme, theme]);

  const value = useMemo(
    () => ({ theme, setTheme, toggleTheme }),
    [theme, setTheme, toggleTheme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within ThemeProvider");
  }
  return ctx;
}
