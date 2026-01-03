-- ==================================
-- GOLD: Anomalies (Daily + Category)
-- ==================================

-- 1) Daily anomalies using rolling baseline + z-score
-- DuckDB supports window functions; using rolling avg/stddev.
CREATE OR REPLACE VIEW daily_anomalies AS
WITH base AS (
  SELECT
    order_date,
    total_orders,
    total_revenue,
    aov,
    on_time_rate
  FROM daily_kpis
),
stats AS (
  SELECT
    *,
    AVG(total_revenue) OVER (
      ORDER BY order_date
      ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
    ) AS rev_avg_14d,
    STDDEV_SAMP(total_revenue) OVER (
      ORDER BY order_date
      ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
    ) AS rev_std_14d,

    AVG(total_orders) OVER (
      ORDER BY order_date
      ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
    ) AS ord_avg_14d,
    STDDEV_SAMP(total_orders) OVER (
      ORDER BY order_date
      ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
    ) AS ord_std_14d
  FROM base
)
SELECT
  order_date,
  total_orders,
  total_revenue,
  aov,
  on_time_rate,

  rev_avg_14d,
  rev_std_14d,
  CASE
    WHEN rev_std_14d IS NULL OR rev_std_14d = 0 THEN NULL
    ELSE (total_revenue - rev_avg_14d) / rev_std_14d
  END AS revenue_zscore,

  ord_avg_14d,
  ord_std_14d,
  CASE
    WHEN ord_std_14d IS NULL OR ord_std_14d = 0 THEN NULL
    ELSE (total_orders - ord_avg_14d) / ord_std_14d
  END AS orders_zscore,

  CASE
    WHEN rev_std_14d IS NULL OR rev_std_14d = 0 THEN 0
    WHEN ABS((total_revenue - rev_avg_14d) / rev_std_14d) >= 3 THEN 1
    ELSE 0
  END AS revenue_anomaly_flag,

  CASE
    WHEN ord_std_14d IS NULL OR ord_std_14d = 0 THEN 0
    WHEN ABS((total_orders - ord_avg_14d) / ord_std_14d) >= 3 THEN 1
    ELSE 0
  END AS orders_anomaly_flag

FROM stats;


-- 2) Category anomalies (daily revenue per category)
CREATE OR REPLACE VIEW category_anomalies AS
WITH base AS (
  SELECT
    order_date,
    category,
    total_revenue
  FROM category_kpis
),
stats AS (
  SELECT
    *,
    AVG(total_revenue) OVER (
      PARTITION BY category
      ORDER BY order_date
      ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
    ) AS cat_rev_avg_14d,
    STDDEV_SAMP(total_revenue) OVER (
      PARTITION BY category
      ORDER BY order_date
      ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
    ) AS cat_rev_std_14d
  FROM base
)
SELECT
  order_date,
  category,
  total_revenue,
  cat_rev_avg_14d,
  cat_rev_std_14d,
  CASE
    WHEN cat_rev_std_14d IS NULL OR cat_rev_std_14d = 0 THEN NULL
    ELSE (total_revenue - cat_rev_avg_14d) / cat_rev_std_14d
  END AS category_revenue_zscore,
  CASE
    WHEN cat_rev_std_14d IS NULL OR cat_rev_std_14d = 0 THEN 0
    WHEN ABS((total_revenue - cat_rev_avg_14d) / cat_rev_std_14d) >= 3 THEN 1
    ELSE 0
  END AS category_anomaly_flag
FROM stats;

