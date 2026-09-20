# Setup Guide — Dinesh AI Fund

**Complete installation and configuration guide for the Dinesh AI Fund 7-agent investment research system.**

Founded by **Dineshgopi Sunkara** — Senior Controls Engineer · Automation Engineer

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Demo Mode (No API Keys Required)](#demo-mode-no-api-keys-required)
- [Live Mode with LLM Enrichment](#live-mode-with-llm-enrichment)
- [Running the Web Dashboard](#running-the-web-dashboard)
- [Command-Line Usage](#command-line-usage)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

- **Python**: 3.11 or higher
- **Operating System**: Linux, macOS, or Windows (with WSL recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Internet**: Required for market data (yfinance) and optional LLM API calls

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sunkara1111/ai-hedge-fund.git
cd ai-hedge-fund
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -e .
```

For development (includes testing tools):

```bash
pip install -e ".[dev]"
```

---

## Configuration

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your preferred text editor:

```bash
# Optional: Anthropic API key for live LLM enrichment
ANTHROPIC_API_KEY=your_key_here

# Optional: Alpaca credentials (not required for basic usage)
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
```

**Note:** The `.env` file is git-ignored for security. Never commit API keys to version control.

---

## Demo Mode (No API Keys Required)

Demo mode uses bundled sample data and rule-based agents. Perfect for:

- Testing the system without API costs
- Educational demonstrations
- Understanding the 7-agent workflow

### CLI Demo

```bash
# Analyze a single ticker in demo mode
python -m hedge_fund.cli analyze TSLA --demo

# Scan universe and deep-dive top opportunity
python -m hedge_fund.cli scan --demo
```

### Web Dashboard Demo

```bash
# Start the dashboard
uvicorn hedge_fund.web.app:app --reload --port 8000
```

Open your browser to [http://localhost:8000?demo=1](http://localhost:8000?demo=1)

Or toggle the "Demo" switch in the UI.

---

## Live Mode with LLM Enrichment

Live mode requires an Anthropic API key and provides:

- Real-time LLM analysis from Claude
- Enhanced agent reasoning
- Custom analysis based on live market data

### Setup

1. Get an API key from [Anthropic Console](https://console.anthropic.com/)
2. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### CLI Live Mode

```bash
# Analyze with LLM enrichment (no --demo flag)
python -m hedge_fund.cli analyze AAPL

# Scan universe with LLM agents
python -m hedge_fund.cli scan
```

### Web Dashboard Live Mode

```bash
uvicorn hedge_fund.web.app:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) (without `?demo=1`) and ensure Demo toggle is OFF.

---

## Running the Web Dashboard

The web dashboard provides a visual interface for the 7-agent research floor.

### Start the Server

```bash
uvicorn hedge_fund.web.app:app --reload --port 8000
```

Options:

- `--reload`: Auto-restart on code changes (development)
- `--port 8000`: Specify port (default: 8000)
- `--host 0.0.0.0`: Allow external connections

### API Endpoints

- `GET /` — Dashboard UI
- `GET /api/health` — System health check
- `POST /api/analyze` — Analyze a ticker
  ```json
  {
    "ticker": "TSLA",
    "demo": true
  }
  ```
- `POST /api/scan` — Universe scan
  ```json
  {
    "demo": true
  }
  ```

### Example API Call

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"NVDA","demo":true}' \
  | python -m json.tool
```

---

## Command-Line Usage

After installation, you can use either:

- `python -m hedge_fund.cli` (always works)
- `hedge-fund` (console script, may require PATH setup)

### Analyze a Ticker

```bash
# Demo mode (no API key)
hedge-fund analyze TSLA --demo

# Live mode (requires ANTHROPIC_API_KEY)
hedge-fund analyze AAPL
```

### Scan Universe

```bash
# Demo mode
hedge-fund scan --demo

# Live mode
hedge-fund scan
```

### Output

Results are printed to stdout in JSON format. You can redirect to a file:

```bash
hedge-fund analyze TSLA --demo > tsla_analysis.json
```

---

## Testing

Run the test suite:

```bash
# Install dev dependencies first
pip install -e ".[dev]"

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_graph.py

# Run with coverage report
pytest --cov=hedge_fund --cov-report=html
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'hedge_fund'`

**Solution:**
```bash
pip install -e .
```

#### 2. Missing Dependencies

**Problem:** `ImportError: cannot import name 'ChatAnthropic'`

**Solution:**
```bash
pip install --upgrade langchain-anthropic
```

#### 3. API Key Not Found

**Problem:** `ValueError: ANTHROPIC_API_KEY not found`

**Solution:**
- Use `--demo` flag for demo mode, OR
- Add `ANTHROPIC_API_KEY` to `.env` file

#### 4. Port Already in Use

**Problem:** `Error: address already in use`

**Solution:**
```bash
# Use a different port
uvicorn hedge_fund.web.app:app --port 8001

# Or kill the process using port 8000
# Linux/macOS:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 5. Market Data Fetch Errors

**Problem:** `yfinance.exceptions.YFinanceException`

**Solution:**
- Check internet connection
- Try a different ticker symbol
- Use `--demo` mode if live data is unavailable

### Getting Help

- Check the [main README](/README.md)
- Review code comments in `src/hedge_fund/`
- Open an issue on [GitHub](https://github.com/sunkara1111/ai-hedge-fund/issues)
- Contact founder: [github.com/sunkara1111](https://github.com/sunkara1111)

---

## Project Structure

```
ai-hedge-fund/
├── docs/                    # GitHub Pages static site
│   ├── index.html          # Public showcase
│   └── SETUP.md            # This guide
├── src/hedge_fund/         # Main package
│   ├── agents/             # 7 agent implementations
│   ├── tools/              # Market data, indicators, news
│   ├── web/                # FastAPI dashboard
│   ├── graph.py            # LangGraph orchestration
│   ├── state.py            # Agent state management
│   ├── cli.py              # Command-line interface
│   └── demo_data.py        # Demo mode data
├── tests/                  # Test suite
├── examples/               # Sample outputs
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Package metadata
├── LICENSE                 # MIT license
├── COPYRIGHT.md            # Copyright notice
├── PATENT_NOTICE.md        # IP rights notice
└── README.md               # Main documentation
```

---

## Next Steps

1. **Run a demo analysis**: `hedge-fund analyze TSLA --demo`
2. **Start the dashboard**: `uvicorn hedge_fund.web.app:app --reload --port 8000`
3. **Explore the code**: Start with `src/hedge_fund/graph.py`
4. **Add your API key**: For live LLM enrichment
5. **Customize agents**: Modify agent logic in `src/hedge_fund/agents/`

---

## Disclaimer

**Paper / research only.** This software is for educational purposes. It does not handle real money, execute live trades, or provide financial advice. Use at your own risk. See [LICENSE](../LICENSE) for warranty disclaimers.

---

## About the Founder

**Dinesh AI Fund** was created by **Dineshgopi Sunkara** — Senior Controls Engineer · Automation Engineer

- GitHub: [github.com/sunkara1111](https://github.com/sunkara1111)
- Project: [github.com/sunkara1111/ai-hedge-fund](https://github.com/sunkara1111/ai-hedge-fund)
- Live showcase: [sunkara1111.github.io/ai-hedge-fund](https://sunkara1111.github.io/ai-hedge-fund/)

© 2026 Dineshgopi Sunkara. All rights reserved.
