"""
Realistic sample data for MSFT — used when DEMO_MODE=true or network is unavailable.
All figures are approximate real values for Microsoft as of early 2025.
"""
import math
import random


def _generate_demo_prices() -> list[dict]:
    random.seed(42)
    prices = []
    trading_days = 252

    for i in range(trading_days):
        trend = (415.32 - 344.79) / trading_days
        seasonal = 10 * math.sin(2 * math.pi * i / 252)
        noise = random.gauss(0, 3.5)
        close = 344.79 + trend * i + seasonal + noise
        close = max(close, 344.0)

        high = close + random.uniform(1, 6)
        low = close - random.uniform(1, 6)
        open_price = close + random.gauss(0, 2)

        year = 2024 + (i + 130) // 252
        day_of_year = (i + 130) % 252
        month = min(day_of_year // 21 + 1, 12)
        day = min(day_of_year % 21 + 1, 28)
        date_str = f"{year}-{month:02d}-{day:02d}"

        prices.append({
            "date": date_str,
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": random.randint(15000000, 28000000),
        })

    prices.sort(key=lambda x: x["date"])
    return prices


MSFT_DEMO: dict = {
    "symbol": "MSFT",
    "overview": {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "sector": "Technology",
        "industry": "Software—Infrastructure",
        "exchange": "NMS",
        "currency": "USD",
        "price": 415.32,
        "prev_close": 411.50,
        "change_pct": 0.93,
        "market_cap": 3087000000000,
        "enterprise_value": 3124000000000,
        "shares_outstanding": 7435000000,
        "float_shares": 7421000000,
        "beta": 0.89,
        "52w_high": 468.35,
        "52w_low": 344.79,
        "avg_volume": 20340000,
        "volume": 18900000,
        "description": (
            "Microsoft Corporation develops and supports software, services, devices, and solutions worldwide. "
            "The company operates in three segments: Productivity and Business Processes, Intelligent Cloud, "
            "and More Personal Computing. The Intelligent Cloud segment includes Azure, server products, and "
            "enterprise services. Copilot, Microsoft's AI assistant, is embedded across its entire product portfolio, "
            "driving significant commercial adoption. The company is headquartered in Redmond, Washington."
        ),
        "website": "https://www.microsoft.com",
        "employees": 221000,
        "country": "United States",
        "city": "Redmond",
    },
    "valuation": {
        "pe_trailing": 34.8,
        "pe_forward": 29.2,
        "peg_ratio": 2.1,
        "price_to_book": 12.4,
        "price_to_sales": 12.9,
        "ev_to_revenue": 13.1,
        "ev_to_ebitda": 24.6,
        "earnings_yield": 2.87,
        "book_value_per_share": 33.45,
        "revenue_per_share": 32.15,
    },
    "financials": {
        "revenue_ttm": 245122000000,
        "gross_profit": 170000000000,
        "ebitda": 127000000000,
        "net_income": 88136000000,
        "eps_trailing": 11.45,
        "eps_forward": 13.10,
        "revenue_growth_yoy": 0.161,
        "earnings_growth_yoy": 0.218,
        "gross_margin": 0.694,
        "operating_margin": 0.448,
        "profit_margin": 0.360,
        "ebitda_margin": 0.518,
        "total_cash": 75500000000,
        "total_debt": 44000000000,
        "net_cash": 31500000000,
        "free_cash_flow": 74000000000,
        "operating_cash_flow": 87000000000,
        "current_ratio": 1.32,
        "quick_ratio": 1.27,
        "debt_to_equity": 41.2,
        "return_on_equity": 0.342,
        "return_on_assets": 0.148,
        "dividend_yield": 0.0072,
        "dividend_rate": 3.00,
        "payout_ratio": 0.253,
    },
    "prices": _generate_demo_prices(),
    "analyst_ratings": {
        "recommendation": "buy",
        "num_analysts": 52,
        "target_mean": 497.50,
        "target_high": 600.00,
        "target_low": 420.00,
        "target_median": 500.00,
        "recent_upgrades_downgrades": [
            {"firm": "Goldman Sachs", "to_grade": "Buy", "from_grade": "Neutral", "action": "up"},
            {"firm": "Morgan Stanley", "to_grade": "Overweight", "from_grade": "Overweight", "action": "reit"},
            {"firm": "Wedbush", "to_grade": "Outperform", "from_grade": "Outperform", "action": "reit"},
            {"firm": "JPMorgan", "to_grade": "Overweight", "from_grade": "Neutral", "action": "up"},
        ],
    },
    "earnings_history": [
        {"quarter": "2025-01-29", "eps_estimate": 3.11, "eps_actual": 3.23, "surprise_pct": 3.86},
        {"quarter": "2024-10-30", "eps_estimate": 3.10, "eps_actual": 3.30, "surprise_pct": 6.45},
        {"quarter": "2024-07-30", "eps_estimate": 2.93, "eps_actual": 2.95, "surprise_pct": 0.68},
        {"quarter": "2024-04-25", "eps_estimate": 2.82, "eps_actual": 2.94, "surprise_pct": 4.26},
        {"quarter": "2024-01-30", "eps_estimate": 2.78, "eps_actual": 2.93, "surprise_pct": 5.40},
        {"quarter": "2023-10-24", "eps_estimate": 2.65, "eps_actual": 2.99, "surprise_pct": 12.83},
        {"quarter": "2023-07-25", "eps_estimate": 2.55, "eps_actual": 2.69, "surprise_pct": 5.49},
        {"quarter": "2023-04-25", "eps_estimate": 2.23, "eps_actual": 2.45, "surprise_pct": 9.87},
    ],
    "sec_filings": [
        {"form_type": "10-K", "filing_date": "2024-07-30", "accession_number": "0001564590-24-012345",
         "document_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=10-K",
         "index_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=10-K", "cik": 789019},
        {"form_type": "10-Q", "filing_date": "2025-01-29", "accession_number": "0001564590-25-001234",
         "document_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=10-Q",
         "index_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=10-Q", "cik": 789019},
        {"form_type": "10-Q", "filing_date": "2024-10-30", "accession_number": "0001564590-24-009876",
         "document_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=10-Q",
         "index_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=10-Q", "cik": 789019},
        {"form_type": "8-K", "filing_date": "2025-01-29", "accession_number": "0001564590-25-000789",
         "document_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=8-K",
         "index_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=8-K", "cik": 789019},
        {"form_type": "8-K", "filing_date": "2024-10-30", "accession_number": "0001564590-24-008765",
         "document_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=8-K",
         "index_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=789019&type=8-K", "cik": 789019},
    ],
    "news": [
        {"title": "Microsoft Azure Revenue Grows 31% in Q2 FY2025, Boosted by AI Demand",
         "summary": "Microsoft reported strong cloud growth driven by Azure AI services and Copilot adoption across enterprise customers. The company raised full-year guidance.", "url": "#", "published": "2025-01-29 16:30", "source": "Yahoo Finance"},
        {"title": "OpenAI Partnership Extends Through 2030 in $10B Deal",
         "summary": "Microsoft extended its exclusive cloud partnership with OpenAI, securing a significant expansion of AI compute infrastructure.", "url": "#", "published": "2025-01-15 09:00", "source": "Reuters"},
        {"title": "Microsoft Copilot for M365 Reaches 1M Paid Enterprise Seats",
         "summary": "The AI productivity tool has seen rapid adoption across Fortune 500 companies, adding meaningfully to Microsoft's commercial cloud revenue.", "url": "#", "published": "2025-01-10 14:00", "source": "CNBC"},
        {"title": "Antitrust Regulators Scrutinize Microsoft's AI Market Position",
         "summary": "European and US regulators are examining Microsoft's dominance in enterprise AI, potentially requiring behavioral remedies.", "url": "#", "published": "2025-01-05 11:00", "source": "MarketWatch"},
        {"title": "Microsoft's Datacenter Capex to Hit $80B in FY2025",
         "summary": "The company confirmed it plans to invest heavily in AI infrastructure, raising concerns about near-term free cash flow compression.", "url": "#", "published": "2024-12-20 10:00", "source": "Bloomberg"},
        {"title": "MSFT Stock: Goldman Sachs Raises Price Target to $550",
         "summary": "Goldman Sachs analyst raised its price target citing accelerating Azure growth and the monetization of Copilot AI across enterprise products.", "url": "#", "published": "2024-12-15 08:30", "source": "Seeking Alpha"},
        {"title": "Microsoft Completes Activision Blizzard Integration, Gaming Revenue Up 61%",
         "summary": "The $69 billion acquisition is proving accretive, with Game Pass subscribers and Xbox content revenue beating expectations.", "url": "#", "published": "2024-12-10 14:00", "source": "Yahoo Finance"},
    ],
    "revenue_trend": [
        {"year": "2020", "value": 143015000000},
        {"year": "2021", "value": 168088000000},
        {"year": "2022", "value": 198270000000},
        {"year": "2023", "value": 211915000000},
        {"year": "2024", "value": 245122000000},
    ],
    "ni_trend": [
        {"year": "2020", "value": 44281000000},
        {"year": "2021", "value": 61271000000},
        {"year": "2022", "value": 72738000000},
        {"year": "2023", "value": 72361000000},
        {"year": "2024", "value": 88136000000},
    ],
    "dcf_result": {
        "base_fcf": 74000000000,
        "projected_cash_flows": [
            85840000000, 99574400000, 115506304000, 126957734000, 139653507000,
            149229452000, 159575413000, 170745292000, 182697162000, 195485963000,
        ],
        "pv_cash_flows": [
            78036363636, 82293388430, 86776720778, 86723268218, 86721040289,
            84225682800, 81889773854, 79704453745, 77661168090, 75750899654,
        ],
        "terminal_value": 2932289445000,
        "pv_terminal_value": 1131024000000,
        "total_pv_operations": 1950806760000,
        "intrinsic_value_per_share": 262.40,
        "assumptions": {
            "discount_rate": 0.10,
            "terminal_growth_rate": 0.03,
            "phase1_growth": 0.161,
            "phase2_growth": 0.092,
            "projection_years": 10,
        },
    },
    "sensitivity": {
        "growth_rates": ["11%", "16%", "21%"],
        "discount_rates": ["8%", "10%", "12%"],
        "matrix": {
            "11%": {"8%": 312.50, "10%": 241.20, "12%": 192.80},
            "16%": {"8%": 398.60, "10%": 304.40, "12%": 239.70},
            "21%": {"8%": 512.30, "10%": 386.90, "12%": 300.50},
        },
    },
    "graham_number": 65.42,
    "fair_value_band": {"bear": 196.50, "base": 262.00, "bull": 327.50},
    "scores": {
        "growth": 16.0,
        "profitability": 18.5,
        "value": 8.0,
        "financial_health": 16.0,
        "momentum": 13.5,
        "total": 72.0,
        "rating": "Strong Buy",
    },
    "ai_analysis": {
        "error": None,
        "analysis": """### 1. EXECUTIVE SUMMARY

Microsoft Corporation (MSFT) is a **Buy** with a 12-month base-case price target of **$490–$520**, representing ~18–25% upside from the current price of $415. The investment thesis rests on three pillars: (1) Azure's durable 30%+ growth trajectory driven by AI workloads, (2) rapidly monetizing Copilot AI embedded across a $200B+ commercial TAM, and (3) a balance sheet generating $74B+ in annual free cash flow. The primary risk is valuation — at 34x trailing P/E, MSFT trades at a premium that requires continued execution.

### 2. BUSINESS QUALITY ASSESSMENT

**Competitive Moat:** Microsoft possesses one of the deepest moats in technology, built on three reinforcing advantages: (i) enterprise lock-in through Microsoft 365 with 400M+ commercial seats; (ii) Azure's hyperscaler scale with $38B+ quarterly revenue run-rate; and (iii) the OpenAI partnership, which gives Microsoft first-mover advantage in enterprise AI before competitors can replicate the stack.

**Revenue Quality:** Revenue is exceptionally diversified and sticky. Intelligent Cloud (40% of revenue) grows at 20%+ with 70%+ gross margins. Productivity & Business Processes (30%) is subscription-based with 95%+ renewal rates. Gaming (10%) is growing 61% post-Activision. No single customer exceeds 5% of revenue.

**Management:** CEO Satya Nadella's capital allocation record is exceptional — acquiring LinkedIn ($26B), GitHub ($7.5B), Activision ($69B), and investing early in OpenAI. ROE of 34.2% and operating margins of 44.8% are best-in-class. The $3B/quarter capital return program (buybacks + dividends) is conservatively sized relative to FCF.

### 3. FINANCIAL ANALYSIS

**Revenue:** $245B TTM, growing 16.1% YoY. Azure grew 31% in the most recent quarter and is accelerating — AI services contributed 13 percentage points of growth. The Copilot commercial flywheel is early-innings with 1M+ paid seats out of 400M potential.

**Margins:** Gross margin of 69.4% is sector-leading. Operating margin of 44.8% has expanded 300bps YoY. Near-term risk: $80B datacenter capex could create 2–3% headwind to FCF margins through FY2026, but this investment should drive meaningful returns from FY2027 onward.

**Balance Sheet:** Net cash position of $31.5B provides a fortress balance sheet. FCF of $74B represents a 24% FCF yield on enterprise value. Interest coverage exceeds 40x.

### 4. VALUATION ANALYSIS

**Multiples:** At 34.8x trailing and 29.2x forward P/E, MSFT trades at a 50%+ premium to the S&P 500. PEG of 2.1x is reasonable for a business growing earnings at 22%. EV/EBITDA of 24.6x is a 20% premium to large-cap software peers — justified given Azure's scale and Copilot optionality.

**DCF:** Base-case DCF (16% Phase 1 growth, 10% discount rate, 3% terminal) yields intrinsic value of **$262/share** — suggesting the stock is pricing in Copilot monetization upside. Bull case at 21% growth / 8% discount rate = $512.

**Price Targets (12-month):**
- 🐂 **Bull ($550):** Azure 30%+ growth sustained, Copilot 5M+ seats
- 📊 **Base ($490):** Azure 25% growth, Copilot 3M seats, 32x forward P/E
- 🐻 **Bear ($360):** Azure decelerates to 18%, antitrust restrictions, multiple compression to 25x

### 5. CATALYSTS & RISKS

**Near-term catalysts:** Q3 FY2025 earnings (Azure re-acceleration), Copilot seat announcements, enterprise AI deal flow, GPT-5 release deepening the ecosystem moat.

**Downside risks:** EU/DOJ AI antitrust (~15% probability), Azure growth deceleration below 25%, capex execution risk at $80B/year, macro-driven enterprise IT budget freezes.

### 6. NEWS SENTIMENT ANALYSIS

**Overall: POSITIVE** with isolated regulatory caution.

Azure's 31% growth beat, OpenAI partnership extension, and Copilot milestones are all bullish. The Activision integration (+61% Gaming revenue) de-risks the acquisition thesis. The only structural concern is antitrust scrutiny, which is a 2025 watch item but low probability of material structural remedy.

The $80B capex announcement is double-edged — signals AI demand confidence but raises near-term FCF risk. Net sentiment: constructive for a 12–18 month horizon.

### 7. INVESTMENT CONCLUSION

| Metric | Value |
|--------|-------|
| **Recommendation** | **Buy** |
| **Conviction** | High |
| **12-month Price Target** | **$490** |
| **Position Sizing** | Core / Overweight |

**Key metrics to watch:** Azure quarterly growth rate (maintain >25%), Copilot commercial seats (target >3M), operating margin trajectory, FCF/share growth (target >15% annually), EU regulatory developments.
""",
        "model": "claude-sonnet-4-6 (Demo — set ANTHROPIC_API_KEY for live analysis)",
        "input_tokens": 3842,
        "output_tokens": 1847,
    },
}
