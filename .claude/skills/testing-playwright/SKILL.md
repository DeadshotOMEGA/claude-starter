---
name: testing-playwright
description: Run and write end-to-end browser tests with Playwright. Use when testing web applications, verifying UI functionality, checking user flows, or when proactive testing is beneficial after code changes. Triggers on "test", "e2e", "playwright", "browser test", "verify the UI", "check the page".
---

# Testing with Playwright

Run E2E tests for local web applications using Playwright.

## Contents

- [Commands](#commands)
- [When to Run Tests Proactively](#when-to-run-tests-proactively)
- [Writing Tests](#writing-tests)
- [Common Assertions](#common-assertions)
- [Handling Async Operations](#handling-async-operations)
- [Server Lifecycle Management](#server-lifecycle-management)
- [Manual Browser Automation](#manual-browser-automation)
- [Debugging](#debugging)

## Commands

```bash
# Run all tests (headless)
bunx playwright test

# Run specific test file
bunx playwright test tests/example.spec.ts

# Run tests with visible browser
bunx playwright test --headed

# Run tests in specific browser
bunx playwright test --project=chromium

# Run with UI mode (interactive)
bunx playwright test --ui

# Show HTML report after tests
bunx playwright show-report
```

## When to Run Tests Proactively

Run tests **without asking** when:
- Implementing or modifying UI components
- Fixing bugs that affect user-visible behavior
- After completing a feature that has existing tests
- Before committing changes to tested areas

## Writing Tests

Test files go in `tests/` directory with `.spec.ts` extension.

```typescript
import { test, expect } from '@playwright/test';

test('descriptive test name', async ({ page }) => {
  // Navigate
  await page.goto('http://localhost:3000');

  // Interact
  await page.getByRole('button', { name: 'Submit' }).click();
  await page.getByLabel('Email').fill('user@example.com');

  // Assert
  await expect(page.getByText('Success')).toBeVisible();
  await expect(page).toHaveURL(/dashboard/);
});
```

### Locator Priority

Prefer these locators (most reliable first):
1. `getByRole()` - accessibility roles
2. `getByLabel()` - form labels
3. `getByText()` - visible text
4. `getByTestId()` - data-testid attributes
5. `locator()` - CSS/XPath (last resort)

### Test Organization

```typescript
test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('scenario one', async ({ page }) => {
    // ...
  });

  test('scenario two', async ({ page }) => {
    // ...
  });
});
```

## Common Assertions

```typescript
// Visibility
await expect(element).toBeVisible();
await expect(element).toBeHidden();

// Text content
await expect(element).toHaveText('exact text');
await expect(element).toContainText('partial');

// Attributes
await expect(element).toHaveAttribute('href', '/path');
await expect(input).toHaveValue('input value');

// State
await expect(element).toBeEnabled();
await expect(checkbox).toBeChecked();

// URL
await expect(page).toHaveURL(/pattern/);
await expect(page).toHaveTitle('Page Title');
```

## Handling Async Operations

```typescript
// Wait for element
await page.waitForSelector('.loading-complete');

// Wait for navigation
await page.waitForURL('**/dashboard');

// Wait for network idle
await page.waitForLoadState('networkidle');

// Custom wait
await expect(element).toBeVisible({ timeout: 10000 });
```

## Server Lifecycle Management

For testing local apps that require server startup, use `scripts/with_server.py`.

**Run `--help` first** to see usage:
```bash
python scripts/with_server.py --help
```

### Single Server

```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

### Multiple Servers (backend + frontend)

```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

The script:
- Starts servers and waits for ports to be ready
- Runs your command after all servers are up
- Cleans up servers when done (even on failure)

### Alternative: playwright.config.ts webServer

Configure automatic server startup in `playwright.config.ts`:
```typescript
export default defineConfig({
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
});
```

## Manual Browser Automation

For one-off automation tasks (not test suites), write native Python Playwright scripts.

### Decision Tree

```
Task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         └─ Write Playwright script using selectors
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Use scripts/with_server.py + automation script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

### Reconnaissance Pattern

For dynamic apps, inspect rendered DOM before acting:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')

    # CRITICAL: Wait for JS to execute
    page.wait_for_load_state('networkidle')

    # Inspect rendered DOM
    page.screenshot(path='/tmp/inspect.png', full_page=True)
    content = page.content()
    buttons = page.locator('button').all()

    # Execute actions using discovered selectors
    # ...

    browser.close()
```

### Common Pitfall

❌ **Don't** inspect DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Debugging

```bash
# Run with trace on failure
bunx playwright test --trace on

# Debug specific test
bunx playwright test --debug tests/example.spec.ts

# View trace from failed run
bunx playwright show-trace test-results/*/trace.zip
```

## Configuration Reference

Key settings in `playwright.config.ts`:
- `testDir`: Test file location (`./tests`)
- `baseURL`: Default URL for `page.goto('')`
- `projects`: Browser configurations
- `webServer`: Auto-start dev server before tests

## Example Files

See `examples/` for common patterns:
- `element_discovery.py` - Discovering buttons, links, and inputs
- `static_html_automation.py` - Using file:// URLs for local HTML
- `console_logging.py` - Capturing console logs during automation
