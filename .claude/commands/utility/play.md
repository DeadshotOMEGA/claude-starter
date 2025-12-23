---
description: Run or create Playwright E2E tests for web applications
argument-hint: <test-description or file>
allowed-tools: Read, Write, Edit, Bash(bunx playwright:*, docker:*)
---

# Playwright Test Runner

**Argument:** $ARGUMENTS (test description or specific test file)

## Your Task

Run or create Playwright E2E tests based on the user's request: **$ARGUMENTS**

## Pre-flight Checks

1. **Ensure services are running** (if testing sentinel project):
   ```bash
   # Check if docker services are up
   docker ps | grep -q sentinel-postgres || docker compose -f ~/projects/sentinel/docker-compose.yml up -d

   # Check if dev servers are running by testing ports
   # Backend: 3001, Frontend: 5173, Kiosk: 5174, TV-Display: 5175
   ```

2. **If services aren't running**, start them:
   ```bash
   ~/projects/sentinel/scripts/start-all.sh
   ```
   Wait for health checks before proceeding.

## Interpret the Request

Parse "$ARGUMENTS" to determine:

1. **What to test**: Which feature/flow/page?
   - "visitor check-in" → kiosk visitor flow
   - "dashboard" → frontend admin dashboard
   - "tv-display" → tv-display page
   - "member check-in" → kiosk member RFID flow

2. **Specific assertions**: What should be verified?
   - "confirm results on frontend" → check frontend reflects changes
   - "verify websocket updates" → check real-time sync

3. **Test scope**:
   - Single page test vs multi-page flow
   - Single app vs cross-app verification

## Execution Strategy

### If existing tests match the request:
```bash
cd ~/projects/sentinel
bunx playwright test -g "relevant pattern" --project=chromium
```

### If new test needed:
1. Create test file in `~/projects/sentinel/tests/e2e/`
2. Use proper selectors (getByRole, getByTestId preferred)
3. Include cross-app verification if requested
4. Run the new test

## Test File Locations

```
~/projects/sentinel/tests/e2e/
├── kiosk/           # Kiosk-specific tests
├── frontend/        # Admin dashboard tests
├── tv-display/      # TV display tests
└── flows/           # Cross-app user flows
```

## Port Reference

| App | Port | Base URL |
|-----|------|----------|
| Backend API | 3000 | http://localhost:3000 |
| Frontend (Admin) | 5173 | http://localhost:5173 |
| Kiosk | 5174 | http://localhost:5174 |
| TV Display | 5175 | http://localhost:5175 |

## Example Test Patterns

**Kiosk visitor check-in:**
```typescript
test('visitor can check in at kiosk', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.getByRole('button', { name: /visitor/i }).click();
  await page.getByLabel('Name').fill('John Doe');
  await page.getByRole('button', { name: /submit/i }).click();
  await expect(page.getByText(/welcome/i)).toBeVisible();
});
```

**Cross-app verification (kiosk → frontend):**
```typescript
test('visitor check-in appears on dashboard', async ({ browser }) => {
  const kioskContext = await browser.newContext();
  const adminContext = await browser.newContext();

  const kioskPage = await kioskContext.newPage();
  const adminPage = await adminContext.newPage();

  // Check in on kiosk
  await kioskPage.goto('http://localhost:5174');
  // ... perform check-in

  // Verify on admin dashboard
  await adminPage.goto('http://localhost:5173');
  await expect(adminPage.getByText('John Doe')).toBeVisible();
});
```

## Output

After running tests:
1. Report pass/fail summary
2. For failures: show what failed and why
3. If HTML report generated: `bunx playwright show-report`
