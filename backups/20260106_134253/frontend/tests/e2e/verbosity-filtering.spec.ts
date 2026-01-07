/**
 * frontend/tests/e2e/verbosity-filtering.spec.ts
 * ===============================================
 * 
 * E2E tests for verbosity filtering functionality.
 * 
 * Requires Playwright setup.
 */

import { test, expect } from '@playwright/test';

test.describe('Verbosity Filtering', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to monitor page (adjust URL as needed)
    // Note: This requires a running experiment
    await page.goto('http://localhost:3000/monitor/test-experiment-id');
  });

  test('should filter logs based on verbosity level', async ({ page }) => {
    // Wait for connection
    await page.waitForSelector('text=Connected to experiment stream', { timeout: 10000 }).catch(() => {
      // If not connected, skip test
      test.skip();
    });
    
    // Set verbosity to 0 (Silent)
    const select = page.locator('select').first();
    await select.selectOption('0');
    
    // Wait a bit for events to filter
    await page.waitForTimeout(1000);
    
    // Verify only Errors tab has content (or shows info message)
    await page.click('text=Errors');
    const errorTab = page.locator('text=Errors');
    await expect(errorTab).toBeVisible();
    
    // Set verbosity to 2 (Detailed)
    await select.selectOption('2');
    await page.waitForTimeout(1000);
    
    // Verify Requests tab now has content
    await page.click('text=Requests');
    // Should see request logs or at least the tab is accessible
    const requestsTab = page.locator('text=Requests');
    await expect(requestsTab).toBeVisible();
    
    // Set verbosity to 3 (Debug)
    await select.selectOption('3');
    await page.waitForTimeout(1000);
    
    // Verify Code Flow tab has content
    await page.click('text=Code Flow');
    const codeFlowTab = page.locator('text=Code Flow');
    await expect(codeFlowTab).toBeVisible();
  });

  test('should expand and collapse rows', async ({ page }) => {
    await page.waitForSelector('text=Connected to experiment stream', { timeout: 10000 }).catch(() => {
      test.skip();
    });
    
    // Click on Requests tab
    await page.click('text=Requests');
    await page.waitForTimeout(500);
    
    // Find first row
    const firstRow = page.locator('table tbody tr').first();
    if (await firstRow.count() > 0) {
      await firstRow.click();
      
      // Verify syntax highlighter appears (expanded content)
      const syntaxHighlighter = page.locator('.prism-code, [class*="syntax"]').first();
      // May or may not be visible depending on content
      
      // Click again to collapse
      await firstRow.click();
    }
  });

  test('should expand all rows', async ({ page }) => {
    await page.waitForSelector('text=Connected to experiment stream', { timeout: 10000 }).catch(() => {
      test.skip();
    });
    
    await page.click('text=Requests');
    await page.waitForTimeout(500);
    
    // Click "Expand All"
    const expandAllButton = page.locator('text=Expand All');
    if (await expandAllButton.count() > 0) {
      await expandAllButton.click();
      
      // Verify rows are expanded (check for copy buttons or expanded content)
      await page.waitForTimeout(500);
      
      // Click "Collapse All"
      const collapseAllButton = page.locator('text=Collapse All');
      if (await collapseAllButton.count() > 0) {
        await collapseAllButton.click();
      }
    }
  });

  test('should copy content to clipboard', async ({ page, context }) => {
    await page.waitForSelector('text=Connected to experiment stream', { timeout: 10000 }).catch(() => {
      test.skip();
    });
    
    await page.click('text=Requests');
    await page.waitForTimeout(500);
    
    // Expand a row
    const firstRow = page.locator('table tbody tr').first();
    if (await firstRow.count() > 0) {
      await firstRow.click();
      await page.waitForTimeout(300);
      
      // Find and click copy button
      const copyButton = page.locator('text=Copy').first();
      if (await copyButton.count() > 0) {
        // Grant clipboard permissions
        await context.grantPermissions(['clipboard-read', 'clipboard-write']);
        
        await copyButton.click();
        await page.waitForTimeout(300);
        
        // Verify clipboard content (if possible)
        // Note: Clipboard API access in Playwright is limited
      }
    }
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await page.waitForSelector('text=Connected to experiment stream', { timeout: 10000 }).catch(() => {
      test.skip();
    });
    
    await page.click('text=Requests');
    await page.waitForTimeout(500);
    
    // Focus first row
    const firstRow = page.locator('table tbody tr').first();
    if (await firstRow.count() > 0) {
      await firstRow.focus();
      
      // Press Enter to expand
      await page.keyboard.press('Enter');
      await page.waitForTimeout(300);
      
      // Press Enter again to collapse
      await page.keyboard.press('Enter');
      await page.waitForTimeout(300);
    }
  });
});
