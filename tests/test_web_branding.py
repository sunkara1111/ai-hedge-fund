"""Branding and FastAPI contract tests for Dinesh AI Fund."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from hedge_fund.branding import (
    FOUNDER_CREDIT,
    FOUNDER_NAME,
    FOUNDER_TITLE,
    PAGES_URL,
    PRODUCT_NAME,
    SHARE_TEXT,
    SITEMAP_URL,
)
from hedge_fund.web.app import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_health_branding_and_contract():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "dinesh-ai-fund"
    assert data["product"] == PRODUCT_NAME
    assert data["founder"] == FOUNDER_NAME
    assert data["founder_credit"] == FOUNDER_CREDIT
    assert data["agents"] == 7
    assert data["handles_real_money"] is False
    assert data["mode"] == "paper-research"


def test_index_has_product_founder_and_seo():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert PRODUCT_NAME in html
    assert FOUNDER_NAME in html
    assert FOUNDER_CREDIT in html
    assert FOUNDER_TITLE in html
    assert "Coming Soon" not in html
    assert "og:title" in html
    assert "og:locale" in html
    assert "twitter:card" in html
    assert "og-image.png" in html
    assert "Paper / research only" in html
    assert "not financial advice" in html.lower()
    assert "does not handle real money" in html.lower()
    assert "AI Hedge Fund" not in html
    assert "Sunkara AI Fund" not in html
    assert (ROOT / "docs" / "robots.txt").exists()
    robots = (ROOT / "docs" / "robots.txt").read_text()
    assert "Allow: /" in robots
    assert f"Sitemap: {SITEMAP_URL}" in robots
    assert (ROOT / "docs" / "sitemap.xml").exists()
    sitemap = (ROOT / "docs" / "sitemap.xml").read_text()
    assert f"<loc>{PAGES_URL}</loc>" in sitemap
    assert SITEMAP_URL in html
    assert 'href="/sitemap.xml"' not in html
    assert "application/ld+json" in html
    assert "Dineshgopi Sunkara" in html
    assert 'id="faq"' in html or "FAQ" in html
    assert 'id="contact"' in html or "Contact" in html
    assert "SoftwareApplication" in html
    assert "Organization" in html
    assert "Built with Claude" not in html
    assert "7-agent research floor" in html
    assert SHARE_TEXT in html


def test_analyze_tsla_demo():
    response = client.post("/api/analyze", json={"ticker": "TSLA", "demo": True})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["ticker"] == "TSLA"
    assert data["demo"] is True
    assert len(data["agents"]) == 7
    assert data["memo"]["recommendation"]
    assert {agent["id"] for agent in data["agents"]} == {
        "market_scout",
        "technical",
        "fundamental",
        "news",
        "quant",
        "risk",
        "portfolio",
    }


def test_scan_demo():
    response = client.post("/api/scan", json={"demo": True})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["mode"] == "scan"
    assert data["scan_ranking"]
    assert len(data["agents"]) == 7
    assert data["ticker"]


def test_analyze_rejects_invalid_ticker():
    response = client.post("/api/analyze", json={"ticker": "BAD TICKER", "demo": True})
    assert response.status_code == 400


def test_docs_showcase_assets_and_branding():
    html = (ROOT / "docs" / "index.html").read_text()
    assert PRODUCT_NAME in html
    assert FOUNDER_CREDIT in html
    assert FOUNDER_TITLE in html
    assert "Coming Soon" not in html
    assert "sample-analysis.json" in html or "Sample / demo analysis" in html or 'id="examples"' in html
    assert "og:image" in html
    assert "og:locale" in html
    assert "Sample examples" in html
    assert 'id="examples"' in html
    assert "sample examples" in html.lower()
    assert "not financial advice" in html.lower()
    assert SHARE_TEXT in html
    sample = json.loads((ROOT / "docs" / "sample-analysis.json").read_text())
    assert sample["ticker"] == "TSLA"
    assert sample["demo"] is True
    assert len(sample["agents"]) == 7
    nvda = json.loads((ROOT / "docs" / "sample-nvda.json").read_text())
    assert nvda["ticker"] == "NVDA"
    assert nvda["demo"] is True
    assert len(nvda["agents"]) == 7
    assert nvda["memo"]["recommendation"]
    reject = json.loads((ROOT / "docs" / "sample-reject.json").read_text())
    assert reject["demo"] is True
    assert len(reject["agents"]) == 7
    assert reject["memo"].get("trade_rejected") is True or "REJECT" in reject["memo"].get("recommendation", "").upper() or "PASS" in reject["memo"].get("recommendation", "").upper()
    risk = next(a for a in reject["agents"] if a["id"] == "risk")
    assert risk["verdict"]["label"] == "REJECT"
    gallery = json.loads((ROOT / "docs" / "sample-examples.json").read_text())
    assert len(gallery["examples"]) >= 3
    ids = {e["id"] for e in gallery["examples"]}
    assert {"tsla", "nvda", "reject"} <= ids
    assert (ROOT / "docs" / "og-image.png").exists()
    assert (ROOT / "docs" / "og-square.png").exists()
    assert (ROOT / "docs" / ".nojekyll").exists()
    assert "How it works" in html
    assert "Combined Result" in html or "Final memo" in html
    assert "Market Scout" in html
    assert "Technical Analyst" in html
    assert "Dinesh AI Fund" in html
    assert "Sunkara AI Fund" not in html
    assert "Built with Claude" not in html
    assert (ROOT / "docs" / "robots.txt").exists()
    robots = (ROOT / "docs" / "robots.txt").read_text()
    assert "Allow: /" in robots
    assert f"Sitemap: {SITEMAP_URL}" in robots
    assert (ROOT / "docs" / "sitemap.xml").exists()
    sitemap = (ROOT / "docs" / "sitemap.xml").read_text()
    assert f"<loc>{PAGES_URL}</loc>" in sitemap
    assert sitemap.count("<loc>") == 1
    assert "sample-nvda.json" not in sitemap
    assert "sample-reject.json" not in sitemap
    assert SITEMAP_URL in html
    assert 'href="/sitemap.xml"' not in html
    assert not (ROOT / "sitemap.xml").exists()
    not_found = (ROOT / "docs" / "404.html").read_text()
    assert PRODUCT_NAME in not_found
    assert FOUNDER_CREDIT in not_found
    assert "Coming Soon" not in not_found
    assert "application/ld+json" in html
    assert "Dineshgopi Sunkara" in html
    assert 'id="faq"' in html or "FAQ" in html
    assert 'id="contact"' in html or "Contact" in html
    assert "SoftwareApplication" in html
    assert "Organization" in html
    app_js = (ROOT / "docs" / "app.js").read_text()
    assert "sample-examples.json" in app_js
    assert "sample-nvda.json" in app_js
    assert "sample-reject.json" in app_js


def test_dashboard_serves_hero_asset():
    response = client.get("/assets/hero-orbit.png")
    assert response.status_code == 200
    assert "image" in (response.headers.get("content-type") or "")


def test_social_images_dimensions():
    from PIL import Image

    landscape = Image.open(ROOT / "src/hedge_fund/web/static/og-image.png")
    square = Image.open(ROOT / "src/hedge_fund/web/static/og-square.png")
    assert landscape.size == (1200, 630)
    assert square.size == (1080, 1080)
