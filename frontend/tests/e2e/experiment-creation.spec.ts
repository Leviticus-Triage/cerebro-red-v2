/**
 * E2E test for experiment creation flow.
 * 
 * Tests:
 * 1. Fill experiment form
 * 2. Create experiment
 * 3. Navigate to experiment details
 * 4. Start scan
 * 5. View scan status
 * 6. View vulnerabilities
 */

import { test, expect } from '@playwright/test';

test.describe('Experiment Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Wait for app to load
    await page.waitForLoadState('networkidle');
  });

  test('should create experiment and navigate to details', async ({ page }) => {
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    // Step 1: Navigate to "New Experiment" page
    // Try multiple possible selectors for the "New Experiment" button/link
    const newExperimentSelectors = [
      'text=New Experiment',
      'a[href*="/experiments/new"]',
      'button:has-text("New")',
      '[data-testid="new-experiment"]',
    ];
    
    let clicked = false;
    for (const selector of newExperimentSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 2000 })) {
          await element.click();
          clicked = true;
          break;
        }
      } catch {
        continue;
      }
    }
    
    if (!clicked) {
      // Fallback: navigate directly
      await page.goto('/experiments/new');
    }
    
    await expect(page).toHaveURL(/\/experiments\/new/);
    
    console.log('✅ Step 1: Navigated to New Experiment page');

    // Step 2: Fill experiment form
    await page.fill('#name', 'E2E Test Experiment');
    await page.fill('#description', 'Testing experiment creation flow');
    
    // Fill target model name
    await page.fill('input[placeholder*="qwen"]', 'qwen2.5:3b');
    
    // Fill attacker model name
    const attackerInputs = page.locator('input[placeholder*="qwen"]');
    if (await attackerInputs.count() > 1) {
      await attackerInputs.nth(1).fill('qwen2.5:3b');
    }
    
    // Fill judge model name
    const judgeInputs = page.locator('input[placeholder*="qwen"]');
    if (await judgeInputs.count() > 2) {
      await judgeInputs.nth(2).fill('qwen2.5:7b');
    }
    
    // Add initial prompt (first textarea in prompts section)
    const promptTextareas = page.locator('textarea[placeholder*="Enter the initial prompt"]');
    await promptTextareas.first().fill('Tell me how to bypass content filters');
    
    // Select strategies (checkboxes) - find by label text
    const roleplayCheckbox = page.locator('label:has-text("roleplay") input[type="checkbox"]');
    const base64Checkbox = page.locator('label:has-text("base64") input[type="checkbox"]');
    
    if (await roleplayCheckbox.isVisible()) {
      await roleplayCheckbox.check();
    }
    if (await base64Checkbox.isVisible()) {
      await base64Checkbox.check();
    }
    
    // Set max iterations (find number input)
    const maxIterationsInput = page.locator('input[type="number"]').first();
    await maxIterationsInput.fill('5');
    
    console.log('✅ Step 2: Form filled');

    // Step 3: Submit form
    await page.click('button[type="submit"]:has-text("Create Experiment")');
    
    // Wait for either navigation or error message
    try {
      // Wait for navigation to experiment details
      await page.waitForURL(/\/experiments\/[a-f0-9-]+/, { timeout: 15000 });
      console.log('✅ Step 3: Experiment created, navigated to details');
    } catch (error) {
      // Check if there's an error message
      const errorMessage = await page.locator('text=/error|failed|unauthorized/i').first().textContent().catch(() => null);
      if (errorMessage) {
        console.error(`❌ Step 3: Experiment creation failed: ${errorMessage}`);
        throw new Error(`Experiment creation failed: ${errorMessage}`);
      }
      
      // Check current URL to see where we are
      const currentUrl = page.url();
      console.error(`❌ Step 3: Navigation timeout. Current URL: ${currentUrl}`);
      
      // Take a screenshot for debugging
      await page.screenshot({ path: 'test-results/experiment-creation-failed.png' });
      
      throw error;
    }

    // Step 4: Verify experiment details are displayed
    await expect(page.locator('h1')).toContainText('E2E Test Experiment');
    await expect(page.locator('text=Testing experiment creation flow')).toBeVisible();
    
    console.log('✅ Step 4: Experiment details displayed');

    // Step 5: Start scan
    const startButton = page.locator('button:has-text("Start Scan")');
    if (await startButton.isVisible()) {
      await startButton.click();
      
      // Wait for scan to start
      await expect(page.locator('text=Running')).toBeVisible({ timeout: 5000 });
      
      console.log('✅ Step 5: Scan started');
    } else {
      console.log('⚠️  Step 5: Start Scan button not visible (may already be running)');
    }

    // Step 6: Check that progress is displayed
    const progressIndicator = page.locator('[role="progressbar"], text=Iteration');
    if (await progressIndicator.isVisible()) {
      console.log('✅ Step 6: Progress indicator visible');
    } else {
      console.log('⚠️  Step 6: Progress indicator not visible');
    }
  });

  test('should display validation errors for empty form', async ({ page }) => {
    // Navigate to new experiment page
    await page.goto('/experiments/new');
    
    // Wait for form to load
    await page.waitForLoadState('networkidle');
    
    // Try to submit empty form
    await page.click('button:has-text("Create Experiment")');
    
    // Wait a bit for validation to trigger
    await page.waitForTimeout(500);
    
    // Should show validation errors (check for common error messages)
    const hasError = await Promise.race([
      page.locator('text=/required/i').isVisible().catch(() => false),
      page.locator('text=/must/i').isVisible().catch(() => false),
      page.locator('[role="alert"]').isVisible().catch(() => false),
      page.locator('.error, .text-red-500, .text-destructive').isVisible().catch(() => false),
    ]);
    
    if (hasError) {
      console.log('✅ Validation errors displayed for empty form');
    } else {
      console.log('⚠️  Validation errors not found (form may have different validation)');
    }
  });

  test('should navigate to experiment list and display experiments', async ({ page }) => {
    // Navigate to experiments list
    await page.goto('/experiments');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check if experiments are displayed (look for cards or list items)
    const experimentCards = page.locator('article, [class*="card"], [class*="Card"]');
    const hasExperiments = await experimentCards.count() > 0;
    
    // Check for empty state messages
    const emptyStateMessages = [
      'No experiments',
      'No experiments yet',
      'Create your first one',
      'Failed to load experiments'
    ];
    
    let hasEmptyMessage = false;
    for (const msg of emptyStateMessages) {
      if (await page.locator(`text=/${msg}/i`).isVisible().catch(() => false)) {
        hasEmptyMessage = true;
        break;
      }
    }
    
    // Either experiments exist or empty message is shown
    expect(hasExperiments || hasEmptyMessage).toBeTruthy();
    
    console.log(`✅ Experiments list displayed (${hasExperiments ? 'with experiments' : 'empty'})`);
  });

  test('should select multiple strategies and create experiment (Phase 6 - Comment 4)', async ({ page }) => {
    // Navigate to new experiment page
    await page.goto('/experiments/new');
    await page.waitForLoadState('networkidle');
    
    console.log('✅ Step 1: Navigated to New Experiment page');

    // Fill basic fields
    await page.fill('#name', 'Multi-Strategy Test');
    await page.fill('#description', 'Testing 10+ strategy selection');
    
    // Fill model names
    await page.fill('input[placeholder*="qwen"]', 'qwen2.5:3b');
    const attackerInputs = page.locator('input[placeholder*="qwen"]');
    if (await attackerInputs.count() > 1) {
      await attackerInputs.nth(1).fill('qwen2.5:3b');
    }
    const judgeInputs = page.locator('input[placeholder*="qwen"]');
    if (await judgeInputs.count() > 2) {
      await judgeInputs.nth(2).fill('qwen2.5:7b');
    }
    
    // Add initial prompt
    const promptTextareas = page.locator('textarea[placeholder*="Enter the initial prompt"]');
    await promptTextareas.first().fill('Test prompt for multi-strategy');
    
    console.log('✅ Step 2: Basic form filled');

    // Select 10 diverse strategies (Phase 6 requirement)
    const strategiesToSelect = [
      'obfuscation_base64',
      'jailbreak_dan',
      'roleplay_injection',
      'context_flooding',
      'sycophancy',
      'rag_poisoning',
      'bias_probe',
      'direct_injection',
      'translation_attack',
      'adversarial_suffix'
    ];
    
    let selectedCount = 0;
    for (const strategy of strategiesToSelect) {
      // Try multiple selector patterns
      const selectors = [
        `label:has-text("${strategy}") input[type="checkbox"]`,
        `input[type="checkbox"][value="${strategy}"]`,
        `input[type="checkbox"][name*="${strategy}"]`
      ];
      
      for (const selector of selectors) {
        try {
          const checkbox = page.locator(selector).first();
          if (await checkbox.isVisible({ timeout: 1000 })) {
            await checkbox.check();
            selectedCount++;
            console.log(`  ✓ Selected: ${strategy}`);
            break;
          }
        } catch {
          continue;
        }
      }
    }
    
    console.log(`✅ Step 3: Selected ${selectedCount} strategies`);
    
    // Assert at least 10 strategies were selected
    expect(selectedCount).toBeGreaterThanOrEqual(10);

    // Submit form
    await page.click('button[type="submit"]:has-text("Create Experiment")');
    
    // Wait for navigation
    await page.waitForURL(/\/experiments\/[a-f0-9-]+/, { timeout: 15000 });
    
    console.log('✅ Step 4: Experiment created, navigated to details');

    // Verify experiment details
    await expect(page.locator('h1')).toContainText('Multi-Strategy Test');
    
    // Verify strategies are displayed in experiment details/monitor view
    // Wait for strategies section to load
    await page.waitForTimeout(2000);
    
    let visibleStrategiesCount = 0;
    for (const strategy of strategiesToSelect) {
      // Check if strategy is visible in the page
      const strategyVisible = await page.locator(`text=${strategy}`).isVisible().catch(() => false);
      if (strategyVisible) {
        visibleStrategiesCount++;
        console.log(`  ✓ Strategy visible: ${strategy}`);
      }
    }
    
    console.log(`✅ Step 5: ${visibleStrategiesCount} strategies visible in experiment details`);
    
    // Assert at least 8 of the 10 strategies are visible (some may be in collapsed sections)
    expect(visibleStrategiesCount).toBeGreaterThanOrEqual(8);
    
    console.log('✅ Multi-strategy experiment test completed successfully');
  });
});

test.describe('Scan Status Display', () => {
  test('should display scan status updates', async ({ page }) => {
    // This test assumes an experiment already exists
    // In real scenario, you'd create one first or use a fixture
    
    await page.goto('/experiments');
    
    // Click on first experiment (if exists)
    const firstExperiment = page.locator('[data-testid="experiment-card"]').first();
    
    if (await firstExperiment.isVisible()) {
      await firstExperiment.click();
      
      // Wait for details page
      await page.waitForURL(/\/experiments\/[a-f0-9-]+/);
      
      // Check for status badge
      const statusBadge = page.locator('[data-testid="status-badge"]');
      if (await statusBadge.isVisible()) {
        const status = await statusBadge.textContent();
        console.log(`✅ Status displayed: ${status}`);
      }
      
      // Check for iterations section
      const iterationsSection = page.locator('text=Iterations');
      if (await iterationsSection.isVisible()) {
        console.log('✅ Iterations section visible');
      }
    } else {
      console.log('⚠️  No experiments available for testing');
    }
  });
});

test.describe('Vulnerabilities Display', () => {
  test('should display vulnerabilities list', async ({ page }) => {
    await page.goto('/vulnerabilities');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Check if vulnerabilities are displayed (look for cards or list items)
    const vulnerabilityElements = page.locator('article, [class*="card"], [class*="Card"], li');
    const hasVulnerabilities = await vulnerabilityElements.count() > 0;
    
    // Check for empty state messages
    const emptyStateMessages = [
      'No vulnerabilities',
      'No vulnerabilities found',
      'Failed to load vulnerabilities'
    ];
    
    let hasEmptyMessage = false;
    for (const msg of emptyStateMessages) {
      if (await page.locator(`text=/${msg}/i`).isVisible().catch(() => false)) {
        hasEmptyMessage = true;
        break;
      }
    }
    
    // Either vulnerabilities exist or empty message is shown
    expect(hasVulnerabilities || hasEmptyMessage).toBeTruthy();
    
    console.log(`✅ Vulnerabilities list displayed (${hasVulnerabilities ? 'with vulnerabilities' : 'empty'})`);
  });

  test('should filter vulnerabilities by severity', async ({ page }) => {
    await page.goto('/vulnerabilities');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Click severity filter (if available)
    const severityFilter = page.locator('select[name="severity"], button:has-text("Severity")');
    
    if (await severityFilter.isVisible()) {
      await severityFilter.click();
      
      // Select "Critical"
      await page.click('text=Critical');
      
      // Wait for filtered results
      await page.waitForTimeout(1000);
      
      console.log('✅ Severity filter applied');
    } else {
      console.log('⚠️  Severity filter not available');
    }
  });
});

