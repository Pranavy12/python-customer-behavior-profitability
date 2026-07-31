# Customer Behavior and Profitability Analysis (Python)

## Problem Statement
Given ~8,600 orders across 1,200 customers, segment customers by purchase behavior and identify which segments, categories, and channels actually drive profitability — not just revenue volume.

## Dataset
- `customers.csv` — customer signup date, region, acquisition channel
- `orders.csv` — order-level transactions with revenue, discount, refund flags

## Approach
- **RFM segmentation** (Recency, Frequency, Monetary) using quantile-based scoring (`pd.qcut`) to bucket customers into Champions / Loyal / At Risk / Dormant
- **Profitability breakdown** by segment, product category, and acquisition channel using groupby aggregations
- **Pareto analysis** to quantify revenue concentration among top customers

## Key Findings
- **Champions (25% of customers) drive 38.8% of net revenue**, while Dormant customers (25%) contribute only 13.4% — a ~3x value gap between the top and bottom quartile.
- **62% of customers drive 80% of revenue** — closer to a Pareto split than the classic 80/20, meaning revenue is somewhat more distributed but the top segment is still disproportionately valuable, making retention of Champions/Loyal the higher-leverage priority over broad acquisition.
- **Online is the leading revenue channel** (~₹2.65 Cr) followed by Marketplace, but Grocery (via Retail Store, cross-referenced with the SQL leakage project) carries the highest average discount rate — a category/channel combination worth margin review.
- Category revenue is fairly evenly spread (Sports, Beauty, Home & Kitchen, Electronics all within ~₹0.3 Cr of each other) — no single category dominates, so the profitability lever is customer segment and discount discipline, not category mix.

## Files
- `analysis.py` — full analysis script
- `rfm_output.csv` — per-customer RFM scores and segment labels
- `customer_analysis_charts.png` — 4-panel visualization (segment revenue, segment distribution, category revenue, Pareto curve)

## How to Run
```bash
python3 analysis.py
```
