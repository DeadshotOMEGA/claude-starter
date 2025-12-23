# Database Migration Safety Guide

PostgreSQL-focused strategies for zero-downtime schema changes.

## Migration Safety Checklist

Before running any migration:

- [ ] **Rollback script ready** — Always have the reverse operation prepared
- [ ] **Tested on production snapshot** — Verify timing and impact on real data volume
- [ ] **Traffic impact assessed** — Know if migration blocks reads/writes and for how long
- [ ] **Deployment window confirmed** — Schedule during low traffic if blocking operations
- [ ] **Monitoring in place** — Watch for lock contention, query timeouts
- [ ] **Incremental approach** — Break large operations into batches when possible

## Safe Column Operations

### Adding Columns

**Safe: Add nullable column**
```sql
-- No locks, instant operation
ALTER TABLE users ADD COLUMN middle_name TEXT;
```

**Safe: Add with default (PostgreSQL 11+)**
```sql
-- PG11+ optimized: no table rewrite
ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active';
```

**Dangerous: Add with default (PostgreSQL <11)**
```sql
-- Rewrites entire table, locks for duration
ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active';

-- Instead: three-step approach
-- 1. Add nullable
ALTER TABLE users ADD COLUMN status TEXT;
-- 2. Backfill in batches (see Large Table Updates)
UPDATE users SET status = 'active' WHERE status IS NULL;
-- 3. Add NOT NULL constraint
ALTER TABLE users ALTER COLUMN status SET NOT NULL;
```

### Adding NOT NULL Constraints

**Three-step safe pattern:**

```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN email TEXT;

-- Step 2: Backfill data (see Large Table Updates for batching)
UPDATE users SET email = old_email WHERE email IS NULL;

-- Step 3: Add constraint with validation
-- Option A: Direct (locks table during scan)
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Option B: Check constraint first (PG12+, safer for large tables)
ALTER TABLE users ADD CONSTRAINT users_email_not_null
  CHECK (email IS NOT NULL) NOT VALID;
-- Validate separately (allows concurrent reads)
ALTER TABLE users VALIDATE CONSTRAINT users_email_not_null;
-- Then add NOT NULL
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users DROP CONSTRAINT users_email_not_null;
```

### Renaming Columns

**NEVER rename directly in production.**

Use expand-contract pattern:

```sql
-- Phase 1: Expand (add new column)
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Phase 2: Dual write (application updates both columns)
-- Deploy application code that writes to both old_name and full_name
UPDATE users SET full_name = old_name WHERE full_name IS NULL;

-- Phase 3: Migrate reads (application reads from full_name)
-- Deploy application code that reads from full_name

-- Phase 4: Contract (remove old column)
-- Only after confirming all code uses full_name
ALTER TABLE users DROP COLUMN old_name;
```

**Timeline:** Weeks or months, not one migration.

### Changing Column Types

**Safe: Expanding types**
```sql
-- varchar to text (instant)
ALTER TABLE users ALTER COLUMN bio TYPE TEXT;

-- Smaller to larger int (instant in most cases)
ALTER TABLE users ALTER COLUMN count TYPE BIGINT;

-- Numeric precision increase
ALTER TABLE products ALTER COLUMN price TYPE NUMERIC(12,2);
```

**Dangerous: Shrinking types**
```sql
-- Requires table rewrite and validation
ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50);

-- Safer: Add constraint first to validate data
ALTER TABLE users ADD CONSTRAINT username_length
  CHECK (LENGTH(username) <= 50);
-- Wait, monitor for violations
-- Then change type
ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50);
ALTER TABLE users DROP CONSTRAINT username_length;
```

**Type conversions requiring USING:**
```sql
-- Explicit conversion (rewrites table)
ALTER TABLE logs
  ALTER COLUMN created_at TYPE TIMESTAMPTZ
  USING created_at AT TIME ZONE 'UTC';
```

## Index Operations

**Always use CONCURRENTLY for production:**

```sql
-- Create index without blocking writes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Drop index without blocking
DROP INDEX CONCURRENTLY idx_users_email;
```

**Gotchas:**
- `CONCURRENTLY` cannot run inside transaction block
- If `CREATE INDEX CONCURRENTLY` fails, leaves INVALID index behind
- Check for invalid indexes: `SELECT * FROM pg_indexes WHERE indexdef LIKE '%INVALID%'`
- Drop invalid indexes before retrying

**Partial indexes for better performance:**
```sql
-- Index only active users
CREATE INDEX CONCURRENTLY idx_users_active
  ON users(email) WHERE status = 'active';
```

## Table Operations

### Adding Tables

```sql
-- Create table (no impact on existing tables)
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  action TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ⚠️ Don't forget Row Level Security if using Supabase/RLS pattern
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_select ON audit_logs
  FOR SELECT USING (auth.uid() = user_id);
```

### Dropping Tables

**Never drop directly. Use two-phase approach:**

```sql
-- Phase 1: Rename to mark for deletion
ALTER TABLE old_users RENAME TO _deprecated_old_users_20240115;

-- Deploy code, monitor for errors referencing old_users
-- Wait days/weeks

-- Phase 2: Actually drop (after confirming no dependencies)
DROP TABLE _deprecated_old_users_20240115;
```

**Check dependencies first:**
```sql
-- Find foreign keys referencing table
SELECT
  tc.table_name,
  kcu.column_name,
  ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND ccu.table_name = 'table_to_drop';
```

## Foreign Key Operations

**Add foreign key without blocking:**

```sql
-- Step 1: Add constraint as NOT VALID (doesn't check existing rows)
ALTER TABLE orders
  ADD CONSTRAINT fk_orders_user_id
  FOREIGN KEY (user_id) REFERENCES users(id)
  NOT VALID;

-- Step 2: Validate separately (allows concurrent operations)
ALTER TABLE orders
  VALIDATE CONSTRAINT fk_orders_user_id;
```

**Why this matters:**
- `NOT VALID` only validates new rows (fast)
- `VALIDATE CONSTRAINT` scans existing rows without blocking writes
- Direct FK addition blocks all writes until validation completes

## Large Table Updates

**Never run unbounded UPDATE on large tables.**

Use batch updates with sleep:

```sql
DO $$
DECLARE
  batch_size INT := 1000;
  affected INT;
BEGIN
  LOOP
    -- Update in batches
    UPDATE users
    SET status = 'active'
    WHERE status IS NULL
      AND id IN (
        SELECT id FROM users
        WHERE status IS NULL
        LIMIT batch_size
      );

    GET DIAGNOSTICS affected = ROW_COUNT;

    -- Log progress
    RAISE NOTICE 'Updated % rows', affected;

    -- Exit when done
    EXIT WHEN affected < batch_size;

    -- Sleep to reduce load (milliseconds)
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

**Tuning batch updates:**
- Start with small batch_size (100-1000)
- Adjust pg_sleep based on load (0.1 - 1.0 seconds)
- Monitor `pg_stat_activity` for blocking queries
- Run during low-traffic windows for large migrations

**Alternative: Background job approach**
```sql
-- Flag rows for update
ALTER TABLE users ADD COLUMN _needs_migration BOOLEAN DEFAULT TRUE;

-- Background process updates in batches
-- Application code handles both old and new values during transition
```

## Rollback Patterns

**Always have rollback ready before migration:**

```sql
-- migration_001_up.sql
BEGIN;
ALTER TABLE users ADD COLUMN middle_name TEXT;
COMMIT;

-- migration_001_down.sql
BEGIN;
ALTER TABLE users DROP COLUMN middle_name;
COMMIT;
```

**For complex migrations, document rollback steps:**

```sql
-- UP: Add NOT NULL with three-step pattern
-- 1. Add column
ALTER TABLE users ADD COLUMN email TEXT;
-- 2. Backfill
UPDATE users SET email = old_email;
-- 3. Add constraint
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- DOWN: Reverse in opposite order
-- 1. Remove constraint
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;
-- 2. (Backfill not needed for rollback)
-- 3. Drop column
ALTER TABLE users DROP COLUMN email;
```

**Test rollback on staging:**
1. Apply migration
2. Verify schema changes
3. Apply rollback
4. Verify schema restored
5. Re-apply migration (should work again)

## General Guidelines

- **Migrations are code** — Version control, code review, testing
- **One change per migration** — Easier to rollback, easier to debug
- **Irreversible operations** — Document clearly, extra caution
- **Test on production-like data** — Timing varies with data volume
- **Monitor during deployment** — Watch for locks, slow queries, errors
- **Communicate** — Alert team before potentially disruptive migrations
