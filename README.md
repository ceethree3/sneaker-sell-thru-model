# Sneaker Sell-Through Risk Model

A binary classifier that predicts whether a shoe style will hit a healthy 
sell-through rate at the moment inventory is received -- before a single 
unit sells.

## Problem

Every markdown decision in retail comes too late. By the time you know a 
shoe isn't selling, you've already lost margin. This model flags sell-through 
risk on day one using only signals available at receipt time, giving merchants 
earlier and more confident inventory decisions.

## Results

- 0.934 ROC-AUC
- 94% recall on healthy styles (32 of 34 correctly identified)
- 412 of 466 at-risk styles correctly flagged
- Buyer order quantity identified as dominant signal at 54% feature importance
- Evaluated using Leave-One-Out cross-validation across 500 synthetic SKUs

## Model Output

Each SKU receives one of four action buckets at receipt time:

| Bucket | Action |
|---|---|
| Reorder | Strong sell-through predicted -- plan replenishment early |
| Monitor | Mid-tier signal -- watch velocity in first 2 weeks |
| Discount | At-risk -- promotional cadence recommended |
| Return / Clear | High risk -- initiate return or clearance immediately |

## Features

Inputs available at receipt time only -- no sales history required:

- Vendor
- Department
- Price tier
- Average retail price
- Units received (buyer order quantity)
- Receive month

## Data

Mock data modeled after real retail inventory and sales patterns. 500 synthetic 
SKUs across 5 departments and 7 vendors. Data lives in `/data`. Schema defined 
in `/sql/schema.sql`.

## Tools

- Python (Pandas, NumPy, Scikit-learn)
- Random Forest Classifier
- SQLite
- Jupyter Notebook

## Project Structure

```
sneaker-sell-thru-model/
├── data/
│   ├── inventory.csv
│   └── sales.csv
├── models/
│   └── model.pkl
├── notebooks/
│   ├── eda.ipynb
│   ├── results.ipynb
│   └── business_case.ipynb
├── sql/
│   └── schema.sql
├── generate_data_v2.py
├── train_model.py
└── load_data.py
```

- Jupyter Notebook

