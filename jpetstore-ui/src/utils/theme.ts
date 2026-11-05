export type ThemeMode = "dark" | "light";

export const THEME_STORAGE_KEY = "jpetstore-theme";

export function readStoredTheme(): ThemeMode {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
  } catch {
    /* ignore */
  }
  return "dark";
}

export function applyThemeToDocument(theme: ThemeMode): void {
  document.documentElement.setAttribute("data-theme", theme);
}
