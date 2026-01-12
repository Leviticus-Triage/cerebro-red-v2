/**
 * E2E tests for demo mode functionality.
 * 
 * Tests demo mode banner, API routing, guided tour, and tooltip behavior.
 */

import { test, expect } from '@playwright/test';

test.describe('Demo Mode', () => {
  test.beforeEach(async ({ page }) => {
    // Set demo mode environment variable
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // Inject demo mode into page context
    await page.addInitScript(() => {
      (window as any).__VITE_DEMO_MODE__ = 'true';
    });
  });

  test('should display demo mode banner when VITE_DEMO_MODE is true', async ({ page }) => {
    await page.goto('/');
    
    // Wait for banner to appear
    const banner = page.getByText(/Demo Mode Active/i);
    await expect(banner).toBeVisible();
    
    // Check banner content
    await expect(banner).toContainText('read-only mock data');
    await expect(banner).toContainText('deploy locally');
  });

  test('should route API calls to /api/demo/* in demo mode', async ({ page }) => {
    // Intercept API calls
    const apiCalls: string[] = [];
    page.on('request', (request) => {
      if (request.url().includes('/api/')) {
        apiCalls.push(request.url());
      }
    });

    await page.goto('/');
    
    // Wait for experiments to load
    await page.waitForSelector('[data-tour="experiment-running"], [data-tour="experiment-failed"], [data-tour="experiment-completed"]', {
      timeout: 10000,
    });

    // Check that API calls went to demo endpoints
    const demoCalls = apiCalls.filter(url => url.includes('/api/demo/'));
    expect(demoCalls.length).toBeGreaterThan(0);
  });

  test('should start guided tour automatically on first visit', async ({ page }) => {
    // Clear localStorage to simulate first visit
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('cerebro-tour-storage');
    });

    await page.reload({ waitUntil: 'networkidle' });
    
    // Wait for tour to start
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    // Check tour dialog is visible
    const tourDialog = page.getByText(/Running Experiment|Step 1 of/i);
    await expect(tourDialog).toBeVisible();
  });

  test('should highlight correct experiment cards in tour', async ({ page }) => {
    await page.goto('/');
    
    // Wait for experiments to load
    await page.waitForSelector('[data-tour="experiment-running"]', { timeout: 10000 });
    
    // Check tour attributes exist
    const runningCard = page.locator('[data-tour="experiment-running"]');
    const failedCard = page.locator('[data-tour="experiment-failed"]');
    const completedCard = page.locator('[data-tour="experiment-completed"]');
    
    await expect(runningCard).toBeVisible();
    await expect(failedCard).toBeVisible();
    await expect(completedCard).toBeVisible();
  });

  test('should allow tour to be dismissed and restarted', async ({ page }) => {
    await page.goto('/');
    
    // Start tour if not already started
    const helpButton = page.locator('button[title*="tour"], button:has-text("?")').first();
    if (await helpButton.isVisible()) {
      await helpButton.click();
    }
    
    // Wait for tour dialog
    await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
    
    // Dismiss tour
    const closeButton = page.getByRole('button', { name: /finish|close/i }).first();
    await closeButton.click();
    
    // Tour should be dismissed
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    
    // Restart tour via help button
    await helpButton.click();
    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  test('should show demo tooltip on create experiment button', async ({ page }) => {
    await page.goto('/');
    
    // Find create experiment button
    const createButton = page.getByRole('button', { name: /create.*experiment/i }).first();
    
    if (await createButton.isVisible()) {
      // Hover over button to show tooltip
      await createButton.hover();
      
      // Check tooltip appears
      const tooltip = page.getByText(/Demo mode.*Deploy locally/i);
      await expect(tooltip).toBeVisible({ timeout: 2000 });
    }
  });

  test('should display helpful error message when attempting write operation', async ({ page }) => {
    await page.goto('/');
    
    // Try to create an experiment (should be blocked in demo mode)
    const createButton = page.getByRole('button', { name: /create.*experiment/i }).first();
    
    if (await createButton.isVisible()) {
      await createButton.click();
      
      // Wait for error message
      const errorMessage = page.getByText(/Demo mode|403|Forbidden|deploy locally/i);
      await expect(errorMessage).toBeVisible({ timeout: 5000 });
    }
  });

  test('should show 3 mock experiments on dashboard', async ({ page }) => {
    await page.goto('/');
    
    // Wait for experiments to load
    await page.waitForSelector('[data-tour="experiment-running"]', { timeout: 10000 });
    
    // Check for all 3 demo experiments
    const runningExp = page.getByText(/Demo: Running Experiment/i);
    const failedExp = page.getByText(/Demo: Failed Experiment/i);
    const completedExp = page.getByText(/Demo: Completed Experiment/i);
    
    await expect(runningExp).toBeVisible();
    await expect(failedExp).toBeVisible();
    await expect(completedExp).toBeVisible();
  });
});
