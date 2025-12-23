# Polyglot Persistence

Using multiple database technologies in the same system, choosing the right tool for each job.

## When to Use Multiple Databases

| Scenario | Primary Database | Secondary Database | Why |
|----------|------------------|-------------------|-----|
| Full-text search | PostgreSQL | Elasticsearch | Complex search queries, relevance ranking, fuzzy matching |
| Caching | PostgreSQL | Redis | Sub-millisecond reads, reduce DB load, session storage |
| Analytics | PostgreSQL (OLTP) | ClickHouse / TimescaleDB | Columnar storage, time-series aggregation, high write throughput |
| Session storage | PostgreSQL | Redis | Fast ephemeral data, TTL expiration, distributed sessions |
| Document storage | PostgreSQL | MongoDB | Flexible schema, nested documents, rapid prototyping |
| Time-series data | PostgreSQL | InfluxDB / TimescaleDB | Time-based queries, downsampling, retention policies |
| Graph relationships | PostgreSQL | Neo4j | Complex relationship traversal, recommendation engines |
| Real-time messaging | PostgreSQL | RabbitMQ / Kafka | Event streaming, pub/sub patterns, message queuing |

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                      Application                        │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │   API Layer │  │  Services   │  │  Workers     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘   │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          │                 │                 │
     ┌────▼────┐       ┌────▼────┐       ┌───▼────┐
     │         │       │         │       │        │
     │  Redis  │       │  Postgres│      │ Search │
     │ (Cache) │       │ (Primary)│      │ (Elastic)│
     │         │       │         │       │        │
     └─────────┘       └────┬────┘       └────────┘
                            │
                     ┌──────▼──────┐
                     │   CDC Tool  │
                     │  (Debezium) │
                     └──────┬──────┘
                            │
                       ┌────▼────┐
                       │  Kafka  │
                       └────┬────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
         ┌────▼────┐   ┌────▼────┐   ┌───▼────┐
         │ Redis   │   │ Search  │   │ Analytics│
         │ Consumer│   │Indexer  │   │  Store  │
         └─────────┘   └─────────┘   └─────────┘
```

## Synchronization Strategies

### 1. Dual Write (Simple but Risky)

Application writes to multiple databases directly.

**Pros:**
- Simple to implement
- No additional infrastructure
- Immediate consistency

**Cons:**
- Risk of partial failures (one DB succeeds, other fails)
- No transactional guarantees across databases
- Application complexity increases

**Use when:** Low-stakes data, eventual consistency acceptable, simple cache invalidation.

```python
async def create_product_dual_write(product_data):
    # Write to primary DB
    product = await db.products.insert(product_data)

    # Write to search index (risk: might fail)
    try:
        await elasticsearch.index(
            index="products",
            id=product.id,
            document=product_data
        )
    except Exception as e:
        # Log error, queue for retry
        await retry_queue.add("index_product", product.id)

    return product
```

### 2. Change Data Capture (Recommended)

Capture database changes at the transaction log level and stream to consumers.

**Pros:**
- Single source of truth (primary database)
- No application-level dual writes
- Guaranteed to capture all changes
- Ordered, durable event stream

**Cons:**
- Additional infrastructure required
- Slight delay (eventual consistency)
- Complexity in setup

**Architecture:**
```
PostgreSQL WAL → Debezium → Kafka → Consumers
                                      ├─ Redis sync
                                      ├─ Elasticsearch indexer
                                      └─ Analytics pipeline
```

**Use when:** Critical data consistency, multiple downstream systems, audit trail needed.

### 3. Application Events (Outbox Pattern)

Application writes to primary DB + outbox table in same transaction. Background worker publishes events.

**Pros:**
- Transactional integrity within primary DB
- Guaranteed event publishing
- Application controls event shape

**Cons:**
- Additional table and worker needed
- Slight delay in propagation

**Use when:** Need transaction guarantees but want application-controlled events.

See: Outbox pattern documentation for implementation details.

## Cache-Aside Pattern

Most common caching strategy: application checks cache first, falls back to database.

```python
# Read operation
async def get_product(product_id: str):
    """Fetch product with cache-aside pattern."""
    # 1. Try cache first
    cached = await redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)

    # 2. Cache miss - fetch from database
    product = await db.query(
        "SELECT * FROM products WHERE id = $1",
        product_id
    )

    if not product:
        raise NotFoundError(f"Product {product_id} not found")

    # 3. Populate cache for next time
    await redis.setex(
        f"product:{product_id}",
        3600,  # 1 hour TTL
        json.dumps(product)
    )

    return product


# Write operation
async def update_product(product_id: str, updates: dict):
    """Update product and invalidate cache."""
    # 1. Update primary database
    product = await db.query(
        """
        UPDATE products
        SET name = $1, price = $2, updated_at = NOW()
        WHERE id = $3
        RETURNING *
        """,
        updates['name'],
        updates['price'],
        product_id
    )

    # 2. Invalidate cache (lazy regeneration on next read)
    await redis.delete(f"product:{product_id}")

    # Alternative: Update cache immediately
    # await redis.setex(
    #     f"product:{product_id}",
    #     3600,
    #     json.dumps(product)
    # )

    return product
```

## Best Practices

### Data Ownership
- One database is the source of truth per entity
- Other databases are derived views
- Never write same data to multiple DBs as primary

### Consistency Model
- Choose appropriate consistency: immediate, eventual, or bounded
- Document expected lag for derived views
- Handle cache misses gracefully

### Monitoring
- Track synchronization lag
- Alert on replication failures
- Monitor cache hit rates

### Schema Evolution
- Plan for schema changes across systems
- Version your events/messages
- Test data migration across all databases

### Failure Handling
- Primary DB failure → application down (expected)
- Cache failure → degrade to direct DB reads
- Search failure → degrade to basic DB queries
- Always gracefully handle secondary DB failures
