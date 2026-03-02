# ---------------------------------------------------------
# Fix Python path so pytest can find project modules
# ---------------------------------------------------------
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from agents.sql_agent import run_agent


# -----------------------------
# Test 1: Anomaly Explanation
# -----------------------------
def test_anomaly_explanation():

    output = run_agent("Why did revenue spike on 2017-11-24?")

    assert output.intent == "explain_anomaly"
    assert "Revenue increased" in output.summary
    assert output.confidence in ["Very High", "High", "Medium"]


# -----------------------------
# Test 2: KPI Summary
# -----------------------------
def test_kpi_summary():

    output = run_agent("KPI summary")

    assert output.intent == "kpi_summary"
    assert output.results is not None
    assert output.confidence == "High"


# -----------------------------
# Test 3: Top Categories
# -----------------------------
def test_top_categories():

    output = run_agent("Top categories by revenue")

    assert output.intent == "top_categories"
    assert "top_categories" in output.results


# -----------------------------
# Test 4: Missing Date Handling
# -----------------------------
def test_missing_date():

    output = run_agent("Why did revenue spike?")

    assert output.intent == "missing_date"
    assert "YYYY-MM-DD" in output.summary


# ---------------------------------------------------------
# Test 5: Guardrail Protection
# ---------------------------------------------------------
def test_guardrail_protection():
    output = run_agent("Drop table daily_kpis")

    # Should not generate execution plan
    assert output.plan == []
    assert output.intent == "help"
