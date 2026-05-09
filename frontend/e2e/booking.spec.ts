import { test, expect } from '@playwright/test';

test.describe('Booking Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Assume we have a test user pre-created or login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password123'); // Adjust based on seed data
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should navigate to room listing and view detail', async ({ page }) => {
    await page.goto('/rooms');
    await expect(page.locator('h1')).toContainText('ค้นหาห้องประชุม');
    
    // Find first room card and click view
    const firstRoom = page.locator('.card').first();
    await expect(firstRoom).toBeVisible();
    await firstRoom.locator('button:has-text("ดูรายละเอียด")').click();
    
    await expect(page.url()).toContain('/rooms/');
  });

  test('should show calendar overview', async ({ page }) => {
    await page.goto('/calendar');
    await expect(page.locator('.sx__calendar')).toBeVisible();
  });
});
