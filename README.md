# AI Hedge Fund

A **complete, runnable** multi-agent investment research system. Seven specialized agents collaborate via [LangGraph](https://github.com/langchain-ai/langgraph) to scout opportunities, analyze technicals/fundamentals/news, score edge, enforce risk limits, and produce an investment memo.

> **Disclaimer — paper / research only.** This project is for education and experimentation. It is **not financial advice**. Do not use it to make real trading decisions without independent due diligence. Simulated scores and demo data do not predict future results.

## Architecture

```mermaid
flowchart TD
    Start([START]) --> MS[Market Scout]
    MS --> TA[Technical Analyst]
    MS --> FA[Fundamental Analyst]
    MS --> NA[News Analyst]
    TA --> QA[Quant Analyst]
    FA --> QA
    NA --> QA
    QA --> RM[Risk Manager]
    RM -->|approved| PM[Portfolio Manager]
    RM -->|rejected| EndNode([END])
    PM --> EndNode
```

| # | Agent | Role |
|---|-------|------|
| 1 | **Market Scout** | Finds & ranks opportunities |
| 2 | **Technical Analyst** | RSI, MACD, MAs, trend, bias |
| 3 | **Fundamental Analyst** | Financials & valuation |
| 4 | **News Analyst** | Headlines, catalysts, sentiment |
| 5 | **Quant Analyst** | Edge score, win probability, scenarios, factors |
| 6 | **Risk Manager** | Stress tests, downside, sizing — **can REJECT** |
| 7 | **Portfolio Manager** | Final investment memo + allocation |

## Stack

- Python 3.11+
- LangGraph + LangChain (+ `langchain-anthropic` for live mode)
- `yfinance` for market data
- Optional Alpaca (not required)
- **`--demo` mode** works with **no API keys** (canned data + rule-based agents, zero LLM calls)

## Setup

```bash
cd ai-hedge-fund
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .

# Optional for live LLM analysis
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=...
```

## Usage

```bash
# Full 7-agent analysis (demo — no API key)
python -m hedge_fund.cli analyze TSLA --demo

# Universe scan then deep-dive top name
python -m hedge_fund.cli scan --demo

# Live mode (requires ANTHROPIC_API_KEY; still uses yfinance for market data)
python -m hedge_fund.cli analyze AAPL
```

Or via the console script after install:

```bash
hedge-fund analyze TSLA --demo
```

## Project layout

```
ai-hedge-fund/
  README.md
  requirements.txt
  pyproject.toml
  .env.example
  .gitignore
  src/hedge_fund/
    __init__.py
    state.py          # TypedDict AgentState
    graph.py          # LangGraph wiring + conditional risk routing
    config.py
    cli.py
    demo_data.py
    llm.py            # optional Anthropic enrichment (skipped in --demo)
    agents/           # 7 agents
    tools/            # market_data, indicators, news
    web/
      app.py          # FastAPI + /api/analyze + /api/scan
      static/         # polished single-page dashboard
  examples/sample_output.md
  tests/test_graph_smoke.py
```

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```


## Web dashboard

A local product-style UI (cream background, orange accents, 7 agent “floors”, final memo panel) wired to the same LangGraph pipeline.

```bash
# install / refresh deps (includes fastapi + uvicorn)
pip install -e .

# start the dashboard
uvicorn hedge_fund.web.app:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000). Use the **Demo** toggle (or `?demo=1`) to run without `ANTHROPIC_API_KEY`.

API:

- `POST /api/analyze` — body `{ "ticker": "TSLA", "demo": true }`
- `POST /api/scan` — body `{ "demo": true }`
- `GET /` — dashboard UI

```bash
curl -s -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"TSLA","demo":true}' | python -m json.tool | head
```

> Screenshot note: open the dashboard after a demo analyze — agent cards 01–07 update on the left, investment memo on the right.

## License

MIT — use at your own risk. Not investment advice.
