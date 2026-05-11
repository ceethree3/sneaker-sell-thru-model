-- Shoe Sell-Through Predictive Model
-- SQLite schema
-- Enable foreign key enforcement (must be run per connection in SQLite)
PRAGMA foreign_keys = ON;


-- ─────────────────────────────────────────────
-- Core tables
-- ─────────────────────────────────────────────

-- Style-level product attributes. One row per SKU.
CREATE TABLE products (
    sku          TEXT PRIMARY KEY,
    vendor_style TEXT NOT NULL,   -- manufacturer style number (e.g. FD2596-100)
    brand_desc   TEXT NOT NULL,   -- full brand + style name
    sku_desc     TEXT NOT NULL,   -- short colorway/label
    vendor       TEXT NOT NULL,   -- brand name
    department   TEXT NOT NULL    -- product category (e.g. RETRO BASKETBALL)
);

-- Size-level inventory. One row per SKU + size.
-- retail_price lives here because it can vary by size in real data.
CREATE TABLE inventory (
    sku            TEXT    NOT NULL REFERENCES products(sku),
    size           REAL    NOT NULL,
    receive_date   TEXT    NOT NULL,  -- YYYY-MM-DD
    units_received INTEGER NOT NULL CHECK (units_received > 0),
    retail_price   REAL    NOT NULL CHECK (retail_price > 0),
    PRIMARY KEY (sku, size)
);

-- Individual sales transactions.
CREATE TABLE sales (
    sale_id       TEXT PRIMARY KEY,
    sku           TEXT    NOT NULL REFERENCES products(sku),
    size          REAL    NOT NULL,
    sale_date     TEXT    NOT NULL,  -- YYYY-MM-DD
    quantity_sold INTEGER NOT NULL CHECK (quantity_sold > 0),
    retail_price  REAL    NOT NULL,
    sale_price    REAL    NOT NULL,
    sale_type     TEXT    NOT NULL CHECK (sale_type IN ('full_price', 'markdown')),
    FOREIGN KEY (sku, size) REFERENCES inventory(sku, size)
);


-- ─────────────────────────────────────────────
-- Indexes
-- ─────────────────────────────────────────────

CREATE INDEX idx_inventory_sku  ON inventory (sku);
CREATE INDEX idx_sales_sku      ON sales (sku);
CREATE INDEX idx_sales_sku_size ON sales (sku, size);
CREATE INDEX idx_sales_date     ON sales (sale_date);


-- ─────────────────────────────────────────────
-- Views for sell-through analysis
-- ─────────────────────────────────────────────

-- Sell-through rate per SKU (style level).
-- This is the primary target variable for the predictive model.
CREATE VIEW sku_sell_through AS
SELECT
    p.sku,
    p.vendor,
    p.department,
    p.brand_desc,
    p.sku_desc,
    MIN(i.receive_date)                                                         AS receive_date,
    SUM(i.units_received)                                                       AS units_received,
    COALESCE(SUM(s.quantity_sold), 0)                                           AS units_sold,
    ROUND(
        CAST(COALESCE(SUM(s.quantity_sold), 0) AS REAL) / SUM(i.units_received),
        4
    )                                                                           AS sell_through_rate,
    MAX(s.sale_date)                                                            AS last_sale_date,
    AVG(i.retail_price)                                                         AS avg_retail_price,
    CASE
        WHEN AVG(i.retail_price) <  80  THEN 'budget'
        WHEN AVG(i.retail_price) < 130  THEN 'mid'
        WHEN AVG(i.retail_price) < 175  THEN 'premium'
        ELSE                                 'luxury'
    END                                                                         AS price_tier
FROM products p
JOIN  inventory i ON p.sku = i.sku
LEFT JOIN sales s ON p.sku = s.sku
GROUP BY p.sku, p.vendor, p.department, p.brand_desc, p.sku_desc;


-- Sell-through rate per SKU + size (size run analysis).
CREATE VIEW size_sell_through AS
SELECT
    i.sku,
    i.size,
    i.receive_date,
    i.units_received,
    i.retail_price,
    COALESCE(SUM(s.quantity_sold), 0)                                           AS units_sold,
    ROUND(
        CAST(COALESCE(SUM(s.quantity_sold), 0) AS REAL) / i.units_received,
        4
    )                                                                           AS sell_through_rate
FROM inventory i
LEFT JOIN sales s ON i.sku = s.sku AND i.size = s.size
GROUP BY i.sku, i.size, i.units_received, i.receive_date, i.retail_price;


-- Markdown behavior per SKU: rate and average discount depth.
CREATE VIEW sku_markdown_summary AS
SELECT
    sku,
    SUM(quantity_sold)                                                          AS units_sold,
    SUM(CASE WHEN sale_type = 'markdown' THEN quantity_sold ELSE 0 END)        AS markdown_units,
    ROUND(
        CAST(SUM(CASE WHEN sale_type = 'markdown' THEN quantity_sold ELSE 0 END) AS REAL)
        / NULLIF(SUM(quantity_sold), 0),
        4
    )                                                                           AS markdown_rate,
    ROUND(
        AVG(CASE WHEN sale_type = 'markdown'
            THEN (retail_price - sale_price) / retail_price END),
        4
    )                                                                           AS avg_discount_pct
FROM sales
GROUP BY sku;


-- ─────────────────────────────────────────────
-- Load data from CSVs (run from repo root)
-- ─────────────────────────────────────────────
--
-- sqlite3 sellthrough.db < sql/schema.sql
--
-- Then in the SQLite shell:
--   .mode csv
--   .import data/inventory.csv inventory_raw
--   .import data/sales.csv sales_raw
--
-- Or use the load_data.py script (see project root) to normalize
-- product attributes into the products table before inserting.
