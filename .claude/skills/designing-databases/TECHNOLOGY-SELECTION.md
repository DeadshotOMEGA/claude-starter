# Database Technology Selection Guide

Quick reference for choosing the right database technology based on requirements.

## Quick Selection Guide

| Requirement | Recommended Database | Why |
|-------------|---------------------|-----|
| ACID transactions + complex queries | PostgreSQL | Best-in-class relational features, JSON support |
| Schema flexibility + horizontal scaling | MongoDB | Document model, sharding built-in |
| Sub-millisecond reads, caching | Redis | In-memory, data structures |
| Time-series data | TimescaleDB | PostgreSQL extension optimized for time-series |
| Full-text search | Elasticsearch | Purpose-built search engine |
| Graph relationships | Neo4j | Native graph traversal |
| High-volume analytics | ClickHouse | Column-oriented, extreme performance |
| Serverless, pay-per-request | DynamoDB | AWS-managed, auto-scaling |
| Multi-model (docs + graph + search) | ArangoDB | Unified query language |
| Default choice (unknown requirements) | PostgreSQL | Versatile, battle-tested, rich ecosystem |

## Relational Databases

| Feature | PostgreSQL | MySQL | SQL Server |
|---------|-----------|-------|------------|
| **JSON Support** | Excellent (JSONB, indexes) | Good (JSON type) | Good (JSON functions) |
| **Full-Text Search** | Built-in (tsvector) | Basic (FULLTEXT) | Built-in (Full-Text) |
| **Extensions** | Rich (PostGIS, TimescaleDB) | Limited | Proprietary only |
| **Replication** | Streaming, logical | Async, semi-sync | Always On, mirroring |
| **Window Functions** | Excellent | Good (v8.0+) | Excellent |
| **Geospatial** | PostGIS (best-in-class) | Basic ST_ functions | Spatial types |
| **License** | PostgreSQL (permissive) | GPL/Commercial | Proprietary |
| **Performance** | Excellent reads/writes | Faster simple reads | Excellent on Windows |
| **Best For** | General purpose, analytics | Read-heavy web apps | Enterprise Windows stacks |

### When to Use PostgreSQL
- Need ACID + flexibility
- JSON + relational in one database
- Advanced queries (CTEs, window functions)
- Open-source requirement
- **Default choice**

### When to Use MySQL
- Read-heavy workloads
- Simpler schema
- Existing MySQL expertise
- Need MyISAM for specific use cases

### When to Use SQL Server
- Windows-centric infrastructure
- .NET applications
- Enterprise support requirement
- Advanced BI features needed

## Document Databases

| Feature | MongoDB | DynamoDB | CouchDB |
|---------|---------|----------|---------|
| **Schema** | Flexible | Key-value/document | Document |
| **Query Language** | Rich (aggregation) | Limited (key/index) | MapReduce, Mango |
| **Consistency** | Configurable | Eventual/strong | Eventual |
| **Scaling** | Sharding | Auto-scaling | Multi-master replication |
| **Indexing** | Secondary indexes | GSI/LSI (limited) | Views |
| **Transactions** | Multi-document | Single-item | Single-doc |
| **Hosting** | Self/Atlas | AWS-managed | Self/cloud |
| **Best For** | Flexible schemas | Serverless apps | Offline-first apps |

### When to Use MongoDB
- Schema evolves frequently
- Need complex queries on documents
- Horizontal scaling required
- Rich query capabilities needed

### When to Use DynamoDB
- Serverless architecture
- AWS ecosystem
- Predictable single-item access patterns
- Pay-per-request pricing preferred

### When to Use CouchDB
- Offline-first applications
- Multi-master replication
- Conflict resolution needed
- Mobile sync requirements

## Key-Value Stores

| Feature | Redis | Memcached | DynamoDB |
|---------|-------|-----------|----------|
| **Data Structures** | Strings, hashes, lists, sets, sorted sets, streams | Strings only | Key-value, documents |
| **Persistence** | RDB, AOF | None | Durable |
| **Replication** | Master-replica | None (client-side) | Multi-region |
| **Max Value Size** | 512 MB | 1 MB | 400 KB |
| **Eviction** | Configurable policies | LRU | N/A (durable) |
| **Pub/Sub** | Built-in | No | Streams (limited) |
| **Transactions** | Yes (MULTI/EXEC) | No | Limited |
| **Best For** | Caching + data structures | Simple caching | Primary database |

### When to Use Redis
- Need data structures (lists, sets, sorted sets)
- Pub/sub messaging
- Session storage
- Real-time leaderboards
- Rate limiting

### When to Use Memcached
- Simple key-value caching only
- Multi-threaded performance critical
- Existing infrastructure

### When to Use DynamoDB (as KV Store)
- Need durability
- Serverless requirement
- AWS-native stack

## Decision Flowchart

```
START
  │
  ├─ Need ACID transactions?
  │    ├─ YES → Need complex joins/aggregations?
  │    │         ├─ YES → PostgreSQL
  │    │         └─ NO → PostgreSQL (simplicity) or MySQL (read-heavy)
  │    │
  │    └─ NO → Schema flexible/unknown?
  │              ├─ YES → MongoDB
  │              └─ NO → Define access patterns
  │
  ├─ Primary use case?
  │    ├─ Caching → Read latency critical?
  │    │             ├─ YES (< 1ms) → Redis
  │    │             └─ NO (< 10ms) → Redis + PostgreSQL
  │    │
  │    ├─ Time-series data → TimescaleDB (PostgreSQL extension)
  │    │
  │    ├─ Full-text search → Elasticsearch + Primary DB
  │    │
  │    ├─ Graph relationships → Neo4j + Primary DB
  │    │
  │    ├─ High-volume analytics → ClickHouse
  │    │
  │    └─ Serverless/AWS-native → DynamoDB
  │
  └─ Unclear requirements?
       └─ PostgreSQL (most versatile, can pivot later)
```

## Cost Considerations

### Self-Hosted (Monthly Estimates - Medium Scale)

| Database | Server Cost | Storage Cost | Ops Overhead | Total |
|----------|-------------|--------------|--------------|-------|
| PostgreSQL | $50-200 | $20-50 | High | $70-250 |
| MySQL | $50-200 | $20-50 | High | $70-250 |
| MongoDB | $50-200 | $20-50 | High | $70-250 |
| Redis | $50-150 | $10-30 | Medium | $60-180 |
| Elasticsearch | $100-400 | $50-150 | High | $150-550 |

### Managed Services (Monthly Estimates - Medium Scale)

| Service | Provider | Base Cost | Storage Cost | Total |
|---------|----------|-----------|--------------|-------|
| RDS PostgreSQL | AWS | $100-300 | $30-100 | $130-400 |
| Cloud SQL PostgreSQL | GCP | $100-300 | $30-100 | $130-400 |
| Atlas MongoDB | MongoDB | $60-300 | $0.25/GB | $100-400 |
| ElastiCache Redis | AWS | $50-200 | Included | $50-200 |
| DynamoDB | AWS | $0 + usage | $0.25/GB | $25-200 |
| Elasticsearch Service | Elastic | $95-500 | Included | $95-500 |

**Notes:**
- Self-hosted requires DevOps expertise (ops overhead = engineer time)
- Managed services include backups, updates, monitoring
- DynamoDB cost varies wildly by traffic pattern
- Free tiers: AWS RDS (750h/month), MongoDB Atlas (512MB), many others

## Multi-Database Strategies

### Common Patterns

**1. PostgreSQL + Redis**
- PostgreSQL: Primary, durable storage
- Redis: Caching, sessions, real-time features
- **Use when:** Need relational + sub-millisecond reads

**2. PostgreSQL + Elasticsearch**
- PostgreSQL: Primary storage
- Elasticsearch: Full-text search, analytics
- **Use when:** Complex search requirements

**3. PostgreSQL + DynamoDB**
- PostgreSQL: Main application data
- DynamoDB: High-throughput event logs
- **Use when:** Hybrid cloud, specific AWS services

**4. MongoDB + Redis**
- MongoDB: Flexible document storage
- Redis: Caching, real-time data
- **Use when:** Schema flexibility + performance

### Anti-Patterns

❌ **MySQL + PostgreSQL** — Operational overhead, no clear benefit
❌ **MongoDB + DynamoDB** — Overlapping use cases
❌ **Multiple relational DBs** — Unless hard requirements dictate

## Technology-Specific Gotchas

### PostgreSQL
- Connection pooling required (default max 100 connections)
- VACUUM can cause I/O spikes
- JSON queries slower than native fields

### MongoDB
- No joins (use aggregation pipeline or denormalize)
- Index carefully (scans are expensive)
- Watch out for large document growth

### Redis
- Volatile by default (configure persistence)
- Single-threaded (scale with clustering)
- Memory limits enforced strictly

### DynamoDB
- Plan access patterns upfront (hard to change)
- Secondary indexes are expensive
- No ad-hoc queries

### Elasticsearch
- Not a primary database (eventual consistency)
- Resource-intensive (RAM, CPU)
- Complex cluster management

## Quick Checklist

Before choosing, answer:
- [ ] What are the primary access patterns?
- [ ] Is schema stable or evolving?
- [ ] What consistency guarantees are needed?
- [ ] What's the query complexity?
- [ ] What's the expected scale (reads/writes per second)?
- [ ] Is full-text search required?
- [ ] Are transactions required?
- [ ] Self-hosted or managed?
- [ ] What's the budget?
- [ ] What's the team's expertise?

**If unsure → Start with PostgreSQL.** It handles 90% of use cases and pivoting later is feasible.
