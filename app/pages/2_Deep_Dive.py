import duckdb
import pandas as pd
import streamlit as st

DB_PATH = "warehouse/insightpilot.duckdb"
st.title("🔎 Deep Dive — Filters & Drilldowns")

con = duckdb.connect(DB_PATH)

# Date range bounds from fact_orders
bounds = con.execute("""
    SELECT MIN(order_date) AS min_d, MAX(order_date) AS max_d
    FROM fact_orders
""").fetchdf()

min_date = pd.to_datetime(bounds["min_d"][0]).date()
max_date = pd.to_datetime(bounds["max_d"][0]).date()

start, end = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter options
states = con.execute("SELECT DISTINCT customer_state FROM fact_orders WHERE customer_state IS NOT NULL ORDER BY 1").fetchdf()["customer_state"].tolist()
statuses = con.execute("SELECT DISTINCT order_status FROM fact_orders WHERE order_status IS NOT NULL ORDER BY 1").fetchdf()["order_status"].tolist()

state = st.selectbox("Customer State", ["All"] + states)
status = st.selectbox("Order Status", ["All"] + statuses)

# Category list from category_kpis
cats = con.execute("SELECT DISTINCT category FROM category_kpis ORDER BY 1").fetchdf()["category"].tolist()
category = st.selectbox("Category", ["All"] + cats)

filters = ["order_date BETWEEN ? AND ?"]
params = [start, end]

if state != "All":
    filters.append("customer_state = ?")
    params.append(state)

if status != "All":
    filters.append("order_status = ?")
    params.append(status)

where_clause = " AND ".join(filters)

st.subheader("📌 Filtered KPI Summary")

kpi = con.execute(f"""
    SELECT
      COUNT(DISTINCT order_id) AS orders,
      SUM(gross_revenue) AS revenue,
      AVG(gross_revenue) AS avg_order_value
    FROM fact_orders
    WHERE {where_clause}
""", params).fetchdf()

st.write(kpi)

st.divider()
st.subheader("🏷️ Category Breakdown (Revenue)")

cat_where = "order_date BETWEEN ? AND ?"
cat_params = [start, end]

if category != "All":
    cat_where += " AND category = ?"
    cat_params.append(category)

cat_df = con.execute(f"""
    SELECT category, SUM(total_revenue) AS revenue, SUM(total_orders) AS orders
    FROM category_kpis
    WHERE {cat_where}
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 15
""", cat_params).fetchdf()

st.dataframe(cat_df, use_container_width=True)

st.divider()
st.subheader("🗺️ Top States (Revenue)")

state_df = con.execute(f"""
    SELECT customer_state, SUM(gross_revenue) AS revenue, COUNT(DISTINCT order_id) AS orders
    FROM fact_orders
    WHERE {where_clause}
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 15
""", params).fetchdf()

st.dataframe(state_df, use_container_width=True)

st.divider()
st.subheader("🧾 Recent Orders (Sample)")

orders_df = con.execute(f"""
    SELECT order_id, order_date, customer_state, order_status, gross_revenue, delivery_days
    FROM fact_orders
    WHERE {where_clause}
    ORDER BY order_date DESC
    LIMIT 25
""", params).fetchdf()

st.dataframe(orders_df, use_container_width=True)

con.close()

