from __future__ import annotations
import config


def _mock_complete(system: str, prompt: str) -> str:
    """Deterministic stand-in used when no ANTHROPIC_API_KEY is configured."""
    if "inference" in system.lower() or "infer" in prompt.lower():
        return (
            "- Revenue grew across all three regions quarter over quarter, with APAC "
            "showing the steepest acceleration (+39% Q1->Q4).\n"
            "- North America remains the largest revenue base but has the highest "
            "customer churn of the three regions, worth flagging to account teams.\n"
            "- EMEA shows the most stable net customer growth (new minus churned), "
            "suggesting retention practices there could be a template for other regions."
        )
    if "summarize" in prompt.lower() or "findings" in system.lower():
        return (
            "- Total revenue across all regions grew from roughly $2.79M in Q1 to "
            "$3.51M in Q4.\n"
            "- APAC had the smallest revenue base but the fastest growth rate.\n"
            "- Churned customers declined in APAC and EMEA across the year but rose "
            "in North America in Q3 before recovering in Q4."
        )
    if "chart" in system.lower() or "extracted" in prompt.lower():
        return (
            "- The revenue chart shows all three regions trending upward from Q1 to "
            "Q4, with North America consistently the largest bar each quarter.\n"
            "- The gap between North America and the other two regions narrows "
            "slightly by Q4 as APAC and EMEA grow faster."
        )
    return "- No mock response configured for this prompt type."


def complete(system: str, prompt: str) -> str:
    """Return an LLM completion for the given system/user prompt."""
    if not config.USE_REAL_LLM:
        return _mock_complete(system, prompt)

    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in response.content if block.type == "text"
    )
