import { test, expect } from '@playwright/test';

test.describe('Code Flow Panel', () => {
  test('should display code-flow events when verbosity=3', async ({ page }) => {
    // Navigate to monitor page
    await page.goto('/experiments/test-id/monitor');
    
    // Click code-flow tab
    await page.click('button:has-text("Code Flow")');
    
    // Wait for code-flow events (mock WebSocket)
    await page.evaluate(() => {
      // Simulate code-flow WebSocket message
      window.dispatchEvent(new CustomEvent('websocket-message', {
        detail: {
          type: 'code_flow',
          event_type: 'strategy_selection',
          strategy: 'roleplay_injection',
          reasoning: 'Initial strategy',
          iteration: 1,
          timestamp: new Date().toISOString()
        }
      }));
    });
    
    // Verify event is displayed
    await expect(page.locator('text=STRATEGY SELECTION')).toBeVisible();
    await expect(page.locator('text=roleplay_injection')).toBeVisible();
  });
  
  test('should show empty state when no events', async ({ page }) => {
    await page.goto('/experiments/test-id/monitor');
    await page.click('button:has-text("Code Flow")');
    
    // Verify empty state
    await expect(page.locator('text=No code-flow events yet')).toBeVisible();
    await expect(page.locator('text=verbosity=3')).toBeVisible();
  });
});
