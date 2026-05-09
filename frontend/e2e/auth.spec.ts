import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should allow a user to register and see pending message', async ({ page }) => {
    await page.goto('/register');
    
    await page.fill('input[placeholder*="ชื่อ-นามสกุล"]', 'Test User');
    await page.fill('input[placeholder*="อีเมล"]', `test_${Date.now()}@example.com`);
    await page.fill('input[placeholder*="รหัสพนักงาน"]', `EMP_${Date.now()}`);
    await page.fill('input[placeholder*="รหัสผ่าน"]', 'Password123!');
    await page.fill('input[placeholder*="ยืนยันรหัสผ่าน"]', 'Password123!');
    
    await page.click('button[type="submit"]');
    
    // Check for success message or pending status
    await expect(page.locator('text=รอการอนุมัติ')).toBeVisible();
  });

  test('should show error on invalid login', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.alert-error')).toBeVisible();
  });
});
