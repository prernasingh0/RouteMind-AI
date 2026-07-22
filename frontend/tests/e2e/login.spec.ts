import { expect, test } from '@playwright/test';
test('login route renders credential form', async ({ page }) => { await page.goto('/login'); await expect(page.getByText('Sign in to RouteMind AI')).toBeVisible(); });
