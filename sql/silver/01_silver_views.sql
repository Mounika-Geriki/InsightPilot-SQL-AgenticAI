-- =========================
-- SILVER LAYER: Clean Views
-- =========================

-- Orders
CREATE OR REPLACE VIEW silver_orders AS
SELECT
  order_id,
  customer_id,
  order_status,
  CAST(order_purchase_timestamp AS TIMESTAMP) AS order_purchase_ts,
  CAST(order_approved_at AS TIMESTAMP)        AS order_approved_ts,
  CAST(order_delivered_carrier_date AS TIMESTAMP) AS order_delivered_carrier_ts,
  CAST(order_delivered_customer_date AS TIMESTAMP) AS order_delivered_customer_ts,
  CAST(order_estimated_delivery_date AS TIMESTAMP) AS order_estimated_delivery_ts
FROM orders_raw
WHERE order_id IS NOT NULL;

-- Order Items
CREATE OR REPLACE VIEW silver_order_items AS
SELECT
  order_id,
  order_item_id,
  product_id,
  seller_id,
  CAST(shipping_limit_date AS TIMESTAMP) AS shipping_limit_ts,
  CAST(price AS DOUBLE)    AS price,
  CAST(freight_value AS DOUBLE) AS freight_value
FROM order_items_raw
WHERE order_id IS NOT NULL;

-- Customers
CREATE OR REPLACE VIEW silver_customers AS
SELECT
  customer_id,
  customer_unique_id,
  customer_zip_code_prefix,
  customer_city,
  customer_state
FROM customers_raw
WHERE customer_id IS NOT NULL;

-- Payments
CREATE OR REPLACE VIEW silver_order_payments AS
SELECT
  order_id,
  payment_sequential,
  payment_type,
  CAST(payment_installments AS INTEGER) AS payment_installments,
  CAST(payment_value AS DOUBLE) AS payment_value
FROM order_payments_raw
WHERE order_id IS NOT NULL;

-- Products
CREATE OR REPLACE VIEW silver_products AS
SELECT
  product_id,
  product_category_name,
  CAST(product_name_lenght AS INTEGER)        AS product_name_length,
  CAST(product_description_lenght AS INTEGER) AS product_description_length,
  CAST(product_photos_qty AS INTEGER)         AS product_photos_qty,
  CAST(product_weight_g AS DOUBLE)            AS product_weight_g,
  CAST(product_length_cm AS DOUBLE)           AS product_length_cm,
  CAST(product_height_cm AS DOUBLE)           AS product_height_cm,
  CAST(product_width_cm AS DOUBLE)            AS product_width_cm
FROM products_raw
WHERE product_id IS NOT NULL;

-- Sellers
CREATE OR REPLACE VIEW silver_sellers AS
SELECT
  seller_id,
  seller_zip_code_prefix,
  seller_city,
  seller_state
FROM sellers_raw
WHERE seller_id IS NOT NULL;

-- Reviews
CREATE OR REPLACE VIEW silver_order_reviews AS
SELECT
  review_id,
  order_id,
  CAST(review_score AS INTEGER) AS review_score,
  CAST(review_creation_date AS TIMESTAMP) AS review_creation_ts,
  CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_ts
FROM order_reviews_raw
WHERE order_id IS NOT NULL;

-- Category Translation
CREATE OR REPLACE VIEW silver_category_translation AS
SELECT
  product_category_name,
  product_category_name_english
FROM category_translation_raw
WHERE product_category_name IS NOT NULL;

