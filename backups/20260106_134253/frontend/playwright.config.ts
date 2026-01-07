import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1, // Retry once locally for flaky tests
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  // Global timeout settings
  timeout: 60000, // 60s per test (LLM operations can be slow)
  expect: {
    timeout: 10000, // 10s for assertions
  },
  
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    
    // Action timeouts
    actionTimeout: 15000, // 15s for clicks, fills, etc.
    navigationTimeout: 30000, // 30s for page navigation
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120000, // 2 minutes to start dev server
  },
});

