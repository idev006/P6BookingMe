import { test, expect } from '@playwright/test';

test.describe('Admin Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should access admin users management', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page.locator('h1')).toContainText('จัดการสมาชิก');
  });

  test('should access system settings', async ({ page }) => {
    await page.goto('/admin/settings');
    await expect(page.locator('h1')).toContainText('ตั้งค่าระบบ');
  });

  test('should see audit logs', async ({ page }) => {
    await page.goto('/admin/audit-logs');
    await expect(page.locator('h1')).toContainText('Audit Logs');
  });
});
