from __future__ import annotations

import os
from typing import Dict, Any

try:
    import requests  # already installed via streamlit dependency chain usually
except Exception:  # pragma: no cover
    requests = None


def llm_enabled() -> bool:
    return os.getenv("LLM_MODE", "off").lower() == "on"


def rewrite_narrative_with_llm(structured: Dict[str, Any]) -> str:
    """
    Rewrite-only wrapper.
    Input is deterministic narrative + metrics.
    Output is a polished executive narrative.
    This function MUST NOT change numbers; it only rewrites.
    """

    # If disabled or missing deps, return deterministic narrative
    if not llm_enabled():
        return deterministic_narrative(structured)

    provider = os.getenv("LLM_PROVIDER", "none").lower()
    api_key = os.getenv("LLM_API_KEY", "").strip()

    if not api_key or provider == "none":
        return deterministic_narrative(structured)

    # Prompt: enforce rewrite-only behavior
    prompt = f"""
You are an analytics communicator. Rewrite the narrative ONLY using the facts below.
Rules:
- Do NOT invent metrics, dates, or categories.
- Do NOT change numbers.
- If something is missing, say it's unknown.
- Keep it concise and executive-friendly.

FACTS (JSON-like):
{structured}

Return a short narrative in 5-8 bullet points.
""".strip()

    # Provider-agnostic placeholder:
    # Implement your preferred provider here (OpenAI/Gemini/Anthropic).
    # For now, we fallback to deterministic to avoid breaking your project.

    return deterministic_narrative(structured)


def deterministic_narrative(structured: Dict[str, Any]) -> str:
    """Fallback deterministic narrative in readable form."""
    parts = []
    for k in ["what_happened", "why_it_happened", "so_what", "next_steps"]:
        v = structured.get(k)
        if v:
            parts.append(f"{k.replace('_', ' ').title()}: {v}")
    return "\n\n".join(parts) if parts else "No narrative available."
