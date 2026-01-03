import duckdb
import pandas as pd
import streamlit as st

DB_PATH = "warehouse/insightpilot.duckdb"

st.set_page_config(page_title="InsightPilot | Executive Overview", layout="wide")
st.title("🚀 InsightPilot — Executive Overview")

con = duckdb.connect(DB_PATH)

# Load daily KPIs
daily = con.execute("""
    SELECT * FROM daily_kpis
""").fetchdf()

# Basic filters
min_date = pd.to_datetime(daily["order_date"]).min()
max_date = pd.to_datetime(daily["order_date"]).max()

start, end = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

mask = (pd.to_datetime(daily["order_date"]) >= pd.to_datetime(start)) & (pd.to_datetime(daily["order_date"]) <= pd.to_datetime(end))
daily_f = daily.loc[mask].copy()

# KPI cards
total_orders = int(daily_f["total_orders"].sum())
total_revenue = float(daily_f["total_revenue"].sum())
aov = float(total_revenue / total_orders) if total_orders else 0.0
on_time = float(daily_f["on_time_rate"].mean()) if len(daily_f) else 0.0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Orders", f"{total_orders:,}")
c2.metric("Total Revenue", f"${total_revenue:,.2f}")
c3.metric("AOV", f"${aov:,.2f}")
c4.metric("Avg On-time Rate", f"{on_time*100:.1f}%")

st.divider()

# Trend chart (Streamlit built-in)
st.subheader("📈 Daily Trends")
st.line_chart(
    daily_f.set_index("order_date")[["total_orders", "total_revenue"]]
)

st.divider()

# Top categories
st.subheader("🏷️ Top Categories (by Revenue)")
cat = con.execute("""
    SELECT category, SUM(total_revenue) AS revenue
    FROM category_kpis
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
""").fetchdf()

st.dataframe(cat, use_container_width=True)

con.close()

