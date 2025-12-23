---
name: applying-testing-patterns
description: Comprehensive testing patterns, frameworks, and CI/CD templates. Use when implementing test suites, configuring test runners, or setting up testing infrastructure.
---

# Applying Testing Patterns

Comprehensive testing frameworks, utilities, and CI/CD templates for test automation.

## Contents

- [Testing Strategy](#testing-strategy)
- [Test Suite Manager](#test-suite-manager)
- [Test Patterns & Utilities](#test-patterns--utilities)
- [Performance Testing](#performance-testing)
- [Configuration Templates](#configuration-templates)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Testing Strategy

### Test Pyramid
- **Unit tests**: 70% - Fast, isolated, test individual functions/methods
- **Integration tests**: 20% - Test component interactions, database, services
- **E2E tests**: 10% - Test complete user flows through the application

### Testing Types
- **Functional**: Feature correctness and requirements
- **Non-functional**: Performance, security, accessibility
- **Regression**: Prevent previously fixed bugs
- **Smoke**: Critical path verification after deployment

### Quality Gates
- **Coverage thresholds**: 80% for branches, functions, lines, statements
- **Performance benchmarks**: Response times, throughput targets
- **Security checks**: Vulnerability scanning, audit compliance

### Risk Assessment
- Identify critical paths (payment, auth, data access)
- Analyze failure impact (data loss, security breach, downtime)
- Prioritize test coverage for high-risk areas

## Test Suite Manager

Comprehensive test orchestration and reporting framework.

See [TestSuiteManager.md](TestSuiteManager.md) for full implementation.

**Key Features:**
- Orchestrates unit, integration, and E2E tests
- Manages test environment setup/teardown
- Generates comprehensive test reports
- Coverage analysis and threshold enforcement
- Automated recommendations based on results

**Usage:**
```javascript
const { TestSuiteManager } = require('./test-framework/test-suite-manager');

const manager = new TestSuiteManager({
  testDirectory: './tests',
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 }
  }
});

await manager.runFullTestSuite();
```

## Test Patterns & Utilities

Reusable patterns for common testing scenarios.

See [TestPatterns.md](TestPatterns.md) for full implementation.

### Page Object Model
Encapsulate page interactions for E2E tests:
```javascript
const loginPage = TestPatterns.createPageObject(page, {
  emailInput: '#email',
  passwordInput: '#password',
  submitButton: '[type="submit"]'
});

await loginPage.emailInput.fill('user@example.com');
await loginPage.passwordInput.fill('password');
await loginPage.submitButton.click();
```

### Test Data Factory
Generate test data with controlled variation:
```javascript
const userFactory = TestPatterns.createTestDataFactory({
  id: () => Math.random().toString(36).substring(7),
  email: () => `user-${Date.now()}@example.com`,
  name: 'Test User',
  role: 'user'
});

const user = userFactory.build({ role: 'admin' });
const users = userFactory.buildList(10);
```

### Mock Service Factory
Create and manage service mocks:
```javascript
const emailService = TestPatterns.createMockService('emailService', [
  'sendEmail',
  'sendBatch',
  'verifyAddress'
]);

emailService.sendEmail.mockResolvedValue({ id: '123', status: 'sent' });
```

### Database Test Helpers
Manage test database state:
```javascript
const dbHelpers = TestPatterns.createDatabaseTestHelpers(db);

await dbHelpers.cleanTables(['users', 'posts', 'comments']);
await dbHelpers.seedTable('users', [{ id: 1, email: 'test@example.com' }]);
const lastUser = await dbHelpers.getLastInserted('users');
```

### API Test Helpers
HTTP client for API testing:
```javascript
const api = TestPatterns.createAPITestHelpers('http://localhost:3000');

const response = await api
  .withAuth(authToken)
  .post('/api/users', { email: 'test@example.com' });

expect(response.status).toBe(201);
```

## Performance Testing

Load testing and performance analysis framework.

See [PerformanceTestFramework.md](PerformanceTestFramework.md) for full implementation.

**Features:**
- Concurrent user simulation with ramp-up
- Response time percentile analysis (p50, p90, p95, p99)
- Throughput and error rate tracking
- Automated performance recommendations

**Usage:**
```javascript
const { PerformanceTestFramework } = require('./test-framework/performance-testing');

const perfTest = new PerformanceTestFramework();

const results = await perfTest.runLoadTest({
  endpoint: 'http://localhost:3000/api/users',
  method: 'GET',
  concurrent: 50,
  duration: 60000,
  rampUp: 10000
});

console.log(`Average response: ${results.responseTime.mean}ms`);
console.log(`95th percentile: ${results.responseTime.p95}ms`);
console.log(`Throughput: ${results.summary.throughput} req/s`);
```

## Configuration Templates

### Jest Configuration
Unit and integration test configuration:

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/*.(test|spec).+(ts|tsx|js)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/test/**/*',
    '!src/**/*.stories.*',
    '!src/**/*.test.*'
  ],
  coverageReporters: ['text', 'lcov', 'html', 'json-summary'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  testTimeout: 10000,
  maxWorkers: '50%'
};
```

### Playwright Configuration
E2E test configuration:

```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/e2e-results.json' }],
    ['junit', { outputFile: 'test-results/e2e-results.xml' }]
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
    { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } }
  ],
  webServer: {
    command: 'npm run start:test',
    port: 3000,
    reuseExistingServer: !process.env.CI
  }
});
```

## CI/CD Integration

Automated testing pipeline for continuous integration.

See [ci-cd-pipeline.yml](ci-cd-pipeline.yml) for complete GitHub Actions workflow.

**Pipeline Stages:**
1. **Unit Tests** - Fast feedback, coverage reporting, Codecov integration
2. **Integration Tests** - With PostgreSQL and Redis services
3. **E2E Tests** - Full browser automation with Playwright
4. **Performance Tests** - Load testing on main branch
5. **Security Tests** - npm audit and CodeQL analysis

**Key Features:**
- Parallel job execution for speed
- Service containers for integration tests
- Artifact uploads for test reports
- Coverage comments on pull requests
- Conditional performance testing

## Best Practices

### Test Organization (AAA Pattern)
```javascript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Arrange
      const userData = { email: 'test@example.com', name: 'Test User' };

      // Act
      const result = await userService.createUser(userData);

      // Assert
      expect(result).toHaveProperty('id');
      expect(result.email).toBe(userData.email);
    });
  });
});
```

### Test Naming
- Use descriptive names: `should create user with valid data`
- Explain expected behavior, not implementation
- Group related tests with `describe` blocks

### Test Isolation
- Each test should run independently
- Clean up state between tests
- Use beforeEach/afterEach for setup/teardown
- Avoid test interdependencies

### Test Data Management
- Use factories for consistent test data
- Generate unique values (emails, IDs) to avoid conflicts
- Use realistic data that matches production patterns
- Keep test data minimal and focused

### Mocking Strategy
- Mock external services (APIs, email, payments)
- Don't mock internal modules (test real integration)
- Use dependency injection for easier mocking
- Reset mocks between tests

### Performance Considerations
- Run unit tests in parallel for speed
- Run integration tests sequentially for reliability
- Use test.skip() for slow/flaky tests temporarily
- Optimize database seed data size

### Coverage Guidelines
- Aim for 80%+ coverage as baseline
- Focus on critical paths (auth, payments, data access)
- Don't chase 100% coverage blindly
- Test behavior, not implementation details
- Exclude generated files and test helpers from coverage

### Error Testing
- Test both success and failure paths
- Test validation error messages
- Test edge cases (empty, null, invalid)
- Test error recovery and rollback

### Integration Testing
- Test database transactions and rollback
- Test API endpoints with real HTTP requests
- Test service integrations with test doubles
- Use test databases, never production

### E2E Testing
- Test critical user journeys only
- Use Page Object Model for maintainability
- Run against production-like environments
- Keep E2E tests stable and reliable

### Continuous Improvement
- Review test failures immediately
- Refactor flaky tests
- Update tests when requirements change
- Monitor test execution time
- Remove obsolete tests
