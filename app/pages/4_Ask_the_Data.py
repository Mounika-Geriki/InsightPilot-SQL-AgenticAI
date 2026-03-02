import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

from agents.sql_agent import run_agent

st.set_page_config(page_title="Ask the Data", layout="wide")

st.title("🤖 Ask the Data")
st.caption("AI-powered analytics copilot for InsightPilot")

st.divider()

# -----------------------------
# Input
# -----------------------------

question = st.text_input(
    "Ask a business question",
    placeholder="Why did revenue spike on 2017-11-24?"
)

run_button = st.button("Run Analysis")

# -----------------------------
# Agent Execution
# -----------------------------

if run_button and question:

    with st.spinner("Analyzing data..."):
        output = run_agent(question)

    st.divider()

    # -----------------------------
    # Plan
    # -----------------------------
    if output.plan:
        st.subheader("🧩 Agent Plan")

        for step in output.plan:
            with st.expander(f"Step: {step.name}"):
                st.write(step.description)
                st.code(step.sql, language="sql")

    # -----------------------------
    # Results
    # -----------------------------
    if output.results:
        st.subheader("📊 Results")

        for name, df in output.results.items():

            st.markdown(f"**{name}**")

            if isinstance(df, pd.DataFrame) and not df.empty:
                st.dataframe(df, width="stretch")
            else:
                st.info("No rows returned.")

    # -----------------------------
    # Summary
    # -----------------------------
    if output.summary:
        st.subheader("📝 Explanation")
        st.success(output.summary)

    # -----------------------------
    # Confidence
    # -----------------------------
    if output.confidence:
        st.subheader("🔎 Confidence Level")
        st.metric("Confidence", output.confidence)

    # -----------------------------
    # Followups
    # -----------------------------
    if output.followups:
        st.subheader("➡️ Suggested Follow-ups")

        for suggestion in output.followups:
            st.write(f"- {suggestion}")

    # -----------------------------
    # Data Source Disclosure
    # -----------------------------
    st.divider()
    st.caption(
        "Data Source: Gold Layer tables (daily_kpis, daily_anomalies, "
        "category_kpis, category_anomalies, state_kpis). "
        "Read-only access enforced via SQL guardrails."
    )
    # -----------------------------
    # Narrative (Deterministic)
    # -----------------------------
    if output.narrative:
        st.subheader("🧠 Deterministic Insight (Source of Truth)")

        st.markdown(f"**What happened:** {output.narrative.get('what_happened','')}")
        st.markdown(f"**Why it happened:** {output.narrative.get('why_it_happened','')}")
        st.markdown(f"**So what:** {output.narrative.get('so_what','')}")
        st.markdown(f"**Next steps:** {output.narrative.get('next_steps','')}")

        if output.narrative.get("top_drivers"):
            st.markdown("**Top drivers:**")
            for d in output.narrative["top_drivers"]:
                st.write(f"- {d}")

    # -----------------------------
    # Optional LLM rewrite
    # -----------------------------
    use_llm = st.toggle("✨ Rewrite as Executive Narrative (Optional LLM)", value=False)

    if use_llm:
        st.subheader("🪄 Executive Narrative (Rewrite Layer)")
        st.info(output.executive_narrative or "LLM is off or not configured. Showing deterministic narrative instead.")

elif run_button and not question:
    st.warning("Please enter a question.")
