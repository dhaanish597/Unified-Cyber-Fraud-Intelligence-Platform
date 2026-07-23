import { test, expect } from '@playwright/test';

test('has title and renders react app', async ({ page }) => {
  page.on('console', msg => console.log('BROWSER CONSOLE:', msg.text()));
  page.on('pageerror', error => console.log('BROWSER ERROR:', error.message));

  await page.goto('http://localhost:5173/');

  // Verify the page title matches
  await expect(page).toHaveTitle(/Unified Cyber-Fraud Intelligence Platform/i);
  
  // Wait for network idle to allow react to mount
  await page.waitForLoadState('networkidle');
  
  const rootHtml = await page.locator('#root').innerHTML();
  console.log('ROOT HTML:', rootHtml);
  
  const rootText = await page.locator('#root').textContent();
  expect(rootText?.length).toBeGreaterThan(0);
});
