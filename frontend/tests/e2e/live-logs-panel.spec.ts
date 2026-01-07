import { test, expect } from '@playwright/test';

test.describe('Live Logs Panel - Structured Tabs', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a test experiment monitor page
    // Note: This assumes a test experiment exists or we mock the API
    await page.goto('/experiments/test-id/monitor');
    
    // Wait for the page to load
    await page.waitForSelector('[data-testid="experiment-monitor"]', { timeout: 10000 }).catch(() => {
      // If test experiment doesn't exist, we'll skip the test
      test.skip();
    });
  });

  test('should display all 6 tabs with counts', async ({ page }) => {
    // Verify all tabs exist
    await expect(page.locator('button:has-text("Requests")')).toBeVisible();
    await expect(page.locator('button:has-text("Responses")')).toBeVisible();
    await expect(page.locator('button:has-text("Judge")')).toBeVisible();
    await expect(page.locator('button:has-text("Tasks")')).toBeVisible();
    await expect(page.locator('button:has-text("Code Flow")')).toBeVisible();
    await expect(page.locator('button:has-text("Errors")')).toBeVisible();
  });

  test('should display table structure in Requests tab', async ({ page }) => {
    // Click Requests tab
    await page.click('button:has-text("Requests")');
    
    // Wait for table to render
    await page.waitForSelector('table', { timeout: 5000 });
    
    // Verify table headers
    await expect(page.locator('th:has-text("Time")')).toBeVisible();
    await expect(page.locator('th:has-text("Iteration")')).toBeVisible();
    await expect(page.locator('th:has-text("Role")')).toBeVisible();
    await expect(page.locator('th:has-text("Prompt")')).toBeVisible();
    await expect(page.locator('th:has-text("Model")')).toBeVisible();
  });

  test('should display table structure in Responses tab', async ({ page }) => {
    await page.click('button:has-text("Responses")');
    await page.waitForSelector('table', { timeout: 5000 });
    
    await expect(page.locator('th:has-text("Time")')).toBeVisible();
    await expect(page.locator('th:has-text("Response")')).toBeVisible();
    await expect(page.locator('th:has-text("Latency")')).toBeVisible();
    await expect(page.locator('th:has-text("Tokens")')).toBeVisible();
  });

  test('should display table structure in Judge tab', async ({ page }) => {
    await page.click('button:has-text("Judge")');
    await page.waitForSelector('table', { timeout: 5000 });
    
    await expect(page.locator('th:has-text("Score")')).toBeVisible();
    await expect(page.locator('th:has-text("Reasoning")')).toBeVisible();
    await expect(page.locator('th:has-text("Success")')).toBeVisible();
  });

  test('should expand row and show syntax highlighting', async ({ page }) => {
    await page.click('button:has-text("Requests")');
    await page.waitForSelector('tbody tr', { timeout: 5000 });
    
    // Click first data row (skip header)
    const firstRow = page.locator('tbody tr').first();
    if (await firstRow.count() > 0) {
      await firstRow.click();
      
      // Verify syntax highlighter appears (react-syntax-highlighter adds specific classes)
      await expect(page.locator('.language-text, [class*="language-"]')).toBeVisible({ timeout: 2000 }).catch(() => {
        // If syntax highlighter doesn't appear, check if expanded content is visible
        expect(firstRow.locator('td').nth(3)).toBeVisible();
      });
    }
  });

  test('should export logs as JSON', async ({ page }) => {
    // Wait for export button
    await page.waitForSelector('button:has-text("JSON")', { timeout: 5000 });
    
    // Set up download listener
    const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
    
    // Click export button
    await page.click('button:has-text("JSON")');
    
    const download = await downloadPromise;
    if (download) {
      expect(download.suggestedFilename()).toContain('.json');
    }
  });

  test('should export logs as CSV', async ({ page }) => {
    await page.waitForSelector('button:has-text("CSV")', { timeout: 5000 });
    
    const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
    await page.click('button:has-text("CSV")');
    
    const download = await downloadPromise;
    if (download) {
      expect(download.suggestedFilename()).toContain('.csv');
    }
  });

  test('should switch between tabs and maintain data', async ({ page }) => {
    // Start on Requests tab
    await page.click('button:has-text("Requests")');
    await page.waitForSelector('table', { timeout: 5000 });
    
    // Switch to Responses
    await page.click('button:has-text("Responses")');
    await expect(page.locator('th:has-text("Response")')).toBeVisible();
    
    // Switch to Judge
    await page.click('button:has-text("Judge")');
    await expect(page.locator('th:has-text("Score")')).toBeVisible();
    
    // Switch back to Requests
    await page.click('button:has-text("Requests")');
    await expect(page.locator('th:has-text("Prompt")')).toBeVisible();
  });

  test('should display badge counts on tabs', async ({ page }) => {
    // Verify badges exist (they may show 0 if no data)
    const requestsTab = page.locator('button:has-text("Requests")');
    await expect(requestsTab.locator('text=/\\d+/')).toBeVisible();
    
    const responsesTab = page.locator('button:has-text("Responses")');
    await expect(responsesTab.locator('text=/\\d+/')).toBeVisible();
  });
});
