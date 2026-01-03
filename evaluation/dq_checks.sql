-- =========================
-- DATA QUALITY CHECKS
-- =========================

-- 1) Null / Key checks
SELECT 'silver_orders' AS table_name, 'order_id_nulls' AS check_name,
       SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS bad_rows
FROM silver_orders;

SELECT 'silver_order_items' AS table_name, 'order_id_nulls' AS check_name,
       SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS bad_rows
FROM silver_order_items;

SELECT 'silver_customers' AS table_name, 'customer_id_nulls' AS check_name,
       SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS bad_rows
FROM silver_customers;

-- 2) Duplicate checks
SELECT 'silver_orders' AS table_name, 'duplicate_order_id' AS check_name,
       COUNT(*) - COUNT(DISTINCT order_id) AS bad_rows
FROM silver_orders;

-- 3) Range checks
SELECT 'silver_order_reviews' AS table_name, 'review_score_out_of_range' AS check_name,
       SUM(CASE WHEN review_score < 1 OR review_score > 5 THEN 1 ELSE 0 END) AS bad_rows
FROM silver_order_reviews;

-- 4) Numeric checks
SELECT 'silver_order_items' AS table_name, 'negative_price_or_freight' AS check_name,
       SUM(CASE WHEN price < 0 OR freight_value < 0 THEN 1 ELSE 0 END) AS bad_rows
FROM silver_order_items;

