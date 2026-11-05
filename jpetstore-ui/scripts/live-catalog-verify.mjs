/**
 * Live catalog browser smoke test (Playwright).
 * Prerequisites: backend on :8000, Vite dev server on :5173 with VITE_USE_MOCK_API=false.
 */
import { chromium } from "playwright";

const UI_BASE = process.env.UI_BASE_URL ?? "http://localhost:5173";
const API_BASE = process.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const apiCalls = [];
  const failed = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") failed.push(`console: ${msg.text()}`);
  });
  page.on("response", (res) => {
    const url = res.url();
    if (url.includes("/api/v1/catalog")) {
      apiCalls.push({ url, status: res.status() });
      if (res.status() >= 400) failed.push(`HTTP ${res.status()} ${url}`);
    }
  });

  await page.goto(UI_BASE, { waitUntil: "networkidle", timeout: 60_000 });

  const categoriesResponse = await page.waitForResponse(
    (r) => r.url().includes("/api/v1/catalog/categories") && r.status() === 200,
    { timeout: 20_000 },
  );
  apiCalls.push({ url: categoriesResponse.url(), status: categoriesResponse.status() });

  await page.waitForSelector("text=Featured categories", { timeout: 15_000 });
  const categoryLink = page.locator('a[href="/categories/FISH"]').first();
  await categoryLink.waitFor({ state: "visible", timeout: 15_000 });

  await categoryLink.click();
  await page.waitForURL("**/categories/FISH", { timeout: 10_000 });
  await page.getByRole("heading", { name: /Fish/i }).waitFor({ timeout: 10_000 });
  await page.getByRole("link", { name: /Angelfish/i }).first().waitFor({ timeout: 15_000 });

  await page.goto(`${UI_BASE}/catalog/search`, { waitUntil: "networkidle" });
  await page.getByLabel("Search keyword").fill("fish");
  await page.getByRole("button", { name: "Search" }).click();
  await page.getByRole("link", { name: /Angelfish/i }).first().waitFor({ timeout: 15_000 });

  await page.goto(`${UI_BASE}/catalog/products/FI-SW-01`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Angelfish" }).waitFor({ timeout: 15_000 });

  const backendHits = apiCalls.filter(
    (c) => c.url.startsWith(API_BASE) || c.url.includes("/api/v1/catalog"),
  );

  await browser.close();

  console.log(
    JSON.stringify(
      {
        ok: failed.length === 0 && backendHits.length > 0,
        apiCalls: backendHits.length,
        failed,
        sampleCalls: backendHits.slice(0, 5),
      },
      null,
      2,
    ),
  );
  if (failed.length > 0 || backendHits.length === 0) process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
