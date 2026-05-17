# StockLens — AI-Powered Stock Analysis

A full-stack web application for deep stock research. Enter any ticker symbol to get:

- **Live market data** — price, volume, 52-week range, beta, market cap
- **SEC EDGAR filings** — 10-K annual reports, 10-Q quarterly, 8-K material events
- **News aggregation** — Yahoo Finance, Google News, MarketWatch, CNBC RSS feeds
- **DCF valuation model** — two-stage discounted cash flow with sensitivity matrix
- **Fundamental ratios** — P/E, PEG, P/B, EV/EBITDA, margins, ROE, Graham Number
- **AI investment thesis** — Claude generates an institutional-quality research report

## Quick Start

```bash
cd stock-analysis
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
python app.py
```

Open http://localhost:5000

## Demo Mode (no API keys needed)

Run with realistic MSFT sample data:

```bash
DEMO_MODE=true python app.py
```

## Configuration

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Required for AI analysis tab (get at console.anthropic.com) |
| `NEWS_API_KEY` | Optional — adds newsapi.org articles (newsapi.org) |
| `DEMO_MODE` | Set to `true` to use pre-loaded MSFT demo data |
| `PORT` | Server port (default 5000) |
| `FLASK_DEBUG` | Set to `true` for auto-reload during development |

## Architecture

```
app.py                          Flask routes and orchestration
src/
  data_collectors/
    stock_data.py               yfinance — prices, financials, ratios
    sec_filings.py              SEC EDGAR API — 10-K/10-Q/8-K
    news.py                     RSS feed aggregation (no API key needed)
  analyzers/
    valuation.py                DCF model, sensitivity, scoring rubric
    claude_analyst.py           Anthropic Claude API — investment thesis
  demo_data.py                  Sample MSFT data for offline/demo use
static/
  css/style.css                 Dark-mode UI
  js/analysis.js                Plotly charts, tab navigation, rendering
templates/
  base.html                     Nav, footer
  index.html                    Landing page with search
  loading.html                  Progress screen while fetching data
  analysis.html                 6-tab analysis dashboard
```

## What the AI Analyzes

The AI tab sends all collected data to Claude and receives a structured report covering:

1. **Executive Summary** — recommendation, 12-month price target
2. **Business Quality** — moat, revenue quality, management effectiveness
3. **Financial Analysis** — growth trajectory, margin profile, cash flow
4. **Valuation Analysis** — multiples vs. peers, DCF interpretation, bull/base/bear targets
5. **Catalysts & Risks** — near-term re-rating events, downside scenarios, macro sensitivity
6. **News Sentiment** — synthesized view of recent headlines
7. **Investment Conclusion** — final rating, conviction level, position sizing

## Data Sources

| Source | Data | Cost |
|---|---|---|
| Yahoo Finance (yfinance) | Prices, financials, analyst ratings | Free |
| SEC EDGAR | 10-K/10-Q/8-K filings, XBRL facts | Free |
| RSS Feeds | News headlines and summaries | Free |
| Anthropic Claude | AI investment analysis | Pay per token |
| NewsAPI (optional) | Additional news sources | Free tier available |

## Disclaimer

For educational and research purposes only. Not financial advice. Always do your own due diligence before making investment decisions.
