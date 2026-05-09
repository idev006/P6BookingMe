import { test, expect } from "@playwright/test";

test("app loads and shows root page", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/BookingMe|P6/i);
});

test("health endpoint returns ok", async ({ request }) => {
  const response = await request.get("http://localhost:8000/health");
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  expect(body.status).toBe("ok");
  expect(body.project).toBe("P6BookingMe");
});
