"""
Customer Behavior and Profitability Analysis
RFM segmentation + profitability breakdown using pandas/numpy.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.width', 120)

customers = pd.read_csv("customers.csv", parse_dates=["signup_date"])
orders = pd.read_csv("orders.csv", parse_dates=["order_date"])

# Only count non-refunded orders as "real" purchases for behavior analysis
valid_orders = orders[orders["refunded"] == 0].copy()

snapshot_date = orders["order_date"].max() + pd.Timedelta(days=1)

# ---------- RFM ----------
rfm = valid_orders.groupby("customer_id").agg(
    recency=("order_date", lambda x: (snapshot_date - x.max()).days),
    frequency=("order_id", "count"),
    monetary=("net_revenue", "sum")
).reset_index()

rfm["r_score"] = pd.qcut(rfm["recency"], 4, labels=[4,3,2,1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"], 4, labels=[1,2,3,4]).astype(int)
rfm["rfm_score"] = rfm["r_score"] + rfm["f_score"] + rfm["m_score"]

def segment(row):
    if row["rfm_score"] >= 10:
        return "Champions"
    elif row["rfm_score"] >= 8:
        return "Loyal"
    elif row["rfm_score"] >= 6:
        return "At Risk"
    else:
        return "Dormant"

rfm["segment"] = rfm.apply(segment, axis=1)

print("=== RFM Segment Distribution ===")
print(rfm["segment"].value_counts())
print()

# ---------- Profitability by segment ----------
seg_profit = rfm.groupby("segment").agg(
    customers=("customer_id","count"),
    total_revenue=("monetary","sum"),
    avg_revenue_per_customer=("monetary","mean")
).sort_values("total_revenue", ascending=False)
seg_profit["revenue_share_pct"] = (seg_profit["total_revenue"] / seg_profit["total_revenue"].sum() * 100).round(1)
print("=== Profitability by Segment ===")
print(seg_profit.round(2))
print()

# ---------- Profitability by category & channel ----------
merged = valid_orders.merge(rfm[["customer_id","segment"]], on="customer_id", how="left")
cat_profit = merged.groupby("category").agg(
    orders=("order_id","count"),
    revenue=("net_revenue","sum"),
    avg_discount_pct=("discount_pct","mean")
).sort_values("revenue", ascending=False)
cat_profit["avg_discount_pct"] = (cat_profit["avg_discount_pct"]*100).round(1)
print("=== Category Profitability ===")
print(cat_profit.round(2))
print()

channel_profit = merged.groupby("channel").agg(
    orders=("order_id","count"),
    revenue=("net_revenue","sum")
).sort_values("revenue", ascending=False)
print("=== Channel Profitability ===")
print(channel_profit.round(2))

# ---------- Pareto check: what % of customers drive 80% of revenue ----------
rfm_sorted = rfm.sort_values("monetary", ascending=False).reset_index(drop=True)
rfm_sorted["cum_revenue_pct"] = rfm_sorted["monetary"].cumsum() / rfm_sorted["monetary"].sum() * 100
cutoff_idx = (rfm_sorted["cum_revenue_pct"] >= 80).idxmax()
pct_customers_for_80pct_revenue = round((cutoff_idx+1) / len(rfm_sorted) * 100, 1)
print(f"\n=== Pareto Check ===\n{pct_customers_for_80pct_revenue}% of customers drive 80% of revenue")

# ---------- Charts ----------
fig, axes = plt.subplots(2, 2, figsize=(13,10))

seg_profit["total_revenue"].plot(kind="bar", ax=axes[0,0], color="#4C72B0")
axes[0,0].set_title("Revenue by RFM Segment")
axes[0,0].set_ylabel("Net Revenue (Rs)")

rfm["segment"].value_counts().plot(kind="pie", ax=axes[0,1], autopct="%1.0f%%")
axes[0,1].set_title("Customer Count by Segment")
axes[0,1].set_ylabel("")

cat_profit["revenue"].plot(kind="bar", ax=axes[1,0], color="#55A868")
axes[1,0].set_title("Revenue by Category")
axes[1,0].set_ylabel("Net Revenue (Rs)")

rfm_sorted["cum_revenue_pct"].plot(ax=axes[1,1], color="#C44E52")
axes[1,1].axhline(80, linestyle="--", color="gray")
axes[1,1].set_title("Cumulative Revenue Concentration (Pareto)")
axes[1,1].set_xlabel("Customers (sorted by revenue, desc)")
axes[1,1].set_ylabel("Cumulative Revenue %")

plt.tight_layout()
plt.savefig("customer_analysis_charts.png", dpi=150)
print("\nCharts saved to customer_analysis_charts.png")

rfm.to_csv("rfm_output.csv", index=False)
