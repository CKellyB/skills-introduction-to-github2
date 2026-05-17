"""
Deep AI-powered stock analysis using the Anthropic Claude API.
Synthesizes all collected data into an investment thesis with valuation analysis.
"""
import os
import json
import anthropic
from typing import Optional


def _format_number(val, suffix="", scale=1e9, decimals=1) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 1e12:
            return f"${v / 1e12:.{decimals}f}T{suffix}"
        elif abs(v) >= 1e9:
            return f"${v / 1e9:.{decimals}f}B{suffix}"
        elif abs(v) >= 1e6:
            return f"${v / 1e6:.{decimals}f}M{suffix}"
        return f"${v:,.0f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def _pct(val) -> str:
    if val is None:
        return "N/A"
    try:
        return f"{float(val) * 100:.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def build_analysis_prompt(
    symbol: str,
    overview: dict,
    valuation: dict,
    financials: dict,
    dcf_result: dict,
    analyst_ratings: dict,
    news_articles: list[dict],
    sec_filings: list[dict],
    scores: dict,
    company_facts: dict,
) -> str:
    name = overview.get("name", symbol)
    price = overview.get("price")
    mktcap = _format_number(overview.get("market_cap"))
    ev = _format_number(overview.get("enterprise_value"))

    # Top 10 recent news headlines
    headlines = "\n".join(
        f"  - [{a['source']}] {a['title']} ({a['published'][:10]})"
        for a in news_articles[:10]
    ) or "  No recent news available."

    # Recent SEC filings
    filings_text = "\n".join(
        f"  - {f['form_type']} filed {f['filing_date']}"
        for f in sec_filings[:6]
    ) or "  No SEC filings data available."

    # DCF summary
    dcf_summary = "N/A"
    if isinstance(dcf_result, dict) and not dcf_result.get("error"):
        iv = dcf_result.get("intrinsic_value_per_share")
        if iv and price:
            margin = (price / iv - 1) * 100
            dcf_summary = (
                f"Intrinsic value per share: ${iv:.2f} | "
                f"Current price: ${price:.2f} | "
                f"Margin of safety: {'%.1f%% overvalued' % margin if margin > 0 else '%.1f%% undervalued' % abs(margin)}"
            )
            dcf_summary += f"\n  Growth assumptions: Phase 1 {dcf_result['assumptions']['phase1_growth']:.1%}, Phase 2 {dcf_result['assumptions']['phase2_growth']:.1%}, Terminal {dcf_result['assumptions']['terminal_growth_rate']:.1%}"

    prompt = f"""You are a senior investment analyst and CFA charterholder. Perform a comprehensive, institutional-quality stock analysis for {name} ({symbol}).

Today's date: 2026-05-17

## COMPANY OVERVIEW
- Name: {name}
- Sector: {overview.get('sector', 'N/A')} | Industry: {overview.get('industry', 'N/A')}
- Exchange: {overview.get('exchange', 'N/A')} | Country: {overview.get('country', 'N/A')}
- Current Price: ${price:.2f if price else 'N/A'}
- Market Cap: {mktcap} | Enterprise Value: {ev}
- Beta: {overview.get('beta', 'N/A')}
- 52-Week Range: ${overview.get('52w_low', 'N/A')} - ${overview.get('52w_high', 'N/A')}
- Description: {overview.get('description', 'N/A')[:600]}

## VALUATION MULTIPLES
- P/E (Trailing): {valuation.get('pe_trailing', 'N/A')}x
- P/E (Forward): {valuation.get('pe_forward', 'N/A')}x
- PEG Ratio: {valuation.get('peg_ratio', 'N/A')}
- Price/Book: {valuation.get('price_to_book', 'N/A')}x
- Price/Sales: {valuation.get('price_to_sales', 'N/A')}x
- EV/Revenue: {valuation.get('ev_to_revenue', 'N/A')}x
- EV/EBITDA: {valuation.get('ev_to_ebitda', 'N/A')}x

## FINANCIAL PERFORMANCE
- Revenue (TTM): {_format_number(financials.get('revenue_ttm'))}
- Revenue Growth YoY: {_pct(financials.get('revenue_growth_yoy'))}
- Gross Margin: {_pct(financials.get('gross_margin'))}
- Operating Margin: {_pct(financials.get('operating_margin'))}
- Net Margin: {_pct(financials.get('profit_margin'))}
- EBITDA: {_format_number(financials.get('ebitda'))}
- Net Income: {_format_number(financials.get('net_income'))}
- EPS (Trailing): ${financials.get('eps_trailing', 'N/A')}
- EPS (Forward): ${financials.get('eps_forward', 'N/A')}
- Earnings Growth YoY: {_pct(financials.get('earnings_growth_yoy'))}
- FCF: {_format_number(financials.get('free_cash_flow'))}
- Operating Cash Flow: {_format_number(financials.get('operating_cash_flow'))}
- Total Cash: {_format_number(financials.get('total_cash'))}
- Total Debt: {_format_number(financials.get('total_debt'))}
- Net Cash Position: {_format_number(financials.get('net_cash'))}
- Current Ratio: {financials.get('current_ratio', 'N/A')}
- Debt/Equity: {financials.get('debt_to_equity', 'N/A')}
- ROE: {_pct(financials.get('return_on_equity'))}
- ROA: {_pct(financials.get('return_on_assets'))}
- Dividend Yield: {_pct(financials.get('dividend_yield'))}

## DCF VALUATION MODEL
{dcf_summary}

## QUANTITATIVE SCORE (0-100)
- Growth Score: {scores.get('growth', 'N/A')}/20
- Profitability Score: {scores.get('profitability', 'N/A')}/20
- Value Score: {scores.get('value', 'N/A')}/20
- Financial Health Score: {scores.get('financial_health', 'N/A')}/20
- Momentum Score: {scores.get('momentum', 'N/A')}/20
- TOTAL: {scores.get('total', 'N/A')}/100 → {scores.get('rating', 'N/A')}

## WALL STREET CONSENSUS
- Consensus: {analyst_ratings.get('recommendation', 'N/A').upper()}
- # Analysts: {analyst_ratings.get('num_analysts', 'N/A')}
- Price Target: Low ${analyst_ratings.get('target_low', 'N/A')} | Mean ${analyst_ratings.get('target_mean', 'N/A')} | High ${analyst_ratings.get('target_high', 'N/A')}

## RECENT NEWS (last 10 articles)
{headlines}

## SEC FILINGS (recent)
{filings_text}

---

Please provide a detailed investment analysis in the following structured format:

### 1. EXECUTIVE SUMMARY (3-4 sentences)
Concise investment thesis including your recommendation (Strong Buy / Buy / Hold / Underperform / Sell) and 12-month price target range.

### 2. BUSINESS QUALITY ASSESSMENT
- Competitive moat and positioning
- Revenue quality and diversification
- Management effectiveness (based on ROE, margin trends, capital allocation)
- Key risks to the business model

### 3. FINANCIAL ANALYSIS
- Revenue and earnings growth trajectory
- Margin profile vs. industry norms
- Balance sheet strength and capital structure
- Free cash flow generation and quality

### 4. VALUATION ANALYSIS
- Assessment of current multiples vs. historical and peers
- DCF model interpretation — is the stock priced for perfection or is there a margin of safety?
- Bull, base, and bear case 12-month price targets with rationale

### 5. CATALYSTS & RISKS
- Near-term (0-6 month) catalysts that could drive re-rating
- Key downside risks and probability assessment
- Macro sensitivity (rates, FX, cycle)

### 6. NEWS SENTIMENT ANALYSIS
- Synthesize the recent news headlines into a sentiment picture (Positive / Neutral / Negative)
- Identify any news that could materially impact the valuation
- Note any regulatory, competitive, or macro themes

### 7. INVESTMENT CONCLUSION
- Final recommendation with conviction level (High / Medium / Low)
- 12-month price target (base case)
- Position sizing suggestion (Core / Overweight / Underweight / Avoid)
- Key metrics to watch

Be specific, quantitative where possible, and intellectually honest about uncertainty. Distinguish between facts from the data and your analytical judgments."""

    return prompt


def run_ai_analysis(
    symbol: str,
    overview: dict,
    valuation: dict,
    financials: dict,
    dcf_result: dict,
    analyst_ratings: dict,
    news_articles: list[dict],
    sec_filings: list[dict],
    scores: dict,
    company_facts: dict,
) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {
            "error": "ANTHROPIC_API_KEY not set. Add it to your .env file to enable AI analysis.",
            "analysis": None,
        }

    prompt = build_analysis_prompt(
        symbol=symbol,
        overview=overview,
        valuation=valuation,
        financials=financials,
        dcf_result=dcf_result,
        analyst_ratings=analyst_ratings,
        news_articles=news_articles,
        sec_filings=sec_filings,
        scores=scores,
        company_facts=company_facts,
    )

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=(
                "You are a senior investment analyst with 20+ years of experience at a top-tier asset manager. "
                "Your analyses are rigorous, balanced, and grounded in data. You cite specific numbers, "
                "acknowledge uncertainty, and distinguish between investment thesis and market sentiment. "
                "Format your response in clean Markdown."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
        analysis_text = response.content[0].text
        return {
            "error": None,
            "analysis": analysis_text,
            "model": response.model,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    except anthropic.AuthenticationError:
        return {"error": "Invalid Anthropic API key. Check your .env file.", "analysis": None}
    except anthropic.RateLimitError:
        return {"error": "Anthropic rate limit reached. Please try again in a moment.", "analysis": None}
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}", "analysis": None}
