/**
 * Vite env resolution for API integration (no secrets logged).
 */

const rawBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
const rawMock = import.meta.env.VITE_USE_MOCK_API as string | undefined;
const rawDevProxy = import.meta.env.VITE_USE_DEV_PROXY as string | undefined;

/** Strip trailing slashes; empty string means same-origin (e.g. Vite dev proxy). */
export function normalizeApiBaseUrl(value: string | undefined): string {
  const trimmed = (value ?? "").trim();
  if (!trimmed) return "";
  return trimmed.replace(/\/+$/, "");
}

/** Mock fixtures only when explicitly "true". */
export function resolveUseMockApi(value: string | undefined): boolean {
  return value === "true";
}

export const useDevProxy = rawDevProxy === "true";

export const apiBaseUrl = useDevProxy ? "" : normalizeApiBaseUrl(rawBase);

export const useMockApi = resolveUseMockApi(rawMock);

export function getApiConfigError(): string | null {
  if (useMockApi) {
    return null;
  }
  if (useDevProxy) {
    return null;
  }
  if (!apiBaseUrl) {
    return (
      "VITE_API_BASE_URL is missing. Copy .env.example to .env and set your FastAPI URL " +
      "(for example http://127.0.0.1:8000), or enable VITE_USE_DEV_PROXY=true with the Vite /api proxy."
    );
  }
  try {
    const parsed = new URL(apiBaseUrl);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return "VITE_API_BASE_URL must be an http(s) URL.";
    }
  } catch {
    return "VITE_API_BASE_URL is not a valid URL.";
  }
  return null;
}

export function logApiConfigInDev(): void {
  if (!import.meta.env.DEV) return;
  const configError = getApiConfigError();
  const mode = useMockApi ? "mock" : useDevProxy ? "live (vite proxy → /api)" : "live";
  console.info(
    `[jpetstore-ui] API mode: ${mode}; base URL: ${apiBaseUrl || "(same origin)"}`,
  );
  if (configError) {
    console.warn(`[jpetstore-ui] ${configError}`);
  }
  if (useMockApi) {
    console.warn(
      "[jpetstore-ui] VITE_USE_MOCK_API=true — catalog data comes from fixtures, not FastAPI.",
    );
  }
}
