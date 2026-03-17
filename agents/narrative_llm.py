from __future__ import annotations

import os
from typing import Dict, Any
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

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
    print("LLM CALLED")
    fallback = deterministic_narrative(structured)

    # If disabled, return deterministic narrative
    if not llm_enabled():
        return fallback

    provider = os.getenv("LLM_PROVIDER", "none").lower()
    api_key = os.getenv("LLM_API_KEY", "").strip()

    if not api_key or provider == "none":
        return fallback

    # Prompt: enforce rewrite-only behavior
    prompt = f"""
You are an analytics communicator. Rewrite the narrative ONLY using the facts below.

Rules:
- Do NOT invent metrics, dates, categories, or causes.
- Do NOT change numbers.
- Do NOT add assumptions.
- If something is missing, say it is unknown.
- Keep it concise and executive-friendly.
- Return a short narrative in 5-8 bullet points.

FACTS:
{structured}
""".strip()

    try:
        if provider == "openai":
            if OpenAI is None:
                return fallback

            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a business analytics assistant. "
                            "You only rewrite provided facts into a polished executive narrative. "
                            "You never change numbers, invent insights, or add unsupported claims."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
            )

            content = response.choices[0].message.content
            return content.strip() if content else fallback

        # Future providers can be added here
        # elif provider == "gemini":
        #     ...
        # elif provider == "claude":
        #     ...

        return fallback

    except Exception:
        return fallback


def deterministic_narrative(structured: Dict[str, Any]) -> str:
    """Fallback deterministic narrative in readable form."""
    parts = []

    for k in ["what_happened", "why_it_happened", "so_what", "next_steps"]:
        v = structured.get(k)
        if v:
            parts.append(f"{k.replace('_', ' ').title()}: {v}")

    if structured.get("top_drivers"):
        top_drivers = "\n".join([f"- {driver}" for driver in structured["top_drivers"]])
        parts.append(f"Top Drivers:\n{top_drivers}")

    return "\n\n".join(parts) if parts else "No narrative available."
