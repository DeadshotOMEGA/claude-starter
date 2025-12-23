# TestSuiteManager

Comprehensive test orchestration and reporting framework.

## Full Implementation

```javascript
// test-framework/test-suite-manager.js
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class TestSuiteManager {
  constructor(config = {}) {
    this.config = {
      testDirectory: './tests',
      coverageThreshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      },
      testPatterns: {
        unit: '**/*.test.js',
        integration: '**/*.integration.test.js',
        e2e: '**/*.e2e.test.js'
      },
      ...config
    };

    this.testResults = {
      unit: null,
      integration: null,
      e2e: null,
      coverage: null
    };
  }

  async runFullTestSuite() {
    console.log('🧪 Starting comprehensive test suite...');

    try {
      // Run tests in sequence for better resource management
      await this.runUnitTests();
      await this.runIntegrationTests();
      await this.runE2ETests();
      await this.generateCoverageReport();

      const summary = this.generateTestSummary();
      await this.publishTestResults(summary);

      return summary;
    } catch (error) {
      console.error('❌ Test suite failed:', error.message);
      throw error;
    }
  }

  async runUnitTests() {
    console.log('🔬 Running unit tests...');

    const jestConfig = {
      testMatch: [this.config.testPatterns.unit],
      collectCoverage: true,
      collectCoverageFrom: [
        'src/**/*.{js,ts}',
        '!src/**/*.test.{js,ts}',
        '!src/**/*.spec.{js,ts}',
        '!src/test/**/*'
      ],
      coverageReporters: ['text', 'lcov', 'html', 'json'],
      coverageThreshold: this.config.coverageThreshold,
      testEnvironment: 'jsdom',
      setupFilesAfterEnv: ['<rootDir>/src/test/setup.js'],
      moduleNameMapping: {
        '^@/(.*)$': '<rootDir>/src/$1'
      }
    };

    try {
      const command = `npx jest --config='${JSON.stringify(jestConfig)}' --passWithNoTests`;
      const result = execSync(command, { encoding: 'utf8', stdio: 'pipe' });

      this.testResults.unit = {
        status: 'passed',
        output: result,
        timestamp: new Date().toISOString()
      };

      console.log('✅ Unit tests passed');
    } catch (error) {
      this.testResults.unit = {
        status: 'failed',
        output: error.stdout || error.message,
        error: error.stderr || error.message,
        timestamp: new Date().toISOString()
      };

      throw new Error(`Unit tests failed: ${error.message}`);
    }
  }

  async runIntegrationTests() {
    console.log('🔗 Running integration tests...');

    // Start test database and services
    await this.setupTestEnvironment();

    try {
      const command = `npx jest --testMatch="${this.config.testPatterns.integration}" --runInBand`;
      const result = execSync(command, { encoding: 'utf8', stdio: 'pipe' });

      this.testResults.integration = {
        status: 'passed',
        output: result,
        timestamp: new Date().toISOString()
      };

      console.log('✅ Integration tests passed');
    } catch (error) {
      this.testResults.integration = {
        status: 'failed',
        output: error.stdout || error.message,
        error: error.stderr || error.message,
        timestamp: new Date().toISOString()
      };

      throw new Error(`Integration tests failed: ${error.message}`);
    } finally {
      await this.teardownTestEnvironment();
    }
  }

  async runE2ETests() {
    console.log('🌐 Running E2E tests...');

    try {
      // Use Playwright for E2E testing
      const command = `npx playwright test --config=playwright.config.js`;
      const result = execSync(command, { encoding: 'utf8', stdio: 'pipe' });

      this.testResults.e2e = {
        status: 'passed',
        output: result,
        timestamp: new Date().toISOString()
      };

      console.log('✅ E2E tests passed');
    } catch (error) {
      this.testResults.e2e = {
        status: 'failed',
        output: error.stdout || error.message,
        error: error.stderr || error.message,
        timestamp: new Date().toISOString()
      };

      throw new Error(`E2E tests failed: ${error.message}`);
    }
  }

  async setupTestEnvironment() {
    console.log('⚙️ Setting up test environment...');

    // Start test database
    try {
      execSync('docker-compose -f docker-compose.test.yml up -d postgres redis', { stdio: 'pipe' });

      // Wait for services to be ready
      await this.waitForServices();

      // Run database migrations
      execSync('npm run db:migrate:test', { stdio: 'pipe' });

      // Seed test data
      execSync('npm run db:seed:test', { stdio: 'pipe' });

    } catch (error) {
      throw new Error(`Failed to setup test environment: ${error.message}`);
    }
  }

  async teardownTestEnvironment() {
    console.log('🧹 Cleaning up test environment...');

    try {
      execSync('docker-compose -f docker-compose.test.yml down', { stdio: 'pipe' });
    } catch (error) {
      console.warn('Warning: Failed to cleanup test environment:', error.message);
    }
  }

  async waitForServices(timeout = 30000) {
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      try {
        execSync('pg_isready -h localhost -p 5433', { stdio: 'pipe' });
        execSync('redis-cli -p 6380 ping', { stdio: 'pipe' });
        return; // Services are ready
      } catch (error) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    throw new Error('Test services failed to start within timeout');
  }

  generateTestSummary() {
    const summary = {
      timestamp: new Date().toISOString(),
      overall: {
        status: this.determineOverallStatus(),
        duration: this.calculateTotalDuration(),
        testsRun: this.countTotalTests()
      },
      results: this.testResults,
      coverage: this.parseCoverageReport(),
      recommendations: this.generateRecommendations()
    };

    console.log('\n📊 Test Summary:');
    console.log(`Overall Status: ${summary.overall.status}`);
    console.log(`Total Duration: ${summary.overall.duration}ms`);
    console.log(`Tests Run: ${summary.overall.testsRun}`);

    return summary;
  }

  determineOverallStatus() {
    const results = Object.values(this.testResults);
    const failures = results.filter(result => result && result.status === 'failed');
    return failures.length === 0 ? 'PASSED' : 'FAILED';
  }

  generateRecommendations() {
    const recommendations = [];

    // Coverage recommendations
    const coverage = this.parseCoverageReport();
    if (coverage && coverage.total.lines.pct < 80) {
      recommendations.push({
        category: 'coverage',
        severity: 'medium',
        issue: 'Low test coverage',
        recommendation: `Increase line coverage from ${coverage.total.lines.pct}% to at least 80%`
      });
    }

    // Failed test recommendations
    Object.entries(this.testResults).forEach(([type, result]) => {
      if (result && result.status === 'failed') {
        recommendations.push({
          category: 'test-failure',
          severity: 'high',
          issue: `${type} tests failing`,
          recommendation: `Review and fix failing ${type} tests before deployment`
        });
      }
    });

    return recommendations;
  }

  parseCoverageReport() {
    try {
      const coveragePath = path.join(process.cwd(), 'coverage/coverage-summary.json');
      if (fs.existsSync(coveragePath)) {
        return JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
      }
    } catch (error) {
      console.warn('Could not parse coverage report:', error.message);
    }
    return null;
  }
}

module.exports = { TestSuiteManager };
```

## Usage Examples

### Basic Usage
```javascript
const { TestSuiteManager } = require('./test-framework/test-suite-manager');

const manager = new TestSuiteManager();
const summary = await manager.runFullTestSuite();

if (summary.overall.status !== 'PASSED') {
  process.exit(1);
}
```

### Custom Configuration
```javascript
const manager = new TestSuiteManager({
  testDirectory: './tests',
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    }
  },
  testPatterns: {
    unit: '**/*.spec.ts',
    integration: '**/*.integration.spec.ts',
    e2e: '**/*.e2e.spec.ts'
  }
});
```

### Running Specific Test Types
```javascript
// Run only unit tests
await manager.runUnitTests();

// Run only integration tests
await manager.runIntegrationTests();

// Run only E2E tests
await manager.runE2ETests();
```

## Features

- **Orchestration**: Manages execution order of unit, integration, and E2E tests
- **Environment Management**: Automated setup/teardown of test databases and services
- **Coverage Analysis**: Enforces coverage thresholds and generates reports
- **Result Tracking**: Detailed logging of test execution and outcomes
- **Recommendations**: Automated analysis and suggestions based on results
- **Service Health**: Waits for dependent services before starting tests
