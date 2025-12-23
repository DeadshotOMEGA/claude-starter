# Database Scaling Patterns

Patterns for handling database growth from single-server to distributed systems.

## Contents

- [Scaling Decision Tree](#scaling-decision-tree)
- [Read Replicas](#read-replicas)
- [Horizontal Sharding](#horizontal-sharding)
- [Cross-Shard Queries](#cross-shard-queries)
- [Connection Pooling](#connection-pooling)

## Scaling Decision Tree

```
Start: Performance issues?
│
├─ Read-heavy workload? (>80% reads)
│  └─ YES → Read Replicas
│     ├─ Still slow? → Add caching layer
│     └─ Write bottleneck? → Continue to sharding
│
├─ Write-heavy workload? (>40% writes)
│  └─ YES → Horizontal Sharding
│     ├─ By hash → Even distribution
│     ├─ By range → Time-series data
│     └─ By tenant → Isolated workloads
│
├─ Need tenant isolation?
│  └─ YES → Tenant-Based Sharding
│     ├─ Schema per tenant (medium scale)
│     └─ Database per tenant (high isolation)
│
└─ Single large table?
   └─ YES → Vertical Partitioning
      ├─ Split hot/cold columns
      └─ Archive old data
```

## Read Replicas

### PostgreSQL Streaming Replication

**Primary configuration** (`postgresql.conf`):
```ini
# Enable WAL archiving for replication
wal_level = replica
max_wal_senders = 3          # Max number of replicas
wal_keep_size = 64           # MB of WAL to retain
```

**Replica configuration** (`recovery.conf` or `postgresql.auto.conf`):
```ini
primary_conninfo = 'host=primary-db port=5432 user=replicator password=xxx'
primary_slot_name = 'replica_1'
```

**Create replication user** (on primary):
```sql
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secure_password';
```

### Python Read/Write Splitting

```python
import random
from typing import Literal

class DatabaseRouter:
    """Route queries to primary or replicas based on operation type."""

    def __init__(self, primary_dsn: str, replica_dsns: list[str]):
        self.primary = primary_dsn
        self.replicas = replica_dsns
        self._replica_index = 0

    def get_connection(self, operation: Literal['read', 'write']) -> str:
        """Return DSN for read or write operation."""
        if operation == 'write':
            return self.primary

        # Round-robin across replicas
        replica = self.replicas[self._replica_index % len(self.replicas)]
        self._replica_index += 1
        return replica

    def get_random_replica(self) -> str:
        """Random replica selection (alternative to round-robin)."""
        return random.choice(self.replicas)

# Usage
router = DatabaseRouter(
    primary_dsn='postgresql://primary:5432/db',
    replica_dsns=[
        'postgresql://replica1:5432/db',
        'postgresql://replica2:5432/db',
    ]
)

# Read operations use replicas
read_conn = router.get_connection('read')

# Write operations use primary
write_conn = router.get_connection('write')
```

### Django Database Router

```python
class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):
        return 'replica'

    def db_for_write(self, model, **hints):
        return 'default'  # Primary

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'
```

## Horizontal Sharding

### Hash-Based Sharding

**Consistent hashing** for even distribution:

```python
import hashlib

SHARDS = {
    0: 'postgresql://shard0:5432/db',
    1: 'postgresql://shard1:5432/db',
    2: 'postgresql://shard2:5432/db',
    3: 'postgresql://shard3:5432/db',
}

def get_shard(user_id: str, num_shards: int = 4) -> int:
    """Determine shard using consistent hash."""
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    return hash_value % num_shards

def get_connection_for_user(user_id: str) -> str:
    """Get database connection for a specific user."""
    shard_id = get_shard(user_id)
    return SHARDS[shard_id]

# Usage
user_id = 'user_12345'
conn_string = get_connection_for_user(user_id)
# Always routes same user to same shard
```

### Range-Based Sharding

**Time-series partitioning** by date:

```python
from datetime import datetime

SHARD_RANGES = {
    'shard_2023': ('2023-01-01', '2023-12-31'),
    'shard_2024': ('2024-01-01', '2024-12-31'),
    'shard_2025': ('2025-01-01', '2025-12-31'),
}

def get_shard_for_date(date: datetime) -> str:
    """Route query to shard based on date range."""
    date_str = date.strftime('%Y-%m-%d')

    for shard_name, (start, end) in SHARD_RANGES.items():
        if start <= date_str <= end:
            return f'postgresql://{shard_name}:5432/db'

    raise ValueError(f'No shard found for date {date_str}')

# Query recent data (hits current shard)
recent_shard = get_shard_for_date(datetime(2025, 6, 1))

# Query historical data (hits archive shard)
archive_shard = get_shard_for_date(datetime(2023, 3, 15))
```

### Tenant-Based Sharding

**Schema-per-tenant** (medium scale):

```sql
-- Create schema for each tenant
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_widgets;

-- Identical table structure in each schema
CREATE TABLE tenant_acme.users (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL
);

CREATE TABLE tenant_widgets.users (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL
);
```

```python
def get_schema_for_tenant(tenant_id: str) -> str:
    """Return schema name for tenant."""
    return f'tenant_{tenant_id}'

def execute_tenant_query(tenant_id: str, query: str):
    """Execute query in tenant's schema."""
    schema = get_schema_for_tenant(tenant_id)

    # Set search_path to tenant schema
    with connection.cursor() as cursor:
        cursor.execute(f'SET search_path TO {schema}')
        cursor.execute(query)
```

**Database-per-tenant** (high isolation):

```python
TENANT_DATABASES = {
    'acme': 'postgresql://shard1:5432/tenant_acme',
    'widgets': 'postgresql://shard2:5432/tenant_widgets',
    'tech_corp': 'postgresql://shard3:5432/tenant_tech_corp',
}

def get_tenant_connection(tenant_id: str) -> str:
    """Return dedicated database for tenant."""
    if tenant_id not in TENANT_DATABASES:
        raise ValueError(f'Unknown tenant: {tenant_id}')
    return TENANT_DATABASES[tenant_id]
```

## Cross-Shard Queries

**Scatter-gather** pattern for aggregating across shards:

```python
import asyncio
import asyncpg

async def query_shard(dsn: str, query: str):
    """Execute query on a single shard."""
    conn = await asyncpg.connect(dsn)
    try:
        results = await conn.fetch(query)
        return results
    finally:
        await conn.close()

async def query_all_shards(shards: list[str], query: str):
    """Execute query across all shards and aggregate results."""
    tasks = [query_shard(shard, query) for shard in shards]

    # Execute in parallel
    results = await asyncio.gather(*tasks)

    # Flatten results from all shards
    return [row for shard_results in results for row in shard_results]

# Usage
async def get_all_active_users():
    """Find active users across all database shards."""
    query = "SELECT id, email FROM users WHERE active = true"

    all_shards = [
        'postgresql://shard0:5432/db',
        'postgresql://shard1:5432/db',
        'postgresql://shard2:5432/db',
    ]

    users = await query_all_shards(all_shards, query)
    return users

# Run async query
users = asyncio.run(get_all_active_users())
```

**Limitations:**
- No cross-shard JOINs
- Aggregations require application-level merging
- Transactions cannot span shards

## Connection Pooling

### PgBouncer Configuration

**pgbouncer.ini:**
```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
# Session pooling: One server connection per client session
# Transaction pooling: Release connection after each transaction (recommended)
# Statement pooling: Release after each statement (aggressive)
pool_mode = transaction

# Listen configuration
listen_addr = 0.0.0.0
listen_port = 6432

# Connection limits
max_client_conn = 1000        # Maximum client connections
default_pool_size = 25        # Connections per database
reserve_pool_size = 5         # Emergency reserve
reserve_pool_timeout = 3      # Seconds before using reserve

# Timeouts
server_idle_timeout = 600     # Close idle server connections (seconds)
server_connect_timeout = 15   # Connection attempt timeout
query_timeout = 0             # No query timeout (0 = disabled)

# Logging
admin_users = postgres
stats_users = stats_user
log_connections = 1
log_disconnections = 1
```

**userlist.txt** (authentication):
```
"myuser" "md5d8578edf8458ce06fbc5bb76a58c5ca4"
```

Generate password hash:
```bash
echo -n "passwordmyuser" | md5sum
```

### Application Connection Pool (Python)

```python
import asyncpg

class ConnectionPool:
    """Application-level connection pooling."""

    def __init__(self, dsn: str, min_size: int = 10, max_size: int = 50):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None

    async def initialize(self):
        """Create connection pool on startup."""
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=60,
            max_queries=50000,        # Recycle after N queries
            max_inactive_connection_lifetime=300,  # 5 minutes
        )

    async def execute(self, query: str, *args):
        """Execute query using pooled connection."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def close(self):
        """Close all pooled connections."""
        await self.pool.close()

# Usage
pool = ConnectionPool('postgresql://localhost:5432/mydb')
await pool.initialize()

# Reuse connections from pool
results = await pool.execute('SELECT * FROM users WHERE active = $1', True)
```

### Best Practices

**Pool sizing formula:**
```
connections_needed = (num_workers × avg_concurrent_queries) + buffer
```

Example:
- 10 web workers
- 3 queries per request average
- 20% buffer
- = (10 × 3) × 1.2 = 36 connections

**PgBouncer vs Application Pooling:**

| Feature | PgBouncer | Application Pool |
|---------|-----------|------------------|
| Connection overhead | Minimal | Higher |
| Transaction pooling | Yes | No |
| Multiple apps | Shared pool | Separate pools |
| Complexity | External service | In-app |
| Best for | Multiple apps, high churn | Single app, moderate load |
