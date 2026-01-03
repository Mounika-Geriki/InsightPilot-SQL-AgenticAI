-- =========================
-- GOLD LAYER: Facts + KPIs
-- =========================

-- 1) Fact Orders (grain: order_id)
-- Revenue is computed from order_items (price + freight)
-- Payment is computed from payments (sum of payment_value)
CREATE OR REPLACE VIEW fact_orders AS
WITH item_revenue AS (
  SELECT
    order_id,
    SUM(price) AS items_revenue,
    SUM(freight_value) AS freight_revenue
  FROM silver_order_items
  GROUP BY 1
),
payments AS (
  SELECT
    order_id,
    SUM(payment_value) AS total_payment
  FROM silver_order_payments
  GROUP BY 1
)
SELECT
  o.order_id,
  o.customer_id,
  c.customer_unique_id,
  c.customer_city,
  c.customer_state,
  o.order_status,
  DATE(o.order_purchase_ts) AS order_date,

  -- revenue measures
  COALESCE(ir.items_revenue, 0) AS items_revenue,
  COALESCE(ir.freight_revenue, 0) AS freight_revenue,
  COALESCE(ir.items_revenue, 0) + COALESCE(ir.freight_revenue, 0) AS gross_revenue,

  -- payment measure
  COALESCE(p.total_payment, 0) AS total_payment,

  -- delivery metrics
  o.order_purchase_ts,
  o.order_delivered_customer_ts,
  o.order_estimated_delivery_ts,

  CASE
    WHEN o.order_delivered_customer_ts IS NULL THEN NULL
    ELSE DATE_DIFF('day', DATE(o.order_purchase_ts), DATE(o.order_delivered_customer_ts))
  END AS delivery_days,

  CASE
    WHEN o.order_delivered_customer_ts IS NULL OR o.order_estimated_delivery_ts IS NULL THEN NULL
    WHEN DATE(o.order_delivered_customer_ts) <= DATE(o.order_estimated_delivery_ts) THEN 1
    ELSE 0
  END AS on_time_flag

FROM silver_orders o
LEFT JOIN silver_customers c ON o.customer_id = c.customer_id
LEFT JOIN item_revenue ir ON o.order_id = ir.order_id
LEFT JOIN payments p ON o.order_id = p.order_id
WHERE o.order_purchase_ts IS NOT NULL;


-- 2) Daily KPIs (grain: order_date)
CREATE OR REPLACE VIEW daily_kpis AS
SELECT
  order_date,
  COUNT(DISTINCT order_id) AS total_orders,
  SUM(gross_revenue) AS total_revenue,
  CASE WHEN COUNT(DISTINCT order_id) = 0 THEN 0
       ELSE SUM(gross_revenue) / COUNT(DISTINCT order_id) END AS aov,
  AVG(on_time_flag) AS on_time_rate
FROM fact_orders
GROUP BY 1
ORDER BY 1;


-- 3) Category KPIs (grain: category x date)
CREATE OR REPLACE VIEW category_kpis AS
WITH order_category AS (
  SELECT
    oi.order_id,
    COALESCE(ct.product_category_name_english, p.product_category_name, 'unknown') AS category,
    SUM(oi.price + oi.freight_value) AS revenue
  FROM silver_order_items oi
  LEFT JOIN silver_products p ON oi.product_id = p.product_id
  LEFT JOIN silver_category_translation ct ON p.product_category_name = ct.product_category_name
  GROUP BY 1,2
)
SELECT
  fo.order_date,
  oc.category,
  COUNT(DISTINCT fo.order_id) AS total_orders,
  SUM(oc.revenue) AS total_revenue
FROM fact_orders fo
JOIN order_category oc ON fo.order_id = oc.order_id
GROUP BY 1,2
ORDER BY 1,2;


-- 4) State KPIs (grain: state x date)
CREATE OR REPLACE VIEW state_kpis AS
SELECT
  order_date,
  customer_state,
  COUNT(DISTINCT order_id) AS total_orders,
  SUM(gross_revenue) AS total_revenue,
  AVG(on_time_flag) AS on_time_rate
FROM fact_orders
GROUP BY 1,2
ORDER BY 1,2;

-- 5) Daily SLA KPIs (delivered-only)
CREATE OR REPLACE VIEW daily_sla_kpis AS
SELECT
  order_date,
  COUNT(DISTINCT order_id) AS delivered_orders,
  AVG(on_time_flag) AS on_time_rate_delivered,
  AVG(delivery_days) AS avg_delivery_days
FROM fact_orders
WHERE order_delivered_customer_ts IS NOT NULL
GROUP BY 1
ORDER BY 1;

