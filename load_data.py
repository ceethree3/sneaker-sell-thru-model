"""
Load inventory.csv and sales.csv into the normalized SQLite database.

Usage:
    python load_data.py                        # creates sellthrough.db
    python load_data.py --db path/to/file.db   # custom db path
    python load_data.py --reset                # drop and recreate tables first
"""

import argparse
import csv
import re
import sqlite3
from pathlib import Path

SCHEMA = Path("sql/schema.sql")
INVENTORY_CSV = Path("data/inventory.csv")
SALES_CSV = Path("data/sales.csv")


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def _ddl_keyword(stmt: str) -> str:
    """Return the leading DDL keyword of a statement, skipping SQL comments."""
    stripped = re.sub(r"--[^\n]*", "", stmt).strip().upper()
    for kw in ("CREATE VIEW", "CREATE TABLE", "CREATE INDEX", "PRAGMA"):
        if stripped.startswith(kw):
            return kw
    return ""


def apply_schema(conn: sqlite3.Connection) -> None:
    sql = SCHEMA.read_text()
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    for stmt in statements:
        kw = _ddl_keyword(stmt)
        if kw == "PRAGMA":
            continue
        elif kw == "CREATE VIEW":
            # Always drop and recreate views so schema changes apply without --reset.
            name = re.sub(r"--[^\n]*", "", stmt).split()[2]
            conn.execute(f"DROP VIEW IF EXISTS {name}")
            conn.execute(stmt)
        elif kw == "CREATE TABLE":
            conn.execute(stmt.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1))
        elif kw == "CREATE INDEX":
            conn.execute(stmt.replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS", 1))
        else:
            conn.execute(stmt)
    conn.commit()


def reset_tables(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = OFF")
    for obj in ("VIEW", "TABLE", "INDEX"):
        rows = conn.execute(
            f"SELECT name FROM sqlite_master WHERE type='{obj.lower()}'"
        ).fetchall()
        for row in rows:
            conn.execute(f"DROP {obj} IF EXISTS {row['name']}")
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")


def load_inventory(conn: sqlite3.Connection) -> tuple[int, int]:
    products_seen: set[str] = set()
    product_rows: list[tuple] = []
    inventory_rows: list[tuple] = []

    with INVENTORY_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            sku = row["sku"]
            if sku not in products_seen:
                products_seen.add(sku)
                product_rows.append((
                    sku,
                    row["vendor_style"],
                    row["brand_desc"],
                    row["sku_desc"],
                    row["vendor"],
                    row["department"],
                ))
            inventory_rows.append((
                sku,
                float(row["size"]),
                row["receive_date"],
                int(row["units_received"]),
                float(row["retail_price"]),
            ))

    conn.executemany(
        "INSERT OR IGNORE INTO products (sku, vendor_style, brand_desc, sku_desc, vendor, department) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        product_rows,
    )
    conn.executemany(
        "INSERT OR IGNORE INTO inventory (sku, size, receive_date, units_received, retail_price) "
        "VALUES (?, ?, ?, ?, ?)",
        inventory_rows,
    )
    conn.commit()
    return len(product_rows), len(inventory_rows)


def load_sales(conn: sqlite3.Connection) -> int:
    sales_rows: list[tuple] = []

    with SALES_CSV.open(newline="") as f:
        for row in csv.DictReader(f):
            sales_rows.append((
                row["sale_id"],
                row["sku"],
                float(row["size"]),
                row["sale_date"],
                int(row["quantity_sold"]),
                float(row["retail_price"]),
                float(row["sale_price"]),
                row["sale_type"],
            ))

    conn.executemany(
        "INSERT OR IGNORE INTO sales "
        "(sale_id, sku, size, sale_date, quantity_sold, retail_price, sale_price, sale_type) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        sales_rows,
    )
    conn.commit()
    return len(sales_rows)


def print_summary(conn: sqlite3.Connection) -> None:
    counts = {
        tbl: conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        for tbl in ("products", "inventory", "sales")
    }
    print(f"  products  : {counts['products']:>6} rows")
    print(f"  inventory : {counts['inventory']:>6} rows")
    print(f"  sales     : {counts['sales']:>6} rows")

    print("\nSell-through preview (top 5 by rate):")
    rows = conn.execute(
        "SELECT brand_desc, sku_desc, units_received, units_sold, sell_through_rate "
        "FROM sku_sell_through ORDER BY sell_through_rate DESC LIMIT 5"
    ).fetchall()
    print(f"  {'Style':<45} {'Rcvd':>6} {'Sold':>6} {'ST%':>6}")
    print(f"  {'-'*45} {'-'*6} {'-'*6} {'-'*6}")
    for r in rows:
        label = f"{r['brand_desc']} / {r['sku_desc']}"[:45]
        print(f"  {label:<45} {r['units_received']:>6} {r['units_sold']:>6} {r['sell_through_rate']:>6.1%}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="sellthrough.db", help="SQLite database file")
    parser.add_argument("--reset", action="store_true", help="Drop all tables and reload from scratch")
    args = parser.parse_args()

    for path in (SCHEMA, INVENTORY_CSV, SALES_CSV):
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    conn = connect(args.db)

    if args.reset:
        print("Resetting database...")
        reset_tables(conn)

    apply_schema(conn)

    print(f"Loading into {args.db}...")
    n_products, n_inventory = load_inventory(conn)
    n_sales = load_sales(conn)
    print(f"  Inserted {n_products} products, {n_inventory} inventory rows, {n_sales} sales rows")

    print("\nDatabase totals:")
    print_summary(conn)
    conn.close()


if __name__ == "__main__":
    main()
