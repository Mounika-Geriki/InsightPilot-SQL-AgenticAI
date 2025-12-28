import duckdb

con = duckdb.connect("warehouse/insightpilot.duckdb")
print(con.execute("SHOW TABLES").fetchdf())
con.close()

