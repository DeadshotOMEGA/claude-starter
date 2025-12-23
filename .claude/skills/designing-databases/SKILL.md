---
name: designing-databases
description: Database architecture patterns including data modeling, microservices data boundaries, polyglot persistence, and scalability strategies. Use when designing database schemas, choosing database technologies, or planning data architecture.
---

# Designing Databases

Design scalable, maintainable database architectures using proven patterns and principles.

## Quick Start

```sql
-- Standard entity template (PostgreSQL)
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

For schema patterns → see DATA-MODELING.md
For technology selection → see TECHNOLOGY-SELECTION.md

## Quick Reference

| Topic | Doc | Use When |
|-------|-----|----------|
| Data Modeling | DATA-MODELING.md | Designing schemas, relationships, normalization |
| Microservices | MICROSERVICES.md | Defining service data boundaries, avoiding distributed monoliths |
| Polyglot Persistence | POLYGLOT.md | Choosing database types for different use cases |
| Scaling | SCALING.md | Planning for growth, sharding, replication |
| Technology Selection | TECHNOLOGY-SELECTION.md | Evaluating database options |
| Migrations | MIGRATIONS.md | Schema evolution, zero-downtime changes |

## Core Principles

1. **Domain alignment** — Data boundaries follow business domains, not technical layers
2. **Access pattern driven** — Schema optimized for how data is read/written, not just structure
3. **Consistency clarity** — Explicit about where consistency matters (transactions) vs eventual consistency
4. **Evolution ready** — Schemas designed for change with versioning and migration paths
5. **Right tool right job** — Use polyglot persistence; don't force one database for everything

## Decision Framework

### When to Use Relational (PostgreSQL, MySQL)
- Complex relationships with referential integrity
- ACID transactions required
- Ad-hoc queries needed
- Mature tooling and expertise required
- **Examples**: User accounts, orders, inventory

### When to Use Document (MongoDB, DynamoDB)
- Nested/hierarchical data structures
- Schema flexibility needed
- High write throughput
- Horizontal scaling priority
- **Examples**: Product catalogs, user profiles, logs

### When to Use Key-Value (Redis, DynamoDB)
- Simple lookups by ID
- Caching layer
- Session storage
- High performance reads
- **Examples**: Session data, rate limiting, feature flags

### When to Use Time-Series (TimescaleDB, InfluxDB)
- Time-stamped event data
- Analytics on time ranges
- Retention policies needed
- Downsampling/aggregation
- **Examples**: Metrics, IoT sensors, audit logs

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| God table | Single table with 50+ columns for everything | Split into focused tables by domain |
| EAV abuse | Entity-Attribute-Value for flexibility | Use JSON columns or document DB |
| Premature sharding | Sharding before needed | Scale vertically first, shard only at limits |
| Shared database | Multiple services sharing one database | Each service owns its data store |
| No foreign keys | "Performance" excuse to skip constraints | Use constraints; optimize queries instead |

## Further Reading

For detailed guidance on each topic, see the linked documents above.
