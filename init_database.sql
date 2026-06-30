CREATE TABLE customers (
    id integer PRIMARY KEY,
    email text NOT NULL UNIQUE,
    full_name text NOT NULL,
    created_at timestamptz NOT NULL
);

CREATE TABLE orders (
    id integer PRIMARY KEY,
    order_number text NOT NULL UNIQUE,
    customer_id integer NOT NULL REFERENCES customers(id),
    status text NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled', 'refunded')),
    created_at timestamptz NOT NULL,
    total_amount numeric(12, 2) NOT NULL CHECK (total_amount >= 0),
    currency char(3) NOT NULL DEFAULT 'USD'
);

INSERT INTO customers (id, email, full_name, created_at)
SELECT
    gs,
    'customer' || lpad(gs::text, 6, '0') || '@example.com',
    'Customer ' || gs,
    timestamptz '2025-01-01 00:00:00+00' + ((gs % 365) * interval '1 day')
FROM generate_series(1, 20000) AS gs;

INSERT INTO orders (id, order_number, customer_id, status, created_at, total_amount, currency)
SELECT
    gs,
    'ORD-' || lpad(gs::text, 8, '0'),
    ((gs * 37) % 20000) + 1,
    CASE
        WHEN gs % 20 IN (0, 1, 2, 3, 4, 5, 6, 7, 8) THEN 'paid'
        WHEN gs % 20 IN (9, 10, 11, 12) THEN 'shipped'
        WHEN gs % 20 IN (13, 14, 15) THEN 'pending'
        WHEN gs % 20 IN (16, 17) THEN 'cancelled'
        ELSE 'refunded'
    END,
    timestamptz '2025-10-01 00:00:00+00'
        + ((gs % 180) * interval '1 day')
        + ((gs % 86400) * interval '1 second'),
    round((15 + ((gs * 17) % 25000) / 100.0)::numeric, 2),
    'USD'
FROM generate_series(1, 300000) AS gs;

CREATE INDEX ix_orders_customer_id ON orders(customer_id);
CREATE INDEX ix_orders_created_at ON orders(created_at);

-- Supports the admin search pattern exactly: equality on status, range on created_at,
-- deterministic newest-first ordering, and small limit/offset windows. Included columns
-- let PostgreSQL read the required order fields from the index before joining customers.
CREATE INDEX ix_orders_status_created_at_id_desc
    ON orders(status, created_at DESC, id DESC)
    INCLUDE (order_number, customer_id, total_amount, currency);

ANALYZE customers;
ANALYZE orders;
