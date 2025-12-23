# PerformanceTestFramework

Load testing and performance analysis framework with automated recommendations.

## Full Implementation

```javascript
// test-framework/performance-testing.js
const { performance } = require('perf_hooks');

class PerformanceTestFramework {
  constructor() {
    this.benchmarks = new Map();
    this.thresholds = {
      responseTime: 1000,
      throughput: 100,
      errorRate: 0.01
    };
  }

  async runLoadTest(config) {
    const {
      endpoint,
      method = 'GET',
      payload,
      concurrent = 10,
      duration = 60000,
      rampUp = 5000
    } = config;

    console.log(`🚀 Starting load test: ${concurrent} users for ${duration}ms`);

    const results = {
      requests: [],
      errors: [],
      startTime: Date.now(),
      endTime: null
    };

    // Ramp up users gradually
    const userPromises = [];
    for (let i = 0; i < concurrent; i++) {
      const delay = (rampUp / concurrent) * i;
      userPromises.push(
        this.simulateUser(endpoint, method, payload, duration - delay, delay, results)
      );
    }

    await Promise.all(userPromises);
    results.endTime = Date.now();

    return this.analyzeResults(results);
  }

  async simulateUser(endpoint, method, payload, duration, delay, results) {
    await new Promise(resolve => setTimeout(resolve, delay));

    const endTime = Date.now() + duration;

    while (Date.now() < endTime) {
      const startTime = performance.now();

      try {
        const response = await this.makeRequest(endpoint, method, payload);
        const endTime = performance.now();

        results.requests.push({
          startTime,
          endTime,
          duration: endTime - startTime,
          status: response.status,
          size: response.data ? JSON.stringify(response.data).length : 0
        });

      } catch (error) {
        results.errors.push({
          timestamp: Date.now(),
          error: error.message,
          type: error.code || 'unknown'
        });
      }

      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  async makeRequest(endpoint, method, payload) {
    const axios = require('axios');

    const config = {
      method,
      url: endpoint,
      timeout: 30000,
      validateStatus: () => true
    };

    if (payload && ['POST', 'PUT', 'PATCH'].includes(method.toUpperCase())) {
      config.data = payload;
    }

    return await axios(config);
  }

  analyzeResults(results) {
    const { requests, errors, startTime, endTime } = results;
    const totalDuration = endTime - startTime;

    // Calculate metrics
    const responseTimes = requests.map(r => r.duration);
    const successfulRequests = requests.filter(r => r.status < 400);
    const failedRequests = requests.filter(r => r.status >= 400);

    const analysis = {
      summary: {
        totalRequests: requests.length,
        successfulRequests: successfulRequests.length,
        failedRequests: failedRequests.length + errors.length,
        errorRate: (failedRequests.length + errors.length) / requests.length,
        testDuration: totalDuration,
        throughput: (requests.length / totalDuration) * 1000 // requests per second
      },
      responseTime: {
        min: Math.min(...responseTimes),
        max: Math.max(...responseTimes),
        mean: responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length,
        p50: this.percentile(responseTimes, 50),
        p90: this.percentile(responseTimes, 90),
        p95: this.percentile(responseTimes, 95),
        p99: this.percentile(responseTimes, 99)
      },
      errors: {
        total: errors.length,
        byType: this.groupBy(errors, 'type'),
        timeline: errors.map(e => ({ timestamp: e.timestamp, type: e.type }))
      },
      recommendations: this.generatePerformanceRecommendations(results)
    };

    this.logResults(analysis);
    return analysis;
  }

  percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[index];
  }

  groupBy(array, key) {
    return array.reduce((groups, item) => {
      const group = item[key];
      groups[group] = groups[group] || [];
      groups[group].push(item);
      return groups;
    }, {});
  }

  generatePerformanceRecommendations(results) {
    const recommendations = [];
    const { summary, responseTime } = this.analyzeResults(results);

    if (responseTime.mean > this.thresholds.responseTime) {
      recommendations.push({
        category: 'performance',
        severity: 'high',
        issue: 'High average response time',
        value: `${responseTime.mean.toFixed(2)}ms`,
        recommendation: 'Optimize database queries and add caching layers'
      });
    }

    if (summary.throughput < this.thresholds.throughput) {
      recommendations.push({
        category: 'scalability',
        severity: 'medium',
        issue: 'Low throughput',
        value: `${summary.throughput.toFixed(2)} req/s`,
        recommendation: 'Consider horizontal scaling or connection pooling'
      });
    }

    if (summary.errorRate > this.thresholds.errorRate) {
      recommendations.push({
        category: 'reliability',
        severity: 'high',
        issue: 'High error rate',
        value: `${(summary.errorRate * 100).toFixed(2)}%`,
        recommendation: 'Investigate error causes and implement proper error handling'
      });
    }

    return recommendations;
  }

  logResults(analysis) {
    console.log('\n📈 Performance Test Results:');
    console.log(`Total Requests: ${analysis.summary.totalRequests}`);
    console.log(`Success Rate: ${((analysis.summary.successfulRequests / analysis.summary.totalRequests) * 100).toFixed(2)}%`);
    console.log(`Throughput: ${analysis.summary.throughput.toFixed(2)} req/s`);
    console.log(`Average Response Time: ${analysis.responseTime.mean.toFixed(2)}ms`);
    console.log(`95th Percentile: ${analysis.responseTime.p95.toFixed(2)}ms`);

    if (analysis.recommendations.length > 0) {
      console.log('\n⚠️ Recommendations:');
      analysis.recommendations.forEach(rec => {
        console.log(`- ${rec.issue}: ${rec.recommendation}`);
      });
    }
  }
}

module.exports = { PerformanceTestFramework };
```

## Usage Examples

### Basic Load Test

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

### POST Request Load Test

```javascript
const results = await perfTest.runLoadTest({
  endpoint: 'http://localhost:3000/api/users',
  method: 'POST',
  payload: {
    email: 'test@example.com',
    name: 'Test User'
  },
  concurrent: 20,
  duration: 30000,
  rampUp: 5000
});
```

### Custom Thresholds

```javascript
const perfTest = new PerformanceTestFramework();

// Set custom thresholds
perfTest.thresholds = {
  responseTime: 500,  // 500ms max average response
  throughput: 200,    // 200 req/s minimum
  errorRate: 0.005    // 0.5% max error rate
};

const results = await perfTest.runLoadTest({
  endpoint: 'http://localhost:3000/api/products',
  concurrent: 100,
  duration: 120000
});
```

### Analyzing Results

```javascript
const results = await perfTest.runLoadTest(config);

// Summary metrics
console.log('Total requests:', results.summary.totalRequests);
console.log('Success rate:', (results.summary.successfulRequests / results.summary.totalRequests * 100).toFixed(2) + '%');
console.log('Error rate:', (results.summary.errorRate * 100).toFixed(2) + '%');
console.log('Throughput:', results.summary.throughput.toFixed(2), 'req/s');

// Response time metrics
console.log('Min response:', results.responseTime.min.toFixed(2) + 'ms');
console.log('Max response:', results.responseTime.max.toFixed(2) + 'ms');
console.log('Mean response:', results.responseTime.mean.toFixed(2) + 'ms');
console.log('P50 (median):', results.responseTime.p50.toFixed(2) + 'ms');
console.log('P90:', results.responseTime.p90.toFixed(2) + 'ms');
console.log('P95:', results.responseTime.p95.toFixed(2) + 'ms');
console.log('P99:', results.responseTime.p99.toFixed(2) + 'ms');

// Error analysis
console.log('Total errors:', results.errors.total);
console.log('Errors by type:', results.errors.byType);

// Recommendations
results.recommendations.forEach(rec => {
  console.log(`[${rec.severity}] ${rec.category}: ${rec.issue}`);
  console.log(`  Value: ${rec.value}`);
  console.log(`  Recommendation: ${rec.recommendation}`);
});
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `endpoint` | string | Required | URL to test |
| `method` | string | `'GET'` | HTTP method |
| `payload` | object | `undefined` | Request body (for POST/PUT) |
| `concurrent` | number | `10` | Number of concurrent users |
| `duration` | number | `60000` | Test duration in milliseconds |
| `rampUp` | number | `5000` | Time to gradually add users (ms) |

## Metrics Explained

### Response Time Percentiles
- **P50 (Median)**: 50% of requests were faster than this
- **P90**: 90% of requests were faster than this
- **P95**: 95% of requests were faster than this
- **P99**: 99% of requests were faster than this

Higher percentiles (P95, P99) reveal tail latency - the worst-case experience.

### Throughput
Requests per second the system handled during the test. Indicates capacity.

### Error Rate
Percentage of failed requests. Includes HTTP errors (4xx, 5xx) and exceptions.

## Best Practices

### Gradual Ramp-Up
Always use ramp-up to avoid overwhelming the system immediately:
```javascript
concurrent: 100,
rampUp: 30000  // Add users over 30 seconds
```

### Realistic Durations
Run tests long enough to detect issues:
- Smoke test: 30s - 1min
- Standard test: 5-10min
- Stress test: 30min - 1hr

### Baseline First
Establish baseline metrics before optimization:
```javascript
// Run baseline test
const baseline = await perfTest.runLoadTest(config);

// Make optimizations...

// Run comparison test
const optimized = await perfTest.runLoadTest(config);

// Compare results
console.log('Improvement:', ((baseline.responseTime.mean - optimized.responseTime.mean) / baseline.responseTime.mean * 100).toFixed(2) + '%');
```

### Monitor System Resources
Watch CPU, memory, and I/O during tests to identify bottlenecks.

### Test Production-Like Environments
Don't test against development databases or underpowered instances.
