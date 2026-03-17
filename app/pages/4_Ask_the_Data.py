import sys
from pathlib import Path

# Ensure project root is in PYTHONPATH
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

from agents.sql_agent import run_agent
from agents.narrative_llm import (
    rewrite_narrative_with_llm,
    deterministic_narrative,
)

st.set_page_config(page_title="Ask the Data", layout="wide")

st.title("🤖 Ask the Data")
st.caption("AI-powered analytics copilot for InsightPilot")

st.divider()

# -----------------------------
# Session state init
# -----------------------------
if "question" not in st.session_state:
    st.session_state.question = ""

if "output" not in st.session_state:
    st.session_state.output = None

# -----------------------------
# Input
# -----------------------------
question = st.text_input(
    "Ask a business question",
    value=st.session_state.question,
    placeholder="Why did revenue spike on 2017-11-24?"
)

run_button = st.button("Run Analysis")

# -----------------------------
# Run agent and persist output
# -----------------------------
if run_button:
    if question:
        with st.spinner("Analyzing data..."):
            st.session_state.question = question
            st.session_state.output = run_agent(question)
    else:
        st.warning("Please enter a question.")

output = st.session_state.output

# -----------------------------
# Render persisted output
# -----------------------------
if output:
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
    # Deterministic Narrative
    # -----------------------------
    if output.narrative:
        st.subheader("🧠 Deterministic Insight (Source of Truth)")
        st.markdown(f"**What happened:** {output.narrative.get('what_happened', '')}")
        st.markdown(f"**Why it happened:** {output.narrative.get('why_it_happened', '')}")
        st.markdown(f"**So what:** {output.narrative.get('so_what', '')}")
        st.markdown(f"**Next steps:** {output.narrative.get('next_steps', '')}")

        if output.narrative.get("top_drivers"):
            st.markdown("**Top drivers:**")
            for d in output.narrative["top_drivers"]:
                st.write(f"- {d}")

        # -----------------------------
        # Optional LLM rewrite
        # -----------------------------
        use_llm = st.toggle(
            "✨ Executive Narrative (Rewrite Layer)",
            value=False,
            key="use_llm_toggle"
        )

        if use_llm:
            st.subheader("🪄 Executive Narrative (AI Rewrite)")
            with st.spinner("Rewriting narrative with LLM..."):
                rewritten = rewrite_narrative_with_llm(output.narrative)

            if rewritten and rewritten.strip():
                st.success(rewritten)
            else:
                st.info(deterministic_narrative(output.narrative))