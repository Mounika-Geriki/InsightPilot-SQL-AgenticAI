import duckdb
from pathlib import Path

DB_PATH = "warehouse/insightpilot.duckdb"
SQL_FILES = [
    "sql/silver/01_silver_views.sql",
]

con = duckdb.connect(DB_PATH)

for f in SQL_FILES:
    sql = Path(f).read_text()
    con.execute(sql)
    print(f"✅ Executed: {f}")

con.close()
print("🎉 Silver views created.")

