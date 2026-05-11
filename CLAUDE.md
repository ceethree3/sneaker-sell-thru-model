# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Predictive model for sneaker sell-through rates at the store level. The target variable is `sell_through_rate` (units sold / units received) per SKU. Outputs are predicted sell-through percentages, risk flags for underperformers, and reorder/discount recommendations.

## Commands

**Generate mock data** (overwrites `data/inventory.csv` and `data/sales.csv`):
```bash
python generate_data.py
```

No build system, test framework, or `requirements.txt` exists yet. Required libraries: `pandas`, `scikit-learn`, `sqlite3` (stdlib), `jupyter`.

## Architecture & Phases

The project follows a linear pipeline — each phase feeds the next:

1. **SQL Schema** (`sql/schema.sql` — not yet created): SQLite tables for inventory, sales transactions, and product attributes
2. **Python Model** (`notebooks/` or a `.py` script — not yet created): Load CSVs/SQLite → feature engineering → scikit-learn model → predictions
3. **Jupyter Notebook** (`notebooks/` — empty): Analysis, visualizations, model results
4. **Business Case** (not yet started): Retail-audience framing of findings

**Current status:** Only data generation is complete. Phase 1 has not started.

## Data

Mock data lives in `data/`. Seeded with `random.seed(42)` for reproducibility.

`inventory.csv` schema: `receive_date, sku, vendor_style, brand_desc, department, sku_desc, vendor, size, units_received, retail_price`

`sales.csv` schema: `sale_id, sku, size, sale_date, quantity_sold, retail_price, sale_price, sale_type`

Performance tiers in `generate_data.py` drive sell-through rates and markdown logic:
- `hot`: 85–98% sell-through, 3% markdown rate
- `moderate`: 55–75%, 15% markdown rate
- `slow`: 30–54%, 35% markdown rate
- `dead`: 5–25%, 60% markdown rate

The `sell_through_rate` for a SKU must be computed by joining `inventory` and `sales` on `sku` + `size`.
