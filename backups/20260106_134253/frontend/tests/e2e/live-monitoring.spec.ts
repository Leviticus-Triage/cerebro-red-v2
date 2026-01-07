import { test, expect } from '@playwright/test';

test.describe('Live Monitoring - LLM I/O Visibility', () => {
  test('should display attacker LLM requests and responses', async ({ page }) => {
    // Navigate to experiment monitor
    await page.goto('/experiments/test-experiment-id/monitor');
    
    // Wait for WebSocket connection
    await expect(page.locator('text=Connected to experiment stream')).toBeVisible();
    
    // Wait for attacker LLM request log
    await expect(page.locator('text=/ATTACKER Request/')).toBeVisible({ timeout: 10000 });
    
    // Verify request has role badge
    const attackerRequest = page.locator('[data-testid="log-entry"]').filter({ hasText: 'ATTACKER Request' });
    await expect(attackerRequest.locator('.role-badge')).toHaveText('ATTACKER');
    
    // Click to expand
    await attackerRequest.click();
    
    // Verify full prompt is visible
    await expect(page.locator('text=Full Prompt:')).toBeVisible();
    await expect(page.locator('pre').filter({ hasText: /Generate an improved prompt/ })).toBeVisible();
    
    // Wait for attacker LLM response
    await expect(page.locator('text=/ATTACKER Response/')).toBeVisible({ timeout: 10000 });
    
    // Verify response has latency and tokens
    const attackerResponse = page.locator('[data-testid="log-entry"]').filter({ hasText: 'ATTACKER Response' });
    await expect(attackerResponse).toContainText(/\d+ms/);  // Latency
    await expect(attackerResponse).toContainText(/\d+ tokens/);  // Tokens
    
    // Expand response
    await attackerResponse.click();
    
    // Verify full response is visible
    await expect(page.locator('text=Full Response:')).toBeVisible();
    await expect(page.locator('pre').filter({ hasText: /Rephrased prompt/ })).toBeVisible();
  });
  
  test('should display target and judge LLM interactions', async ({ page }) => {
    await page.goto('/experiments/test-experiment-id/monitor');
    
    // Wait for target request
    await expect(page.locator('text=/TARGET Request/')).toBeVisible({ timeout: 10000 });
    
    // Wait for target response
    await expect(page.locator('text=/TARGET Response/')).toBeVisible({ timeout: 10000 });
    
    // Wait for judge request
    await expect(page.locator('text=/JUDGE Request/')).toBeVisible({ timeout: 10000 });
    
    // Wait for judge evaluation
    await expect(page.locator('text=/Judge Score:/')).toBeVisible({ timeout: 10000 });
    
    // Verify judge score is displayed
    await expect(page.locator('text=/Score: \d+\.\d+\/10/')).toBeVisible();
  });
  
  test('should filter logs by LLM type', async ({ page }) => {
    await page.goto('/experiments/test-experiment-id/monitor');
    
    // Wait for logs to appear
    await expect(page.locator('[data-testid="log-entry"]')).toHaveCount(10, { timeout: 10000 });
    
    // Click LLM filter
    await page.click('button:has-text("LLM")');
    
    // Verify only LLM logs are visible
    const visibleLogs = page.locator('[data-testid="log-entry"]:visible');
    await expect(visibleLogs).toHaveCount(6);  // Only llm_request and llm_response
    
    // Verify no attack/judge logs are visible
    await expect(page.locator('text=/Attack mutation/').first()).not.toBeVisible();
  });
  
  test('should show error when LLM call fails', async ({ page }) => {
    await page.goto('/experiments/test-experiment-id/monitor');
    
    // Wait for error log
    await expect(page.locator('text=/Error from attacker/')).toBeVisible({ timeout: 10000 });
    
    // Verify error has red border
    const errorLog = page.locator('[data-testid="log-entry"]').filter({ hasText: 'Error from attacker' });
    await expect(errorLog).toHaveClass(/border-l-rose-600/);
  });
});
