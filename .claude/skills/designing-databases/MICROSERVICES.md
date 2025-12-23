# Microservices Data Architecture

Data architecture patterns for distributed systems with service isolation, eventual consistency, and resilient transaction handling.

## 1. Database per Service

Each service owns its data. No direct database access between services.

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  Order Service  │         │ Payment Service │         │ Inventory Svc   │
│  ┌───────────┐  │         │  ┌───────────┐  │         │  ┌───────────┐  │
│  │ Orders DB │  │         │  │ Payments  │  │         │  │ Inventory │  │
│  │  - orders │  │         │  │    DB     │  │         │  │    DB     │  │
│  │  - items  │  │         │  │ - payments│  │         │  │  - stock  │  │
│  └───────────┘  │         │  └───────────┘  │         │  └───────────┘  │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                              ┌──────▼──────┐
                              │ Event Bus   │
                              │  (Kafka/    │
                              │   RabbitMQ) │
                              └─────────────┘
```

**Benefits:**
- Service autonomy and independent scaling
- Technology diversity per service
- Fault isolation

**Challenges:**
- No joins across services
- Data consistency requires coordination
- Distributed transactions complexity

## 2. Event Sourcing

Store state changes as immutable event sequence. Current state = replay all events.

### Event Store Schema

```sql
CREATE TABLE event_store (
    id BIGSERIAL PRIMARY KEY,
    stream_id UUID NOT NULL,
    stream_type VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB,
    version INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_stream_version UNIQUE (stream_id, version)
);

CREATE INDEX idx_stream_id ON event_store(stream_id);
CREATE INDEX idx_stream_type ON event_store(stream_type);
CREATE INDEX idx_event_type ON event_store(event_type);
CREATE INDEX idx_created_at ON event_store(created_at);
```

### Rebuilding Aggregate from Events

```python
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    stream_id: str
    event_type: str
    event_data: Dict[str, Any]
    version: int
    created_at: datetime

class OrderAggregate:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = "pending"
        self.items = []
        self.total = 0.0
        self.version = 0

    def apply(self, event: Event):
        """Apply event to rebuild state"""
        if event.event_type == "OrderCreated":
            self.status = "created"
            self.items = event.event_data["items"]
            self.total = event.event_data["total"]

        elif event.event_type == "OrderPaid":
            self.status = "paid"

        elif event.event_type == "OrderShipped":
            self.status = "shipped"

        elif event.event_type == "OrderCancelled":
            self.status = "cancelled"

        self.version = event.version

    @classmethod
    def rebuild_from_events(cls, order_id: str, events: List[Event]):
        """Rebuild aggregate from event stream"""
        aggregate = cls(order_id)
        for event in sorted(events, key=lambda e: e.version):
            aggregate.apply(event)
        return aggregate

# Usage
events = fetch_events_for_stream(order_id)
order = OrderAggregate.rebuild_from_events(order_id, events)
```

**Benefits:**
- Complete audit trail
- Temporal queries (state at any point)
- Event replay for debugging

**Challenges:**
- Query complexity for current state
- Event schema evolution
- Storage growth

## 3. CQRS Pattern

Separate read and write models for scalability and optimization.

```
                    Commands (Writes)
                           │
                           ▼
                ┌──────────────────┐
                │  Write Model     │
                │  (Normalized,    │
                │   Validated)     │
                └────────┬─────────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Event Store │
                  └──────┬──────┘
                         │ Events Published
                         ▼
                  ┌─────────────┐
                  │ Projections │  (Background processors)
                  │  Builder    │
                  └──────┬──────┘
                         │
                         ▼
                ┌──────────────────┐
                │  Read Models     │
                │  (Denormalized,  │
                │   Optimized)     │
                └────────┬─────────┘
                         │
                         ▼
                    Queries (Reads)
```

**Write Model:**
```sql
-- Normalized for consistency
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    customer_id UUID NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE order_items (
    order_id UUID REFERENCES orders(id),
    product_id UUID,
    quantity INT,
    price DECIMAL
);
```

**Read Model (Projection):**
```sql
-- Denormalized for query performance
CREATE TABLE order_summary_view (
    order_id UUID PRIMARY KEY,
    customer_id UUID,
    customer_name VARCHAR(255),
    total_amount DECIMAL,
    item_count INT,
    status VARCHAR(50),
    order_date TIMESTAMP,
    items JSONB  -- All items in single field
);

CREATE INDEX idx_customer_orders ON order_summary_view(customer_id, order_date DESC);
```

## 4. Saga Pattern

Distributed transaction coordination with compensating actions.

```python
from enum import Enum
from typing import Callable, List

class SagaStep:
    def __init__(self,
                 name: str,
                 execute: Callable,
                 compensate: Callable):
        self.name = name
        self.execute = execute
        self.compensate = compensate

class SagaStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    COMPENSATING = "compensating"

class Saga:
    def __init__(self, saga_id: str):
        self.saga_id = saga_id
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []

    def add_step(self, step: SagaStep):
        self.steps.append(step)
        return self

    def execute(self):
        """Execute saga with automatic rollback on failure"""
        try:
            # Execute all steps forward
            for step in self.steps:
                print(f"Executing: {step.name}")
                step.execute()
                self.completed_steps.append(step)

            return SagaStatus.SUCCESS

        except Exception as e:
            print(f"Saga failed at {step.name}: {e}")
            print("Starting compensation...")

            # Compensate in reverse order
            for completed_step in reversed(self.completed_steps):
                try:
                    print(f"Compensating: {completed_step.name}")
                    completed_step.compensate()
                except Exception as comp_error:
                    print(f"Compensation failed for {completed_step.name}: {comp_error}")

            return SagaStatus.FAILED

# Example: Order Creation Saga
def create_order_saga(order_data):
    saga = Saga(saga_id=order_data["order_id"])

    # Step 1: Reserve inventory
    saga.add_step(SagaStep(
        name="Reserve Inventory",
        execute=lambda: inventory_service.reserve(
            order_data["items"]
        ),
        compensate=lambda: inventory_service.release(
            order_data["items"]
        )
    ))

    # Step 2: Process payment
    saga.add_step(SagaStep(
        name="Process Payment",
        execute=lambda: payment_service.charge(
            order_data["customer_id"],
            order_data["total"]
        ),
        compensate=lambda: payment_service.refund(
            order_data["customer_id"],
            order_data["total"]
        )
    ))

    # Step 3: Create order
    saga.add_step(SagaStep(
        name="Create Order",
        execute=lambda: order_service.create(order_data),
        compensate=lambda: order_service.cancel(
            order_data["order_id"]
        )
    ))

    return saga.execute()
```

**Benefits:**
- No distributed locks
- Service autonomy preserved
- Automatic rollback handling

**Challenges:**
- Compensating logic complexity
- Eventual consistency window
- Idempotency required

## 5. Outbox Pattern

Reliable event publishing with atomic database writes.

### Outbox Table Schema

```sql
CREATE TABLE outbox (
    id BIGSERIAL PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,

    INDEX idx_unprocessed (processed_at, created_at)
        WHERE processed_at IS NULL
);
```

### Atomic Write with Outbox

```python
import psycopg2
from psycopg2.extras import Json
import json
from datetime import datetime

class OrderService:
    def __init__(self, db_connection):
        self.db = db_connection

    def create_order(self, order_data):
        """Atomic write to orders table AND outbox"""
        cursor = self.db.cursor()

        try:
            # Start transaction
            cursor.execute("BEGIN")

            # 1. Insert order (business data)
            cursor.execute("""
                INSERT INTO orders (id, customer_id, total, status, created_at)
                VALUES (%(id)s, %(customer_id)s, %(total)s, 'pending', NOW())
            """, order_data)

            # 2. Insert event into outbox (same transaction)
            event = {
                "event_type": "OrderCreated",
                "order_id": order_data["id"],
                "customer_id": order_data["customer_id"],
                "total": order_data["total"],
                "timestamp": datetime.utcnow().isoformat()
            }

            cursor.execute("""
                INSERT INTO outbox (aggregate_id, event_type, payload)
                VALUES (%(order_id)s, 'OrderCreated', %(payload)s)
            """, {
                "order_id": order_data["id"],
                "payload": Json(event)
            })

            # 3. Commit both writes atomically
            cursor.execute("COMMIT")

            return order_data["id"]

        except Exception as e:
            cursor.execute("ROLLBACK")
            raise

# Separate process: Outbox Publisher
class OutboxPublisher:
    def __init__(self, db_connection, event_bus):
        self.db = db_connection
        self.event_bus = event_bus

    def poll_and_publish(self):
        """Poll outbox and publish unprocessed events"""
        cursor = self.db.cursor()

        # Fetch unprocessed events
        cursor.execute("""
            SELECT id, aggregate_id, event_type, payload
            FROM outbox
            WHERE processed_at IS NULL
            ORDER BY created_at
            LIMIT 100
            FOR UPDATE SKIP LOCKED  -- Prevent concurrent processing
        """)

        events = cursor.fetchall()

        for event_id, aggregate_id, event_type, payload in events:
            try:
                # Publish to event bus
                self.event_bus.publish(
                    topic=event_type,
                    message=payload
                )

                # Mark as processed
                cursor.execute("""
                    UPDATE outbox
                    SET processed_at = NOW()
                    WHERE id = %s
                """, (event_id,))

                self.db.commit()

            except Exception as e:
                print(f"Failed to publish event {event_id}: {e}")
                self.db.rollback()
                # Event remains unprocessed for retry
```

**Benefits:**
- Guaranteed event delivery
- No message loss on crash
- Atomic business + messaging

**Challenges:**
- Polling overhead
- Cleanup of processed events
- Ordering guarantees

---

## Pattern Selection Guide

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| **Database per Service** | Enforcing service boundaries | Need joins across domains |
| **Event Sourcing** | Audit trail critical | Simple CRUD sufficient |
| **CQRS** | Read/write workloads differ greatly | Single-model works fine |
| **Saga** | Multi-service transactions needed | ACID transactions available |
| **Outbox** | Reliable event publishing required | In-memory events acceptable |

## Combined Example

Modern e-commerce often combines multiple patterns:

1. **Database per Service** — Orders, Inventory, Payments separate
2. **Event Sourcing** — Order lifecycle as events
3. **CQRS** — Read-optimized order summary views
4. **Saga** — Order creation coordinating multiple services
5. **Outbox** — Reliable event publishing from each service
