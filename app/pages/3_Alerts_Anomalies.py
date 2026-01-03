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

plot_df = daily_f[["order_date", "total_revenue", "total_orders", "revenue_anomaly_flag", "orders_anomaly_flag"]].copy()

# Create marker series: keep value only on anomaly days, else NaN
plot_df["revenue_anomaly_points"] = plot_df.apply(
    lambda r: r["total_revenue"] if r["revenue_anomaly_flag"] == 1 else None, axis=1
)
plot_df["orders_anomaly_points"] = plot_df.apply(
    lambda r: r["total_orders"] if r["orders_anomaly_flag"] == 1 else None, axis=1
)

st.line_chart(plot_df.set_index("order_date")[["total_revenue", "total_orders"]])

st.caption("Anomaly days listed below (z-score ≥ 3). Use the table to see exact dates and scores.")

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
    # Pick strongest revenue anomaly if exists, else strongest orders anomaly
    alerts2 = alerts.copy()
    alerts2["rev_abs"] = alerts2["revenue_zscore"].abs()
    alerts2["ord_abs"] = alerts2["orders_zscore"].abs()

    pick = alerts2.sort_values(["rev_abs", "ord_abs"], ascending=False).iloc[0]
    date_str = str(pd.to_datetime(pick["order_date"]).date())

    bullets = []
    if pd.notna(pick["revenue_zscore"]):
        direction = "spike" if pick["revenue_zscore"] > 0 else "drop"
        bullets.append(
            f"Revenue {direction} on **{date_str}** (z={pick['revenue_zscore']:.2f}) — ${pick['total_revenue']:,.2f} vs rolling baseline."
        )

    if pd.notna(pick["orders_zscore"]):
        direction = "spike" if pick["orders_zscore"] > 0 else "drop"
        bullets.append(
            f"Orders {direction} on **{date_str}** (z={pick['orders_zscore']:.2f}) — {int(pick['total_orders'])} orders."
        )

    if len(cat) > 0:
        top_cat = cat.iloc[0]
        bullets.append(
            f"Top category driver: **{top_cat['category']}** (z={top_cat['category_revenue_zscore']:.2f})."
        )

    for b in bullets:
        st.write(f"- {b}")

con.close()

