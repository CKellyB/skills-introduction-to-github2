"""
Stock Analysis App — Flask backend.
Aggregates financial data, SEC filings, news, and AI-powered valuation analysis.

Set DEMO_MODE=true to use sample MSFT data without network access.
Set ANTHROPIC_API_KEY for AI-powered analysis.
"""
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))

DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

from src.data_collectors.stock_data import (
    get_stock_overview, get_valuation_metrics, get_financial_summary,
    get_historical_prices, get_analyst_ratings, get_earnings_history,
)
from src.data_collectors.sec_filings import (
    get_recent_filings, get_company_facts,
    extract_revenue_trend, extract_net_income_trend,
)
from src.data_collectors.news import get_all_news
from src.analyzers.valuation import (
    dcf_valuation, sensitivity_analysis,
    calculate_graham_number, calculate_fair_value_band, score_stock,
)
from src.analyzers.claude_analyst import run_ai_analysis
from src.demo_data import MSFT_DEMO

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

POPULAR_STOCKS = [
    {"symbol": "MSFT", "name": "Microsoft"},
    {"symbol": "AAPL", "name": "Apple"},
    {"symbol": "GOOGL", "name": "Alphabet"},
    {"symbol": "AMZN", "name": "Amazon"},
    {"symbol": "NVDA", "name": "NVIDIA"},
    {"symbol": "META", "name": "Meta"},
    {"symbol": "TSLA", "name": "Tesla"},
    {"symbol": "JPM", "name": "JPMorgan Chase"},
    {"symbol": "JNJ", "name": "Johnson & Johnson"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway"},
]


@app.route("/")
def index():
    return render_template("index.html", popular_stocks=POPULAR_STOCKS, demo_mode=DEMO_MODE)


@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if request.method == "POST":
        symbol = request.form.get("symbol", "").strip().upper()
    else:
        symbol = request.args.get("symbol", "").strip().upper()

    if not symbol:
        return redirect(url_for("index"))

    return render_template("loading.html", symbol=symbol, demo_mode=DEMO_MODE)


@app.route("/api/analyze/<symbol>")
def api_analyze(symbol: str):
    symbol = symbol.strip().upper()

    # Demo mode: return sample MSFT data
    if DEMO_MODE or symbol == "DEMO":
        data = dict(MSFT_DEMO)
        data["symbol"] = symbol if symbol != "DEMO" else "MSFT"
        return jsonify(data)

    try:
        overview = get_stock_overview(symbol)
        if not overview.get("price"):
            return jsonify({"error": f"Could not find stock data for '{symbol}'. Check the ticker symbol."}), 404

        valuation = get_valuation_metrics(symbol)
        financials = get_financial_summary(symbol)
        prices = get_historical_prices(symbol, "1y")
        analyst_ratings = get_analyst_ratings(symbol)
        earnings = get_earnings_history(symbol)
        sec_filings = get_recent_filings(symbol)
        company_facts = get_company_facts(symbol)
        news = get_all_news(symbol, overview.get("name", ""))

        revenue_trend = extract_revenue_trend(symbol)
        ni_trend = extract_net_income_trend(symbol)

        dcf_result = dcf_valuation(
            free_cash_flow=financials.get("free_cash_flow"),
            revenue=financials.get("revenue_ttm"),
            fcf_margin=financials.get("profit_margin"),
            revenue_growth_rate=financials.get("revenue_growth_yoy"),
            shares_outstanding=overview.get("shares_outstanding"),
        )

        scores = score_stock(overview, valuation, financials)

        sens = None
        fcf = financials.get("free_cash_flow")
        shares = overview.get("shares_outstanding")
        if fcf and fcf > 0 and shares:
            sens = sensitivity_analysis(
                fcf, shares,
                base_growth=financials.get("revenue_growth_yoy") or 0.10,
            )

        graham = calculate_graham_number(financials.get("eps_trailing"), valuation.get("book_value_per_share"))
        fair_value_band = calculate_fair_value_band(financials.get("eps_forward"))

        ai_result = run_ai_analysis(
            symbol=symbol,
            overview=overview,
            valuation=valuation,
            financials=financials,
            dcf_result=dcf_result,
            analyst_ratings=analyst_ratings,
            news_articles=news,
            sec_filings=sec_filings,
            scores=scores,
            company_facts=company_facts,
        )

        return jsonify({
            "symbol": symbol,
            "overview": overview,
            "valuation": valuation,
            "financials": financials,
            "prices": prices,
            "analyst_ratings": analyst_ratings,
            "earnings_history": earnings,
            "sec_filings": sec_filings,
            "news": news,
            "revenue_trend": revenue_trend,
            "ni_trend": ni_trend,
            "dcf_result": dcf_result,
            "sensitivity": sens,
            "graham_number": graham,
            "fair_value_band": fair_value_band,
            "scores": scores,
            "ai_analysis": ai_result,
        })

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/api/price/<symbol>")
def api_price(symbol: str):
    symbol = symbol.strip().upper()
    if DEMO_MODE:
        from src.demo_data import MSFT_DEMO
        return jsonify(MSFT_DEMO["prices"])
    period = request.args.get("period", "1y")
    try:
        prices = get_historical_prices(symbol, period)
        return jsonify(prices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/stock/<symbol>")
def stock_detail(symbol: str):
    return render_template("analysis.html", symbol=symbol.upper(), demo_mode=DEMO_MODE)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    mode = "DEMO" if DEMO_MODE else "LIVE"
    print(f"StockLens running at http://localhost:{port} [{mode} MODE]")
    app.run(host="0.0.0.0", port=port, debug=debug)
