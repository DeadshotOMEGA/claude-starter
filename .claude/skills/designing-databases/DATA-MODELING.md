# Data Modeling Reference

Quick reference for entity-relationship design, normalization, and PostgreSQL constraint patterns.

## Normalization Quick Reference

| Form | Rule | Violation Example | Fix |
|------|------|-------------------|-----|
| **1NF** | Atomic values, no repeating groups | `phone_numbers: "555-1234, 555-5678"` | Separate `phones` table with FK |
| **2NF** | No partial dependencies (all non-key attrs depend on full PK) | `(order_id, product_id) → customer_name` | Move `customer_name` to `orders` |
| **3NF** | No transitive dependencies (non-key attrs independent) | `order → customer_id → customer_city` | Move city to `customers` |
| **BCNF** | Every determinant is a candidate key | `(student, course) → instructor, instructor → dept` | Split into course-instructor table |

**Common violations:**
- **1NF**: CSV in column, arrays of primitives without semantic meaning
- **2NF**: Composite PK with attrs depending on only part of the key
- **3NF**: Derived/calculated columns stored redundantly (denormalize intentionally if needed)

## Entity Design Template

Standard table structure with UUID primary key, audit fields, and soft delete:

```sql
CREATE TABLE entities (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Business Identifier
    slug TEXT UNIQUE NOT NULL,  -- URL-safe, human-readable

    -- Core Attributes
    name TEXT NOT NULL,
    email TEXT,
    status TEXT NOT NULL DEFAULT 'active',

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Audit Fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),

    -- Soft Delete
    deleted_at TIMESTAMPTZ,

    -- Optimistic Locking
    version INTEGER NOT NULL DEFAULT 1,

    -- Constraints
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT positive_version CHECK (version > 0),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'archived'))
);

-- Indexes
CREATE INDEX idx_entities_slug ON entities(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_entities_status ON entities(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_entities_created_at ON entities(created_at DESC);

-- Auto-update timestamp
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Trigger function (create once, reuse everywhere)
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Relationship Patterns

### One-to-Many

**Example:** Customers → Orders

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_number TEXT UNIQUE NOT NULL,
    total NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT positive_total CHECK (total >= 0)
);

-- Index foreign key for join performance
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

**Key decisions:**
- `ON DELETE CASCADE` — Delete orders when customer deleted
- `ON DELETE RESTRICT` — Prevent customer deletion if orders exist
- `ON DELETE SET NULL` — Orphan orders (customer_id becomes NULL)

### Many-to-Many (Junction Table)

**Example:** Products ↔ Categories

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    price NUMERIC(10,2) NOT NULL,

    CONSTRAINT positive_price CHECK (price >= 0)
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE
);

-- Junction table
CREATE TABLE product_categories (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,

    -- Optional: ordering, featured status
    display_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (product_id, category_id),

    -- Ensure only one primary category per product
    CONSTRAINT one_primary_per_product UNIQUE (product_id, is_primary)
        WHERE is_primary = true
);

-- Indexes for both directions
CREATE INDEX idx_product_categories_category ON product_categories(category_id);
CREATE INDEX idx_product_categories_product ON product_categories(product_id);
```

### Self-Referential (Hierarchies)

**Example:** Categories with parent_id

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    parent_id UUID REFERENCES categories(id) ON DELETE CASCADE,

    -- Prevent cycles
    CONSTRAINT no_self_reference CHECK (id != parent_id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for hierarchy traversal
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

**Advanced: ltree for hierarchies**

```sql
CREATE EXTENSION IF NOT EXISTS ltree;

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    path ltree NOT NULL,  -- e.g., 'electronics.computers.laptops'

    CONSTRAINT unique_path UNIQUE (path)
);

-- Index for hierarchy queries
CREATE INDEX idx_categories_path ON categories USING GIST (path);

-- Find all descendants
SELECT * FROM categories WHERE path <@ 'electronics.computers';

-- Find all ancestors
SELECT * FROM categories WHERE path @> 'electronics.computers.laptops';
```

## Constraint Patterns

### Email Validation

```sql
CONSTRAINT valid_email CHECK (
    email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)
```

### Phone Validation (E.164 Format)

```sql
CONSTRAINT valid_phone CHECK (
    phone ~ '^\+[1-9]\d{1,14}$'  -- +12125551234
)
```

### Positive Amounts

```sql
CONSTRAINT positive_amount CHECK (amount > 0)
CONSTRAINT non_negative_quantity CHECK (quantity >= 0)
```

### Enum-Like CHECK Constraints

```sql
-- Simple enum
CONSTRAINT valid_status CHECK (status IN ('draft', 'published', 'archived'))

-- Case-insensitive enum
CONSTRAINT valid_priority CHECK (LOWER(priority) IN ('low', 'medium', 'high'))
```

**When to use CHECK vs ENUM type:**
- **CHECK**: Values may change, want flexibility, simple validation
- **ENUM**: Values are stable, want type safety, performance critical

### Cross-Column Constraints

```sql
-- Date range validation
CONSTRAINT valid_date_range CHECK (end_date >= start_date)

-- Mutual exclusivity
CONSTRAINT one_id_required CHECK (
    (user_id IS NOT NULL AND team_id IS NULL) OR
    (user_id IS NULL AND team_id IS NOT NULL)
)

-- Conditional requirements
CONSTRAINT shipping_info_required CHECK (
    (status != 'shipped') OR
    (status = 'shipped' AND shipping_address IS NOT NULL)
)
```

### Conditional UNIQUE with Partial Index

```sql
-- Only enforce uniqueness for active records
CREATE UNIQUE INDEX idx_users_email_unique
    ON users(email)
    WHERE deleted_at IS NULL;

-- One primary per parent
CREATE UNIQUE INDEX idx_one_primary_per_order
    ON order_items(order_id)
    WHERE is_primary = true;

-- Case-insensitive unique
CREATE UNIQUE INDEX idx_users_username_unique
    ON users(LOWER(username));
```

## Common Patterns

### Multi-Tenancy

```sql
CREATE TABLE tenant_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- All queries MUST filter by tenant_id
    -- Enforce with RLS policies
);

-- Index for tenant isolation
CREATE INDEX idx_tenant_data_tenant ON tenant_data(tenant_id);

-- Row-Level Security
ALTER TABLE tenant_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON tenant_data
    USING (tenant_id = current_setting('app.tenant_id')::UUID);
```

### Audit Trail

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger to populate audit log
CREATE TRIGGER audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON entities
    FOR EACH ROW
    EXECUTE FUNCTION log_audit();
```

### Soft Delete with Unique Constraints

```sql
-- Allow reusing email after soft delete
CREATE UNIQUE INDEX idx_users_email_active
    ON users(email)
    WHERE deleted_at IS NULL;

-- Query pattern: always filter soft-deleted
CREATE VIEW active_users AS
    SELECT * FROM users WHERE deleted_at IS NULL;
```

## Performance Considerations

**Index foreign keys:**
```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

**Partial indexes for common queries:**
```sql
CREATE INDEX idx_orders_pending ON orders(created_at DESC)
    WHERE status = 'pending';
```

**Covering indexes:**
```sql
CREATE INDEX idx_users_lookup ON users(email) INCLUDE (name, status);
```

**JSONB indexes:**
```sql
-- GIN index for JSONB containment
CREATE INDEX idx_entities_metadata ON entities USING GIN (metadata);

-- Expression index for specific key
CREATE INDEX idx_entities_tags ON entities ((metadata->>'tags'));
```

## References

- PostgreSQL CHECK Constraints: https://www.postgresql.org/docs/current/ddl-constraints.html
- ltree Extension: https://www.postgresql.org/docs/current/ltree.html
- Row-Level Security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
