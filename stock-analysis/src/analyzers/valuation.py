"""DCF valuation model and fundamental ratio analysis."""
import numpy as np
from typing import Optional


def dcf_valuation(
    free_cash_flow: Optional[float],
    revenue: Optional[float],
    fcf_margin: Optional[float],
    revenue_growth_rate: Optional[float],
    shares_outstanding: Optional[int],
    discount_rate: float = 0.10,
    terminal_growth_rate: float = 0.03,
    projection_years: int = 10,
) -> dict:
    """
    Two-stage DCF: high-growth phase (years 1-5) then stable growth (years 6-10),
    plus terminal value.
    """
    if not free_cash_flow and fcf_margin and revenue:
        free_cash_flow = revenue * fcf_margin

    if not free_cash_flow or free_cash_flow <= 0:
        return {"error": "Insufficient FCF data for DCF model"}

    if not revenue_growth_rate or revenue_growth_rate <= 0:
        revenue_growth_rate = 0.05

    growth_phase1 = min(revenue_growth_rate, 0.40)
    growth_phase2 = max(growth_phase1 * 0.5, terminal_growth_rate + 0.01)

    cash_flows = []
    pv_cash_flows = []
    cumulative_fcf = free_cash_flow

    for year in range(1, projection_years + 1):
        g = growth_phase1 if year <= 5 else growth_phase2
        cumulative_fcf *= (1 + g)
        pv = cumulative_fcf / ((1 + discount_rate) ** year)
        cash_flows.append(round(cumulative_fcf))
        pv_cash_flows.append(round(pv))

    terminal_value = cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    pv_terminal = terminal_value / ((1 + discount_rate) ** projection_years)

    total_pv = sum(pv_cash_flows) + pv_terminal

    intrinsic_per_share = None
    if shares_outstanding and shares_outstanding > 0:
        intrinsic_per_share = total_pv / shares_outstanding

    return {
        "base_fcf": round(free_cash_flow),
        "projected_cash_flows": cash_flows,
        "pv_cash_flows": pv_cash_flows,
        "terminal_value": round(terminal_value),
        "pv_terminal_value": round(pv_terminal),
        "total_pv_operations": round(total_pv),
        "intrinsic_value_per_share": round(intrinsic_per_share, 2) if intrinsic_per_share else None,
        "assumptions": {
            "discount_rate": discount_rate,
            "terminal_growth_rate": terminal_growth_rate,
            "phase1_growth": round(growth_phase1, 4),
            "phase2_growth": round(growth_phase2, 4),
            "projection_years": projection_years,
        },
    }


def sensitivity_analysis(
    free_cash_flow: float,
    shares_outstanding: int,
    base_growth: float = 0.10,
    base_discount: float = 0.10,
) -> dict:
    growth_rates = [base_growth - 0.05, base_growth, base_growth + 0.05]
    discount_rates = [base_discount - 0.02, base_discount, base_discount + 0.02]

    matrix = {}
    for g in growth_rates:
        row = {}
        for d in discount_rates:
            result = dcf_valuation(
                free_cash_flow=free_cash_flow,
                revenue=None,
                fcf_margin=None,
                revenue_growth_rate=max(g, 0.01),
                shares_outstanding=shares_outstanding,
                discount_rate=max(d, 0.05),
            )
            row[f"{d:.0%}"] = result.get("intrinsic_value_per_share")
        matrix[f"{g:.0%}"] = row

    return {
        "growth_rates": [f"{g:.0%}" for g in growth_rates],
        "discount_rates": [f"{d:.0%}" for d in discount_rates],
        "matrix": matrix,
    }


def peer_comparison(symbol: str, current_metrics: dict, peers_data: list[dict]) -> dict:
    """Compare a stock's multiples against sector peers."""
    if not peers_data:
        return {}

    metrics_to_compare = ["pe_trailing", "pe_forward", "price_to_book", "price_to_sales", "ev_to_ebitda"]
    peer_averages = {}

    for metric in metrics_to_compare:
        values = [p.get(metric) for p in peers_data if p.get(metric) and p[metric] > 0]
        if values:
            peer_averages[metric] = {
                "mean": round(np.mean(values), 2),
                "median": round(np.median(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
            }

    comparisons = {}
    for metric in metrics_to_compare:
        current = current_metrics.get(metric)
        if current and peer_averages.get(metric):
            avg = peer_averages[metric]["mean"]
            comparisons[metric] = {
                "current": current,
                "peer_mean": avg,
                "premium_discount_pct": round((current / avg - 1) * 100, 1) if avg else None,
                "relative": "premium" if current > avg else "discount",
            }

    return {"peer_averages": peer_averages, "comparisons": comparisons}


def calculate_graham_number(eps: Optional[float], book_value: Optional[float]) -> Optional[float]:
    """Benjamin Graham's intrinsic value formula: sqrt(22.5 * EPS * BV)."""
    if eps and book_value and eps > 0 and book_value > 0:
        return round(np.sqrt(22.5 * eps * book_value), 2)
    return None


def calculate_fair_value_band(
    eps_forward: Optional[float],
    pe_low: float = 15,
    pe_mid: float = 20,
    pe_high: float = 25,
) -> Optional[dict]:
    if not eps_forward or eps_forward <= 0:
        return None
    return {
        "bear": round(eps_forward * pe_low, 2),
        "base": round(eps_forward * pe_mid, 2),
        "bull": round(eps_forward * pe_high, 2),
    }


def score_stock(overview: dict, valuation: dict, financials: dict) -> dict:
    """Simple scoring rubric (0-100) across 5 pillars."""
    scores = {}

    # Growth (0-20)
    rev_growth = financials.get("revenue_growth_yoy") or 0
    earn_growth = financials.get("earnings_growth_yoy") or 0
    growth_score = min(20, max(0, (rev_growth + earn_growth) / 2 * 100))
    scores["growth"] = round(growth_score, 1)

    # Profitability (0-20)
    op_margin = financials.get("operating_margin") or 0
    net_margin = financials.get("profit_margin") or 0
    roe = financials.get("return_on_equity") or 0
    profit_score = min(20, max(0, (op_margin * 30 + net_margin * 30 + roe * 40) * 20))
    scores["profitability"] = round(profit_score, 1)

    # Value (0-20) — lower PE/PB → higher score
    pe = valuation.get("pe_forward") or valuation.get("pe_trailing") or 50
    pb = valuation.get("price_to_book") or 10
    value_score = max(0, min(20, 20 - (pe - 15) * 0.3 - (pb - 3) * 0.5))
    scores["value"] = round(value_score, 1)

    # Financial health (0-20)
    current_ratio = financials.get("current_ratio") or 1
    dte = financials.get("debt_to_equity") or 2
    fcf = financials.get("free_cash_flow") or 0
    health_score = min(20, max(0, current_ratio * 5 + max(0, (2 - dte) * 5) + (5 if fcf > 0 else 0)))
    scores["financial_health"] = round(health_score, 1)

    # Momentum (0-20) — based on 52-week position
    price = overview.get("price") or 0
    high52 = overview.get("52w_high") or price
    low52 = overview.get("52w_low") or price
    if high52 > low52:
        position = (price - low52) / (high52 - low52)
        momentum_score = position * 20
    else:
        momentum_score = 10
    scores["momentum"] = round(momentum_score, 1)

    total = sum(scores.values())
    scores["total"] = round(total, 1)

    if total >= 70:
        scores["rating"] = "Strong Buy"
    elif total >= 55:
        scores["rating"] = "Buy"
    elif total >= 40:
        scores["rating"] = "Hold"
    elif total >= 25:
        scores["rating"] = "Underperform"
    else:
        scores["rating"] = "Sell"

    return scores
