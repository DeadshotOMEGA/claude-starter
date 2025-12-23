# TestPatterns

Reusable test utilities and patterns for common testing scenarios.

## Full Implementation

```javascript
// test-framework/test-patterns.js

class TestPatterns {
  // Page Object Model for E2E tests
  static createPageObject(page, selectors) {
    const pageObject = {};

    Object.entries(selectors).forEach(([name, selector]) => {
      pageObject[name] = {
        element: () => page.locator(selector),
        click: () => page.click(selector),
        fill: (text) => page.fill(selector, text),
        getText: () => page.textContent(selector),
        isVisible: () => page.isVisible(selector),
        waitFor: (options) => page.waitForSelector(selector, options)
      };
    });

    return pageObject;
  }

  // Test data factory
  static createTestDataFactory(schema) {
    return {
      build: (overrides = {}) => {
        const data = {};

        Object.entries(schema).forEach(([key, generator]) => {
          if (overrides[key] !== undefined) {
            data[key] = overrides[key];
          } else if (typeof generator === 'function') {
            data[key] = generator();
          } else {
            data[key] = generator;
          }
        });

        return data;
      },

      buildList: (count, overrides = {}) => {
        return Array.from({ length: count }, (_, index) =>
          this.build({ ...overrides, id: index + 1 })
        );
      }
    };
  }

  // Mock service factory
  static createMockService(serviceName, methods) {
    const mock = {};

    methods.forEach(method => {
      mock[method] = jest.fn();
    });

    mock.reset = () => {
      methods.forEach(method => {
        mock[method].mockReset();
      });
    };

    mock.restore = () => {
      methods.forEach(method => {
        mock[method].mockRestore();
      });
    };

    return mock;
  }

  // Database test helpers
  static createDatabaseTestHelpers(db) {
    return {
      async cleanTables(tableNames) {
        for (const tableName of tableNames) {
          await db.query(`TRUNCATE TABLE ${tableName} RESTART IDENTITY CASCADE`);
        }
      },

      async seedTable(tableName, data) {
        if (Array.isArray(data)) {
          for (const row of data) {
            await db.query(`INSERT INTO ${tableName} (${Object.keys(row).join(', ')}) VALUES (${Object.keys(row).map((_, i) => `$${i + 1}`).join(', ')})`, Object.values(row));
          }
        } else {
          await db.query(`INSERT INTO ${tableName} (${Object.keys(data).join(', ')}) VALUES (${Object.keys(data).map((_, i) => `$${i + 1}`).join(', ')})`, Object.values(data));
        }
      },

      async getLastInserted(tableName) {
        const result = await db.query(`SELECT * FROM ${tableName} ORDER BY id DESC LIMIT 1`);
        return result.rows[0];
      }
    };
  }

  // API test helpers
  static createAPITestHelpers(baseURL) {
    const axios = require('axios');

    const client = axios.create({
      baseURL,
      timeout: 10000,
      validateStatus: () => true // Don't throw on HTTP errors
    });

    return {
      async get(endpoint, options = {}) {
        return await client.get(endpoint, options);
      },

      async post(endpoint, data, options = {}) {
        return await client.post(endpoint, data, options);
      },

      async put(endpoint, data, options = {}) {
        return await client.put(endpoint, data, options);
      },

      async delete(endpoint, options = {}) {
        return await client.delete(endpoint, options);
      },

      withAuth(token) {
        client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        return this;
      },

      clearAuth() {
        delete client.defaults.headers.common['Authorization'];
        return this;
      }
    };
  }
}

module.exports = { TestPatterns };
```

## Usage Examples

### Page Object Model

```javascript
const { TestPatterns } = require('./test-framework/test-patterns');

test('user can login', async ({ page }) => {
  const loginPage = TestPatterns.createPageObject(page, {
    emailInput: '#email',
    passwordInput: '#password',
    submitButton: '[type="submit"]',
    errorMessage: '.error-message'
  });

  await loginPage.emailInput.fill('user@example.com');
  await loginPage.passwordInput.fill('password123');
  await loginPage.submitButton.click();

  expect(await page.url()).toContain('/dashboard');
});
```

### Test Data Factory

```javascript
const userFactory = TestPatterns.createTestDataFactory({
  id: () => Math.random().toString(36).substring(7),
  email: () => `user-${Date.now()}@example.com`,
  name: 'Test User',
  role: 'user',
  createdAt: () => new Date()
});

// Create single user
const user = userFactory.build();

// Create user with overrides
const admin = userFactory.build({ role: 'admin', name: 'Admin User' });

// Create list of users
const users = userFactory.buildList(10);

// Create list with overrides
const admins = userFactory.buildList(5, { role: 'admin' });
```

### Mock Service Factory

```javascript
const emailService = TestPatterns.createMockService('emailService', [
  'sendEmail',
  'sendBatch',
  'verifyAddress'
]);

// Configure mock behavior
emailService.sendEmail.mockResolvedValue({ id: '123', status: 'sent' });
emailService.verifyAddress.mockResolvedValue(true);

// Use in test
await myService.sendWelcomeEmail(user);
expect(emailService.sendEmail).toHaveBeenCalledWith({
  to: user.email,
  subject: 'Welcome!',
  template: 'welcome'
});

// Reset between tests
emailService.reset();
```

### Database Test Helpers

```javascript
const dbHelpers = TestPatterns.createDatabaseTestHelpers(db);

beforeEach(async () => {
  // Clean all tables
  await dbHelpers.cleanTables(['users', 'posts', 'comments']);

  // Seed test data
  await dbHelpers.seedTable('users', [
    { id: 1, email: 'user1@example.com', name: 'User 1' },
    { id: 2, email: 'user2@example.com', name: 'User 2' }
  ]);
});

test('creates post', async () => {
  await createPost({ userId: 1, title: 'Test Post' });

  const lastPost = await dbHelpers.getLastInserted('posts');
  expect(lastPost.title).toBe('Test Post');
});
```

### API Test Helpers

```javascript
const api = TestPatterns.createAPITestHelpers('http://localhost:3000');

test('creates user with authentication', async () => {
  // Login to get token
  const loginResponse = await api.post('/api/auth/login', {
    email: 'admin@example.com',
    password: 'admin123'
  });

  const token = loginResponse.data.token;

  // Make authenticated request
  const response = await api
    .withAuth(token)
    .post('/api/users', {
      email: 'newuser@example.com',
      name: 'New User'
    });

  expect(response.status).toBe(201);
  expect(response.data).toHaveProperty('id');

  // Clear auth for next test
  api.clearAuth();
});

test('handles errors gracefully', async () => {
  const response = await api.get('/api/users/invalid-id');

  expect(response.status).toBe(404);
  expect(response.data.error).toBeDefined();
});
```

## Patterns Overview

| Pattern | Purpose | Best For |
|---------|---------|----------|
| **Page Object Model** | Encapsulate page interactions | E2E tests, UI automation |
| **Test Data Factory** | Generate consistent test data | All test types |
| **Mock Service Factory** | Create service mocks | Unit tests, integration tests |
| **Database Helpers** | Manage test database state | Integration tests |
| **API Helpers** | HTTP client for API testing | Integration tests, E2E tests |
