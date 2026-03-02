import re

# Only allow SELECT queries (read-only)
FORBIDDEN = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bATTACH\b",
    r"\bCOPY\b",
    r"\bEXPORT\b",
    r"\bIMPORT\b",
    r"\bPRAGMA\b",
]

def is_safe_sql(sql: str) -> bool:
    if sql is None:
        return False
    s = sql.strip().strip(";")
    # Must start with SELECT or WITH
    if not re.match(r"^(SELECT|WITH)\b", s, flags=re.IGNORECASE):
        return False

    for pat in FORBIDDEN:
        if re.search(pat, s, flags=re.IGNORECASE):
            return False

    return True
