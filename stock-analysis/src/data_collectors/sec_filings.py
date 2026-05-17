"""Fetches 10-K, 10-Q, and 8-K filings from SEC EDGAR (no API key required)."""
import requests
import json
from typing import Optional


EDGAR_BASE = "https://data.sec.gov"
HEADERS = {"User-Agent": "StockAnalysisApp contact@example.com"}


def get_cik_for_ticker(symbol: str) -> Optional[str]:
    try:
        url = f"{EDGAR_BASE}/submissions/CIK{symbol.upper()}.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("cik", "").zfill(10)
    except Exception:
        pass

    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            tickers = resp.json()
            symbol_upper = symbol.upper()
            for entry in tickers.values():
                if entry.get("ticker", "").upper() == symbol_upper:
                    return str(entry["cik_str"]).zfill(10)
    except Exception:
        pass

    return None


def get_recent_filings(symbol: str, form_types: list[str] = None) -> list[dict]:
    if form_types is None:
        form_types = ["10-K", "10-Q", "8-K"]

    cik = get_cik_for_ticker(symbol)
    if not cik:
        return []

    try:
        url = f"{EDGAR_BASE}/submissions/CIK{cik}.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        data = resp.json()
        recent = data.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        descriptions = recent.get("primaryDocument", [])

        results = []
        for i, form in enumerate(forms):
            if form in form_types:
                accession = accessions[i].replace("-", "") if i < len(accessions) else ""
                acc_formatted = accessions[i] if i < len(accessions) else ""
                doc = descriptions[i] if i < len(descriptions) else ""
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{doc}"
                index_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}&dateb=&owner=include&count=10"

                results.append({
                    "form_type": form,
                    "filing_date": dates[i] if i < len(dates) else "",
                    "accession_number": acc_formatted,
                    "document_url": filing_url,
                    "index_url": index_url,
                    "cik": int(cik),
                })

                if len(results) >= 20:
                    break

        return results

    except Exception:
        return []


def get_company_facts(symbol: str) -> dict:
    """Fetches structured financial facts from EDGAR XBRL (income, assets, etc.)."""
    cik = get_cik_for_ticker(symbol)
    if not cik:
        return {}

    try:
        url = f"{EDGAR_BASE}/api/xbrl/companyfacts/CIK{cik}.json"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return {}

        facts = resp.json()
        us_gaap = facts.get("facts", {}).get("us-gaap", {})

        extracted = {}

        concepts = {
            "Revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
            "NetIncome": ["NetIncomeLoss", "NetIncome"],
            "OperatingIncome": ["OperatingIncomeLoss"],
            "EPS_Basic": ["EarningsPerShareBasic"],
            "EPS_Diluted": ["EarningsPerShareDiluted"],
            "TotalAssets": ["Assets"],
            "TotalLiabilities": ["Liabilities"],
            "StockholdersEquity": ["StockholdersEquity"],
            "CashAndEquivalents": ["CashAndCashEquivalentsAtCarryingValue"],
            "FreeCashFlow": ["PaymentsToAcquirePropertyPlantAndEquipment"],
            "RD_Expense": ["ResearchAndDevelopmentExpense"],
            "SharesOutstanding": ["CommonStockSharesOutstanding"],
        }

        for label, concept_names in concepts.items():
            for concept in concept_names:
                if concept in us_gaap:
                    units = us_gaap[concept].get("units", {})
                    unit_data = units.get("USD", units.get("shares", units.get("USD/shares", [])))
                    annual = [
                        entry for entry in unit_data
                        if entry.get("form") in ("10-K", "10-K/A") and entry.get("fp") == "FY"
                    ]
                    annual.sort(key=lambda x: x.get("end", ""), reverse=True)
                    if annual:
                        extracted[label] = annual[:5]
                    break

        return extracted

    except Exception:
        return {}


def extract_revenue_trend(symbol: str) -> list[dict]:
    facts = get_company_facts(symbol)
    revenue_data = facts.get("Revenue", [])
    return [
        {"year": entry.get("end", "")[:4], "value": entry.get("val")}
        for entry in revenue_data
        if entry.get("val") is not None
    ]


def extract_net_income_trend(symbol: str) -> list[dict]:
    facts = get_company_facts(symbol)
    ni_data = facts.get("NetIncome", [])
    return [
        {"year": entry.get("end", "")[:4], "value": entry.get("val")}
        for entry in ni_data
        if entry.get("val") is not None
    ]
