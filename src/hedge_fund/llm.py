"""Optional Anthropic LLM helper — never called in --demo mode."""

from __future__ import annotations

from typing import Any

from hedge_fund.config import get_settings


def llm_available(demo: bool) -> bool:
    if demo:
        return False
    return get_settings().has_llm


def enrich_text(prompt: str, *, demo: bool, system: str | None = None) -> str | None:
    """Return LLM text or None if unavailable / on error."""
    if not llm_available(demo):
        return None
    settings = get_settings()
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0.2,
            max_tokens=800,
        )
        messages: list[Any] = []
        if system:
            messages.append(SystemMessage(content=system))
        messages.append(HumanMessage(content=prompt))
        resp = llm.invoke(messages)
        content = resp.content
        if isinstance(content, list):
            content = "".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        return str(content).strip()
    except Exception:
        return None
