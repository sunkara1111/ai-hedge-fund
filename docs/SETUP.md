# Dinesh AI Fund — Setup & Run Guide

**Founded by Dineshgopi Sunkara**

This guide covers local installation, configuration, and running the 7-agent investment research system.

---

## Prerequisites

- **Python 3.11 or higher** (required)
- Git (for cloning the repository)
- Optional: [Anthropic API key](https://console.anthropic.com/) for live LLM enrichment (not required for demo mode)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sunkara1111/ai-hedge-fund.git
cd ai-hedge-fund
```

### 2. Create and activate a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install the package

```bash
pip install -e .
```

This installs the `hedge-fund` CLI command and all required dependencies:
- LangGraph + LangChain
- `yfinance` for market data
- FastAPI + Uvicorn for the web dashboard
- Rich for console output

---

## Configuration (Optional)

### Environment variables

For **live mode** (LLM-enriched analysis), you need an Anthropic API key:

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and add your key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

**Demo mode** requires no API keys and works out of the box.

---

## Usage

### Command-line interface (CLI)

#### Single-ticker analysis

Run a full 7-agent analysis for a single stock:

```bash
# Demo mode (no API key required)
hedge-fund analyze TSLA --demo

# Live mode (requires ANTHROPIC_API_KEY in .env)
hedge-fund analyze AAPL
```

Or using the module syntax:

```bash
python -m hedge_fund.cli analyze TSLA --demo
```

#### Universe scan

Scan multiple tickers and deep-dive on the top candidate:

```bash
# Demo mode
hedge-fund scan --demo

# Live mode
hedge-fund scan
```

### Web dashboard

The local web dashboard provides a product-style UI (cream background, orange accents, 7 agent floors + final memo panel).

#### 1. Start the server

```bash
uvicorn hedge_fund.web.app:app --reload --port 8000
```

#### 2. Open in browser

Navigate to: [http://localhost:8000](http://localhost:8000)

- Toggle **Demo** mode (or append `?demo=1` to the URL) to run without an API key
- Enter a ticker (e.g., `TSLA`) and click **Analyze**
- Click **Scan** to run a universe scan

#### 3. API endpoints

The dashboard exposes a REST API:

- `GET /` — Dashboard UI
- `GET /api/health` — Product name, founder, agent count
- `POST /api/analyze` — Body: `{ "ticker": "TSLA", "demo": true }`
- `POST /api/scan` — Body: `{ "demo": true }`

**Example API call:**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"TSLA","demo":true}' | python -m json.tool
```

---

## Testing

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

---

## Project Structure

```
ai-hedge-fund/
├── LICENSE                  # MIT license
├── COPYRIGHT                # Copyright notice
├── PATENT_NOTICE            # Patent disclaimer
├── README.md                # Project overview
├── docs/
│   ├── SETUP.md             # This file
│   └── index.html           # GitHub Pages static site
├── src/hedge_fund/
│   ├── agents/              # 7 research agents
│   ├── tools/               # Market data, indicators, news
│   ├── cli.py               # Command-line interface
│   ├── graph.py             # LangGraph wiring
│   ├── web/
│   │   ├── app.py           # FastAPI backend
│   │   └── static/          # Dashboard HTML/CSS/JS
│   └── ...
├── tests/                   # Test suite
├── requirements.txt         # Pinned dependencies
└── pyproject.toml           # Package metadata
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'hedge_fund'`

Ensure you installed the package in editable mode:

```bash
pip install -e .
```

### Dashboard shows "Connection refused"

Make sure the FastAPI server is running:

```bash
uvicorn hedge_fund.web.app:app --reload --port 8000
```

### Live mode fails with API errors

1. Verify your `.env` file contains a valid `ANTHROPIC_API_KEY`
2. Check your API quota at [console.anthropic.com](https://console.anthropic.com/)
3. Fallback to demo mode: `hedge-fund analyze TSLA --demo`

---

## Additional Resources

- **GitHub Repository**: [https://github.com/sunkara1111/ai-hedge-fund](https://github.com/sunkara1111/ai-hedge-fund)
- **Public Showcase**: [https://sunkara1111.github.io/ai-hedge-fund/](https://sunkara1111.github.io/ai-hedge-fund/)
- **Issues & Support**: [GitHub Issues](https://github.com/sunkara1111/ai-hedge-fund/issues)

---

## Disclaimer

**Paper / research only.** This project is for education and experimentation. It is **not financial advice**. It does **not** handle real money, execute live trades, or manage client capital. Do not use it to make real trading decisions without independent due diligence. Simulated scores and demo data do not predict future results.

---

**Founded by Dineshgopi Sunkara**  
Senior Controls Engineer · Automation Engineer
