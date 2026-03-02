import duckdb
import pandas as pd
from pathlib import Path

# Absolute DB path
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "warehouse" / "insightpilot.duckdb"

def run_query(sql: str) -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH))
    try:
        df = con.execute(sql).fetchdf()
    finally:
        con.close()
    return df
