# 📌 InsightPilot — Metrics Dictionary

This document defines the core metrics used in InsightPilot, including business meaning, grain, and SQL lineage.

---

## 1) Total Orders
**Definition:** Count of distinct orders in the selected period.  
**Grain:** Daily (in `daily_kpis`) or overall (dashboard aggregation).  
**Source:** `fact_orders`  
**Logic:**
- `COUNT(DISTINCT order_id)`

---

## 2) Total Revenue (Gross Revenue)
**Definition:** Revenue per order including item price + freight.  
**Grain:** Order-level in `fact_orders`, aggregated daily in `daily_kpis`.  
**Source:** `silver_order_items` → `fact_orders`  
**Logic:**
- `gross_revenue = SUM(price) + SUM(freight_value)` per order

---

## 3) AOV (Average Order Value)
**Definition:** Average gross revenue per order.  
**Grain:** Daily or filtered period.  
**Source:** `daily_kpis` (derived), `fact_orders`  
**Logic:**
- `AOV = total_revenue / total_orders`

---

## 4) On-time Rate (Delivered-only)
**Definition:** Percentage of delivered orders that arrived on or before the estimated delivery date.  
**Grain:** Daily (`daily_sla_kpis`)  
**Source:** `fact_orders` → `daily_sla_kpis`  
**Logic:**
- `on_time_flag = 1 if delivered_date <= estimated_date else 0`
- `on_time_rate_delivered = AVG(on_time_flag)` over delivered orders only

---

## 5) Average Delivery Days (Delivered-only)
**Definition:** Average number of days from purchase to delivery (delivered orders only).  
**Grain:** Daily (`daily_sla_kpis`)  
**Source:** `fact_orders`  
**Logic:**
- `delivery_days = date_diff(delivered_date, purchase_date)`
- `avg_delivery_days = AVG(delivery_days)` over delivered orders only

---

## 6) Category Revenue
**Definition:** Total revenue attributed to product categories.  
**Grain:** Category x Date (`category_kpis`)  
**Source:** `silver_order_items` + `silver_products` + `silver_category_translation`  
**Logic:**
- Join items → products → translation
- `SUM(price + freight_value)` per category

---

## 7) State Revenue
**Definition:** Total revenue by customer state.  
**Grain:** State x Date (`state_kpis`)  
**Source:** `fact_orders`  
**Logic:**
- `SUM(gross_revenue)` grouped by state and date

