"""Collects stock price, financials, and fundamentals via yfinance."""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_stock_overview(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
    prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
    change = ((price - prev_close) / prev_close * 100) if price and prev_close else 0

    return {
        "symbol": symbol.upper(),
        "name": info.get("longName", symbol),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "exchange": info.get("exchange", "N/A"),
        "currency": info.get("currency", "USD"),
        "price": price,
        "prev_close": prev_close,
        "change_pct": round(change, 2),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "float_shares": info.get("floatShares"),
        "beta": info.get("beta"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "avg_volume": info.get("averageVolume"),
        "volume": info.get("volume"),
        "description": info.get("longBusinessSummary", ""),
        "website": info.get("website", ""),
        "employees": info.get("fullTimeEmployees"),
        "country": info.get("country", ""),
        "city": info.get("city", ""),
    }


def get_valuation_metrics(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    return {
        "pe_trailing": info.get("trailingPE"),
        "pe_forward": info.get("forwardPE"),
        "peg_ratio": info.get("pegRatio"),
        "price_to_book": info.get("priceToBook"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "ev_to_revenue": info.get("enterpriseToRevenue"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "earnings_yield": (1 / info["trailingPE"] * 100) if info.get("trailingPE") else None,
        "book_value_per_share": info.get("bookValue"),
        "revenue_per_share": info.get("revenuePerShare"),
    }


def get_financial_summary(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    return {
        "revenue_ttm": info.get("totalRevenue"),
        "gross_profit": info.get("grossProfits"),
        "ebitda": info.get("ebitda"),
        "net_income": info.get("netIncomeToCommon"),
        "eps_trailing": info.get("trailingEps"),
        "eps_forward": info.get("forwardEps"),
        "revenue_growth_yoy": info.get("revenueGrowth"),
        "earnings_growth_yoy": info.get("earningsGrowth"),
        "gross_margin": info.get("grossMargins"),
        "operating_margin": info.get("operatingMargins"),
        "profit_margin": info.get("profitMargins"),
        "ebitda_margin": (info.get("ebitda") / info.get("totalRevenue")) if info.get("ebitda") and info.get("totalRevenue") else None,
        "total_cash": info.get("totalCash"),
        "total_debt": info.get("totalDebt"),
        "net_cash": (info.get("totalCash", 0) or 0) - (info.get("totalDebt", 0) or 0),
        "free_cash_flow": info.get("freeCashflow"),
        "operating_cash_flow": info.get("operatingCashflow"),
        "current_ratio": info.get("currentRatio"),
        "quick_ratio": info.get("quickRatio"),
        "debt_to_equity": info.get("debtToEquity"),
        "return_on_equity": info.get("returnOnEquity"),
        "return_on_assets": info.get("returnOnAssets"),
        "dividend_yield": info.get("dividendYield"),
        "dividend_rate": info.get("dividendRate"),
        "payout_ratio": info.get("payoutRatio"),
    }


def get_historical_prices(symbol: str, period: str = "1y") -> list[dict]:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    if hist.empty:
        return []

    records = []
    for date, row in hist.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })
    return records


def get_income_statement(symbol: str) -> list[dict]:
    ticker = yf.Ticker(symbol)
    try:
        fin = ticker.financials
        if fin is None or fin.empty:
            return []
        result = []
        for col in fin.columns:
            year_data = {"period": col.strftime("%Y") if hasattr(col, "strftime") else str(col)}
            for idx in fin.index:
                val = fin.loc[idx, col]
                key = idx.lower().replace(" ", "_").replace("/", "_")
                year_data[key] = None if pd.isna(val) else float(val)
            result.append(year_data)
        return result
    except Exception:
        return []


def get_balance_sheet(symbol: str) -> list[dict]:
    ticker = yf.Ticker(symbol)
    try:
        bs = ticker.balance_sheet
        if bs is None or bs.empty:
            return []
        result = []
        for col in bs.columns:
            year_data = {"period": col.strftime("%Y") if hasattr(col, "strftime") else str(col)}
            for idx in bs.index:
                val = bs.loc[idx, col]
                key = idx.lower().replace(" ", "_").replace("/", "_")
                year_data[key] = None if pd.isna(val) else float(val)
            result.append(year_data)
        return result
    except Exception:
        return []


def get_cash_flow(symbol: str) -> list[dict]:
    ticker = yf.Ticker(symbol)
    try:
        cf = ticker.cashflow
        if cf is None or cf.empty:
            return []
        result = []
        for col in cf.columns:
            year_data = {"period": col.strftime("%Y") if hasattr(col, "strftime") else str(col)}
            for idx in cf.index:
                val = cf.loc[idx, col]
                key = idx.lower().replace(" ", "_").replace("/", "_")
                year_data[key] = None if pd.isna(val) else float(val)
            result.append(year_data)
        return result
    except Exception:
        return []


def get_analyst_ratings(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    recommendations = []
    try:
        rec = ticker.recommendations
        if rec is not None and not rec.empty:
            for _, row in rec.tail(10).iterrows():
                recommendations.append({
                    "firm": row.get("Firm", ""),
                    "to_grade": row.get("To Grade", ""),
                    "from_grade": row.get("From Grade", ""),
                    "action": row.get("Action", ""),
                })
    except Exception:
        pass

    return {
        "recommendation": info.get("recommendationKey", "N/A"),
        "num_analysts": info.get("numberOfAnalystOpinions"),
        "target_mean": info.get("targetMeanPrice"),
        "target_high": info.get("targetHighPrice"),
        "target_low": info.get("targetLowPrice"),
        "target_median": info.get("targetMedianPrice"),
        "recent_upgrades_downgrades": recommendations,
    }


def get_earnings_history(symbol: str) -> list[dict]:
    ticker = yf.Ticker(symbol)
    try:
        earnings = ticker.earnings_history
        if earnings is None or earnings.empty:
            return []
        result = []
        for _, row in earnings.tail(8).iterrows():
            result.append({
                "quarter": str(row.get("Earnings Date", "")),
                "eps_estimate": row.get("EPS Estimate"),
                "eps_actual": row.get("Reported EPS"),
                "surprise_pct": row.get("Surprise(%)"),
            })
        return result
    except Exception:
        return []


def get_sector_peers(symbol: str) -> list[str]:
    """Returns a hardcoded list of sector peers for common tickers."""
    peers_map = {
        "MSFT": ["AAPL", "GOOGL", "META", "AMZN", "ORCL"],
        "AAPL": ["MSFT", "GOOGL", "META", "AMZN", "NVDA"],
        "GOOGL": ["MSFT", "AAPL", "META", "AMZN", "SNAP"],
        "META": ["GOOGL", "SNAP", "PINS", "TWTR", "MSFT"],
        "AMZN": ["MSFT", "GOOGL", "AAPL", "WMT", "TGT"],
        "NVDA": ["AMD", "INTC", "QCOM", "AVGO", "TSM"],
        "TSLA": ["GM", "F", "RIVN", "LCID", "NIO"],
        "JPM": ["BAC", "WFC", "C", "GS", "MS"],
        "JNJ": ["PFE", "MRK", "ABT", "BMY", "ABBV"],
    }
    return peers_map.get(symbol.upper(), [])
