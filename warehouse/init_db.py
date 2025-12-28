import duckdb
import pandas as pd
from pathlib import Path

# Paths
DATA_PATH = Path("data/raw")
DB_PATH = Path("warehouse/insightpilot.duckdb")

# Connect to DuckDB
con = duckdb.connect(DB_PATH)

# Mapping of raw CSV files to Bronze tables
tables = {
    "customers_raw": "olist_customers_dataset.csv",
    "geolocation_raw": "olist_geolocation_dataset.csv",
    "orders_raw": "olist_orders_dataset.csv",
    "order_items_raw": "olist_order_items_dataset.csv",
    "order_payments_raw": "olist_order_payments_dataset.csv",
    "order_reviews_raw": "olist_order_reviews_dataset.csv",
    "products_raw": "olist_products_dataset.csv",
    "sellers_raw": "olist_sellers_dataset.csv",
    "category_translation_raw": "product_category_name_translation.csv"
}

print("🚀 Initializing InsightPilot Bronze Layer...\n")

for table_name, file_name in tables.items():
    file_path = DATA_PATH / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    df = pd.read_csv(file_path)

    con.execute(f"""
        CREATE OR REPLACE TABLE {table_name} AS
        SELECT * FROM df
    """)

    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"✅ Loaded {table_name:<30} | Rows: {row_count}")

con.close()

print("\n🎉 Bronze layer successfully created!")

