import duckdb
from pathlib import Path

DB_PATH = "warehouse/insightpilot.duckdb"
SQL_PATH = "evaluation/dq_checks.sql"

con = duckdb.connect(DB_PATH)
sql = Path(SQL_PATH).read_text()

# DuckDB can execute multiple SELECTs; fetch results one by one via splitting.
queries = [q.strip() for q in sql.split(";") if q.strip()]

print("\n🧪 Running Data Quality Checks...\n")
for q in queries:
    df = con.execute(q).fetchdf()
    print(df.to_string(index=False))
    print("-" * 60)

con.close()
print("\n✅ DQ checks completed.")

