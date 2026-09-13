"""FastAPI dashboard serving the 7-agent LangGraph pipeline."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from hedge_fund.branding import FOUNDER_CREDIT, FOUNDER_NAME, PRODUCT_NAME
from hedge_fund.demo_data import DEMO_UNIVERSE
from hedge_fund.graph import run_analysis

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Sunkara AI Fund",
    description="7-agent investment research dashboard. Founded by Dineshgopi Sunkara. Paper / research only.",
    version="1.2.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    demo: bool = True
    portfolio_value: float | None = None


class ScanRequest(BaseModel):
    demo: bool = True
    portfolio_value: float | None = None


AGENT_META = [
    {"id": "market_scout", "num": "01", "name": "Market Scout", "section": "1. Market Scout", "icon": "🔭"},
    {"id": "technical", "num": "02", "name": "Technical", "section": "2. Technical Analyst", "icon": "📈"},
    {"id": "fundamental", "num": "03", "name": "Fundamental", "section": "3. Fundamental Analyst", "icon": "📊"},
    {"id": "news", "num": "04", "name": "News", "section": "4. News Analyst", "icon": "📰"},
    {"id": "quant", "num": "05", "name": "Quant", "section": "5. Quant Analyst", "icon": "🧮"},
    {"id": "risk", "num": "06", "name": "Risk Manager", "section": "6. Risk Manager", "icon": "🛡️"},
    {"id": "portfolio", "num": "07", "name": "Portfolio Manager", "section": "7. Portfolio Manager", "icon": "📋"},
]


def _json_safe(obj: Any) -> Any:
    """Recursively coerce values into JSON-serializable forms."""
    if obj is None or isinstance(obj, (str, bool, int)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    # numpy / pandas scalars
    item = getattr(obj, "item", None)
    if callable(item):
        try:
            return _json_safe(item())
        except Exception:
            pass
    return str(obj)


def _verdict_for(agent_id: str, payload: dict[str, Any] | None, result: dict[str, Any]) -> dict[str, Any]:
    data = payload or {}
    if agent_id == "market_scout":
        quote = data.get("quote") or {}
        score = None
        for o in result.get("opportunities") or []:
            if o.get("ticker") == result.get("ticker"):
                score = o.get("opportunity_score")
                break
        return {
            "label": "scouted",
            "score": score,
            "detail": f"${quote.get('price')} · {quote.get('change_pct')}%",
            "tone": "neutral",
        }
    if agent_id == "technical":
        rec = (data.get("recommendation") or "hold").lower()
        tone = "bull" if rec == "buy" else "bear" if rec == "sell" else "neutral"
        return {
            "label": rec.upper(),
            "score": data.get("score"),
            "detail": f"{data.get('bias') or '—'} · {data.get('trend') or '—'}",
            "tone": tone,
        }
    if agent_id == "fundamental":
        rec = (data.get("recommendation") or "hold").lower()
        tone = "bull" if rec == "buy" else "bear" if rec == "sell" else "neutral"
        return {
            "label": rec.upper(),
            "score": data.get("score"),
            "detail": data.get("valuation") or "—",
            "tone": tone,
        }
    if agent_id == "news":
        sent = (data.get("sentiment") or {}).get("label") or "neutral"
        rec = (data.get("recommendation") or "hold").lower()
        tone = "bull" if sent == "bullish" or rec == "buy" else "bear" if sent == "bearish" or rec == "sell" else "neutral"
        return {
            "label": sent.upper(),
            "score": data.get("score"),
            "detail": f"{len(data.get('articles') or [])} headlines",
            "tone": tone,
        }
    if agent_id == "quant":
        rec = (data.get("recommendation") or "hold").lower()
        tone = "bull" if rec == "buy" else "bear" if rec == "sell" else "neutral"
        return {
            "label": f"EDGE {data.get('edge_score')}",
            "score": data.get("edge_score"),
            "detail": f"Win {data.get('win_probability')}%",
            "tone": tone,
        }
    if agent_id == "risk":
        decision = (data.get("decision") or ("REJECT" if result.get("trade_rejected") else "APPROVE")).upper()
        tone = "bear" if decision == "REJECT" else "bull"
        return {
            "label": decision,
            "score": None,
            "detail": (
                f"{float(data.get('position_pct') or 0) * 100:.1f}% size"
                if decision != "REJECT"
                else (data.get("rejection_reason") or result.get("rejection_reason") or "rejected")[:80]
            ),
            "tone": tone,
        }
    if agent_id == "portfolio":
        if result.get("trade_rejected") and not data:
            return {
                "label": "SKIPPED",
                "score": None,
                "detail": "Risk rejected trade",
                "tone": "bear",
            }
        action = (data.get("action") or "HOLD").upper()
        tone = "bull" if "BUY" in action else "bear" if ("SELL" in action or "PASS" in action or "AVOID" in action) else "neutral"
        return {
            "label": action,
            "score": None,
            "detail": f"{float(data.get('allocation_pct') or 0) * 100:.2f}% alloc",
            "tone": tone,
        }
    return {"label": "done", "score": None, "detail": "", "tone": "neutral"}


def shape_response(result: dict[str, Any], *, mode: str = "analyze") -> dict[str, Any]:
    """Normalize graph state into a dashboard-friendly JSON payload."""
    sections = result.get("report_sections") or {}
    agents = []
    for meta in AGENT_META:
        payload = result.get(meta["id"])
        # Portfolio may be missing when risk rejects
        if meta["id"] == "portfolio" and not payload and result.get("trade_rejected"):
            rationale = (
                "Portfolio Manager skipped — trade REJECTED by Risk Manager.\n"
                f"Reason: {result.get('rejection_reason') or 'n/a'}"
            )
            sections = dict(sections)
            sections.setdefault(meta["section"], rationale)
            payload = {
                "action": "PASS (risk rejected)",
                "memo": rationale,
                "summary": rationale,
                "allocation_pct": 0,
                "allocation_dollars": 0,
                "shares": 0,
            }
        rationale = sections.get(meta["section"]) or (payload or {}).get("summary") or ""
        agents.append(
            {
                **meta,
                "status": "done" if payload or rationale else "pending",
                "verdict": _verdict_for(meta["id"], payload if isinstance(payload, dict) else None, result),
                "rationale": rationale,
                "data": payload if isinstance(payload, dict) else {},
            }
        )

    portfolio = result.get("portfolio") or {}
    quant = result.get("quant") or {}
    risk = result.get("risk") or {}
    news = result.get("news") or {}
    scout = result.get("market_scout") or {}

    memo = {
        "recommendation": portfolio.get("action")
        or ("PASS (risk rejected)" if result.get("trade_rejected") else None),
        "allocation_pct": portfolio.get("allocation_pct", risk.get("position_pct")),
        "allocation_dollars": portfolio.get("allocation_dollars", risk.get("position_dollars")),
        "shares": portfolio.get("shares", risk.get("shares")),
        "thesis": scout.get("thesis"),
        "scenarios": quant.get("scenarios") or {},
        "risks": news.get("risks") or risk.get("reasons") or [],
        "catalysts": news.get("catalysts") or [],
        "edge_score": quant.get("edge_score"),
        "win_probability": quant.get("win_probability"),
        "expected_return": quant.get("expected_return"),
        "full_memo": result.get("investment_memo")
        or portfolio.get("memo")
        or sections.get("7. Portfolio Manager"),
        "trade_rejected": bool(result.get("trade_rejected")),
        "rejection_reason": result.get("rejection_reason"),
        "risk_decision": risk.get("decision"),
    }

    quote = scout.get("quote") or (result.get("fundamental") or {}).get("quote") or {}

    return _json_safe(
        {
            "ok": True,
            "mode": mode,
            "ticker": result.get("ticker"),
            "demo": bool(result.get("demo")),
            "portfolio_value": result.get("portfolio_value"),
            "quote": quote,
            "agents": agents,
            "memo": memo,
            "opportunities": result.get("opportunities") or [],
            "report_sections": sections,
            "raw": {
                "market_scout": result.get("market_scout"),
                "technical": result.get("technical"),
                "fundamental": result.get("fundamental"),
                "news": result.get("news"),
                "quant": result.get("quant"),
                "risk": result.get("risk"),
                "portfolio": result.get("portfolio"),
                "trade_rejected": result.get("trade_rejected"),
                "rejection_reason": result.get("rejection_reason"),
                "investment_memo": result.get("investment_memo"),
                "errors": result.get("errors") or [],
            },
        }
    )


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="UI not found")
    return FileResponse(index_path)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "service": "sunkara-ai-fund",
        "product": PRODUCT_NAME,
        "founder": FOUNDER_NAME,
        "founder_credit": FOUNDER_CREDIT,
        "agents": len(AGENT_META),
        "mode": "paper-research",
        "handles_real_money": False,
    }


@app.post("/api/analyze")
def api_analyze(body: AnalyzeRequest):
    ticker = body.ticker.strip().upper()
    if not ticker.isalnum():
        raise HTTPException(status_code=400, detail="Invalid ticker")
    try:
        result = run_analysis(
            ticker,
            demo=body.demo,
            portfolio_value=body.portfolio_value,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc
    return shape_response(result, mode="analyze")


@app.post("/api/scan")
def api_scan(body: ScanRequest):
    try:
        from hedge_fund.tools.market_data import rank_opportunities

        ranked = rank_opportunities(DEMO_UNIVERSE, demo=body.demo)
        if not ranked:
            raise HTTPException(status_code=500, detail="Scan returned no names")
        top = ranked[0]["ticker"]
        result = run_analysis(
            top,
            demo=body.demo,
            portfolio_value=body.portfolio_value,
            tickers=list(DEMO_UNIVERSE),
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Scan failed: {exc}") from exc
    payload = shape_response(result, mode="scan")
    payload["scan_ranking"] = _json_safe(ranked)
    return payload
