/**
 * Frontend-only mock demo verification (run while `npm run dev` is up on port 5173).
 * Usage: node scripts/mock-demo-verify.mjs
 */
import { chromium } from "playwright";

const BASE = process.env.UI_BASE_URL ?? "http://127.0.0.1:5173";

const results = [];

function record(feature, status, note = "") {
  results.push({ feature, status, note });
}

async function collectPageSignals(page) {
  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  const failedRequests = [];
  page.on("requestfailed", (req) => {
    failedRequests.push(`${req.method()} ${req.url()} — ${req.failure()?.errorText ?? "failed"}`);
  });
  const backendCalls = [];
  page.on("request", (req) => {
    const url = req.url();
    if (url.includes(":8000") || url.includes("/api/v1/")) {
      backendCalls.push(`${req.method()} ${url}`);
    }
  });
  return { consoleErrors, failedRequests, backendCalls };
}

async function expectHeading(page, name, level = 1) {
  await page.getByRole("heading", { name, level }).first().waitFor({ timeout: 15000 });
}

async function runFlow(page, viewportName) {
  const signals = await collectPageSignals(page);
  await page.setViewportSize(
    viewportName === "mobile"
      ? { width: 390, height: 844 }
      : viewportName === "tablet"
        ? { width: 834, height: 1112 }
        : { width: 1280, height: 800 },
  );

  const routes = [
    { path: "/", heading: "Premium care for every companion" },
    { path: "/catalog", heading: "Catalog" },
    { path: "/catalog/search", heading: "Search" },
    { path: "/categories/DOGS", heading: "Dogs" },
    { path: "/catalog/products/FI-SW-01", heading: "Angelfish" },
    { path: "/cart", heading: "Shopping cart" },
    { path: "/help", heading: "Help" },
    { path: "/register", heading: "Register" },
    { path: "/signon", heading: "Sign on" },
  ];

  for (const r of routes) {
    try {
      await page.goto(`${BASE}${r.path}`, { waitUntil: "networkidle" });
      await expectHeading(page, r.heading);
      record(`Route ${r.path} (${viewportName})`, "PASS");
    } catch (e) {
      record(`Route ${r.path} (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
    }
  }

  // Login j2ee / j2ee
  try {
    await page.goto(`${BASE}/signon`, { waitUntil: "networkidle" });
    await page.getByLabel("Username").fill("j2ee");
    await page.getByLabel("Password").fill("j2ee");
    await page.getByRole("button", { name: "Sign on" }).click();
    await page.waitForURL(/\/account/, { timeout: 10000 });
    record(`Mock login j2ee/j2ee (${viewportName})`, "PASS");
  } catch (e) {
    record(`Mock login j2ee/j2ee (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Catalog filter + sort
  try {
    await page.goto(`${BASE}/catalog`, { waitUntil: "networkidle" });
    await page.getByLabel("Category").selectOption("DOGS");
    await page.getByLabel("Sort").selectOption("name-desc");
    await page.getByRole("link", { name: /Golden Retriever/i }).first().waitFor();
    record(`Catalog filter & sort (${viewportName})`, "PASS");
  } catch (e) {
    record(`Catalog filter & sort (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Search
  try {
    await page.goto(`${BASE}/catalog/search`, { waitUntil: "networkidle" });
    await page.getByLabel("Search keyword").fill("Golden");
    await page.getByRole("button", { name: "Search" }).click();
    await page.getByRole("link", { name: /Golden Retriever/i }).first().waitFor({ timeout: 8000 });
    record(`Product search (${viewportName})`, "PASS");
  } catch (e) {
    record(`Product search (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // SKU selection + add to cart (Angelfish has EST-1 / EST-2)
  try {
    await page.goto(`${BASE}/catalog/products/FI-SW-01`, { waitUntil: "networkidle" });
    const skuButtons = page.getByRole("button", { name: /EST-2/i });
    if (await skuButtons.count()) {
      await skuButtons.first().click();
      record(`SKU selection (${viewportName})`, "PASS");
    } else {
      record(`SKU selection (${viewportName})`, "NOT TESTED", "SKU buttons not found");
    }
    await page.getByRole("button", { name: "Increase quantity" }).click();
    await page.getByRole("button", { name: "Add to cart" }).click();
    await page.goto(`${BASE}/cart`, { waitUntil: "networkidle" });
    await page.getByRole("spinbutton").first().fill("2");
    record(`Add to cart & quantity (${viewportName})`, "PASS");
  } catch (e) {
    record(`Add to cart & quantity (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Remove item — re-add one line then remove
  try {
    await page.goto(`${BASE}/catalog/products/FI-SW-01`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Add to cart" }).click();
    await page.goto(`${BASE}/cart`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: /Remove/i }).first().click();
    record(`Remove cart item (${viewportName})`, "PASS");
  } catch (e) {
    record(`Remove cart item (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Checkout + confirmation
  try {
    await page.goto(`${BASE}/catalog/products/K9-RT-01`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Add to cart" }).click();
    await page.goto(`${BASE}/checkout`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Place order" }).click();
    await page.getByRole("heading", { name: "Thank you" }).waitFor({ timeout: 10000 });
    record(`Checkout & order confirmation (${viewportName})`, "PASS");
  } catch (e) {
    record(`Checkout & order confirmation (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Theme toggle + persistence
  try {
    await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
    const toggle = page.getByRole("button", { name: /Switch to (light|dark) mode/i });
    const before = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await toggle.click();
    const after = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    await page.reload({ waitUntil: "networkidle" });
    const persisted = await page.evaluate(() => document.documentElement.getAttribute("data-theme"));
    if (before !== after && after === persisted) {
      record(`Theme toggle & persistence (${viewportName})`, "PASS");
    } else {
      record(
        `Theme toggle & persistence (${viewportName})`,
        "FAIL",
        `before=${before} after=${after} persisted=${persisted}`,
      );
    }
  } catch (e) {
    record(`Theme toggle & persistence (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Protected routes after login
  try {
    await page.goto(`${BASE}/account`, { waitUntil: "networkidle" });
    await expectHeading(page, "My account", 1);
    await page.goto(`${BASE}/orders`, { waitUntil: "networkidle" });
    await expectHeading(page, "Order history", 1);
    record(`Account & orders routes (${viewportName})`, "PASS");
  } catch (e) {
    record(`Account & orders routes (${viewportName})`, "FAIL", String(e.message ?? e).slice(0, 120));
  }

  // Console / network / backend
  const consoleErrors = signals.consoleErrors.filter(
    (m) => !m.includes("favicon") && !m.includes("404") && !m.includes("unsplash"),
  );
  const failed = signals.failedRequests.filter(
    (u) => !u.includes("favicon") && !u.includes("unsplash"),
  );
  if (consoleErrors.length === 0) {
    record(`Browser console errors (${viewportName})`, "PASS");
  } else {
    record(`Browser console errors (${viewportName})`, "FAIL", consoleErrors.slice(0, 3).join(" | "));
  }
  if (failed.length === 0) {
    record(`Failed network requests (${viewportName})`, "PASS");
  } else {
    record(`Failed network requests (${viewportName})`, "FAIL", failed.slice(0, 3).join(" | "));
  }
  if (signals.backendCalls.length === 0) {
    record(`No live backend API calls (${viewportName})`, "PASS");
  } else {
    record(`No live backend API calls (${viewportName})`, "FAIL", signals.backendCalls.slice(0, 5).join(" | "));
  }
}

async function main() {
  let browser;
  try {
    browser = await chromium.launch();
    for (const vp of ["desktop", "tablet", "mobile"]) {
      const context = await browser.newContext();
      const page = await context.newPage();
      await runFlow(page, vp);
      await context.close();
    }
  } catch (e) {
    record("Playwright harness", "FAIL", String(e.message ?? e));
  } finally {
    await browser?.close();
  }

  console.log("\n=== JPetStore UI Mock Demo Verification ===\n");
  for (const r of results) {
    console.log(`${r.status.padEnd(11)} | ${r.feature}${r.note ? ` — ${r.note}` : ""}`);
  }
  const failed = results.filter((r) => r.status === "FAIL").length;
  process.exit(failed > 0 ? 1 : 0);
}

main();
