import duckdb
import pandas as pd
import streamlit as st

DB_PATH = "warehouse/insightpilot.duckdb"

st.title("🚀 InsightPilot — Executive Overview")

con = duckdb.connect(DB_PATH)

daily = con.execute("SELECT * FROM daily_kpis").fetchdf()
sla = con.execute("SELECT * FROM daily_sla_kpis").fetchdf()

daily["order_date"] = pd.to_datetime(daily["order_date"])
sla["order_date"] = pd.to_datetime(sla["order_date"])

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

mask2 = (sla["order_date"].dt.date >= start) & (sla["order_date"].dt.date <= end)
sla_f = sla.loc[mask2].copy()

total_orders = int(daily_f["total_orders"].sum())
total_revenue = float(daily_f["total_revenue"].sum())
aov = float(total_revenue / total_orders) if total_orders else 0.0

on_time = float(sla_f["on_time_rate_delivered"].mean()) if len(sla_f) else None
avg_del_days = float(sla_f["avg_delivery_days"].mean()) if len(sla_f) else None

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Orders", f"{total_orders:,}")
c2.metric("Total Revenue", f"${total_revenue:,.2f}")
c3.metric("AOV", f"${aov:,.2f}")
c4.metric("On-time Rate (Delivered)", "N/A" if on_time is None else f"{on_time*100:.1f}%")
c5.metric("Avg Delivery Days", "N/A" if avg_del_days is None else f"{avg_del_days:.2f}")

st.divider()
st.subheader("📈 Daily Trends")
st.line_chart(daily_f.set_index("order_date")[["total_orders", "total_revenue"]])

st.divider()
st.subheader("🏷️ Top Categories (by Revenue)")
cat = con.execute("""
    SELECT category, SUM(total_revenue) AS revenue
    FROM category_kpis
    WHERE order_date BETWEEN ? AND ?
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
""", [start, end]).fetchdf()

st.dataframe(cat, use_container_width=True)

con.close()

