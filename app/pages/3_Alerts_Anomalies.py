import duckdb
import pandas as pd
import streamlit as st

DB_PATH = "warehouse/insightpilot.duckdb"
st.title("🚨 Alerts & Anomalies")

con = duckdb.connect(DB_PATH)

# Load daily anomalies
daily = con.execute("""
    SELECT *
    FROM daily_anomalies
    ORDER BY order_date
""").fetchdf()

daily["order_date"] = pd.to_datetime(daily["order_date"])

min_date = daily["order_date"].min().date()
max_date = daily["order_date"].max().date()

start, end = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

mask = (daily["order_date"].dt.date >= start) & (daily["order_date"].dt.date <= end)
daily_f = daily.loc[mask].copy()

st.subheader("🔔 Daily Alerts")
alerts = daily_f[(daily_f["revenue_anomaly_flag"] == 1) | (daily_f["orders_anomaly_flag"] == 1)].copy()
alerts = alerts.sort_values("order_date", ascending=False)

st.caption("Rule: Anomaly flag triggers when |z-score| ≥ 3 using a 14-day rolling baseline.")
st.dataframe(
    alerts[["order_date", "total_revenue", "revenue_zscore", "total_orders", "orders_zscore", "revenue_anomaly_flag", "orders_anomaly_flag"]],
    use_container_width=True
)

st.divider()
st.subheader("📈 Trend + Anomaly Markers")
st.line_chart(daily_f.set_index("order_date")[["total_revenue", "total_orders"]])

st.divider()
st.subheader("🏷️ Category Anomalies (Top Drivers)")

# Category anomalies in range
cat = con.execute("""
    SELECT order_date, category, total_revenue, category_revenue_zscore
    FROM category_anomalies
    WHERE category_anomaly_flag = 1
      AND order_date BETWEEN ? AND ?
    ORDER BY ABS(category_revenue_zscore) DESC
    LIMIT 30
""", [start, end]).fetchdf()

st.dataframe(cat, use_container_width=True)

st.divider()
st.subheader("🧠 Auto Insight Summary (Rule-based)")

if len(alerts) == 0:
    st.info("No major anomalies detected in the selected range.")
else:
    top = alerts.iloc[0]
    date_str = str(top["order_date"].date())
    rev_z = top["revenue_zscore"]
    ord_z = top["orders_zscore"]

    bullets = []
    if pd.notna(rev_z) and abs(rev_z) >= 3:
        direction = "spike" if rev_z > 0 else "drop"
        bullets.append(f"Revenue anomaly detected on **{date_str}** (z-score: {rev_z:.2f}) — significant {direction} vs 14-day baseline.")
    if pd.notna(ord_z) and abs(ord_z) >= 3:
        direction = "spike" if ord_z > 0 else "drop"
        bullets.append(f"Order volume anomaly detected on **{date_str}** (z-score: {ord_z:.2f}) — significant {direction} vs 14-day baseline.")

    if len(cat) > 0:
        top_cat = cat.iloc[0]
        bullets.append(f"Top category driver: **{top_cat['category']}** (category revenue z-score: {top_cat['category_revenue_zscore']:.2f}).")

    for b in bullets:
        st.write(f"- {b}")

con.close()

