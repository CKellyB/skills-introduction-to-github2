"""Collects news from RSS feeds and optional NewsAPI using requests + BeautifulSoup."""
import requests
import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET


RSS_FEEDS = {
    "yahoo_finance": "https://finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
    "google_news": "https://news.google.com/rss/search?q={symbol}+stock&hl=en-US&gl=US&ceid=US:en",
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_bulletins",
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; StockAnalysisBot/1.0)",
    "Accept": "application/rss+xml, application/xml, text/xml",
}


def _parse_rss_date(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        dt = parsedate_to_datetime(date_str.strip())
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return date_str[:16] if len(date_str) >= 16 else date_str


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def _fetch_rss(url: str, timeout: int = 8) -> list[dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        items = root.findall(".//item")
        if not items:
            items = root.findall(".//atom:entry", ns)

        results = []
        for item in items:
            def get(tag):
                el = item.find(tag)
                if el is None:
                    for prefix in ("media:", "dc:", "content:"):
                        el = item.find(prefix + tag)
                    if el is None:
                        return ""
                return (el.text or "").strip()

            title = _clean_text(get("title"))
            link = get("link")
            if not link:
                link_el = item.find("link")
                if link_el is not None:
                    link = link_el.get("href", "")
            pub = _parse_rss_date(get("pubDate") or get("published") or get("updated"))
            summary = _clean_text(get("description") or get("summary") or get("content"))

            if title:
                results.append({
                    "title": title,
                    "url": link,
                    "published": pub,
                    "summary": summary,
                })
        return results
    except Exception:
        return []


def get_rss_news(symbol: str, max_per_feed: int = 10) -> list[dict]:
    articles = []
    seen_titles: set[str] = set()
    symbol_upper = symbol.upper()

    feeds = [
        ("Yahoo Finance", RSS_FEEDS["yahoo_finance"].format(symbol=symbol)),
        ("Google News", RSS_FEEDS["google_news"].format(symbol=symbol)),
        ("MarketWatch", RSS_FEEDS["marketwatch"]),
        ("CNBC", RSS_FEEDS["cnbc"]),
    ]

    for source_name, url in feeds:
        items = _fetch_rss(url)
        count = 0
        for item in items:
            title = item["title"]
            if not title or title in seen_titles:
                continue

            if source_name in ("MarketWatch", "CNBC"):
                combined = (title + " " + item.get("summary", "")).upper()
                if symbol_upper not in combined:
                    continue

            seen_titles.add(title)
            articles.append({
                "title": title,
                "summary": item.get("summary", ""),
                "url": item.get("url", ""),
                "published": item.get("published", ""),
                "source": source_name,
            })
            count += 1
            if count >= max_per_feed:
                break

    articles.sort(key=lambda x: x["published"], reverse=True)
    return articles[:40]


def get_newsapi_news(symbol: str, company_name: str = "") -> list[dict]:
    api_key = os.getenv("NEWS_API_KEY", "")
    if not api_key:
        return []
    try:
        query = f"{symbol} stock OR {company_name} stock" if company_name else f"{symbol} stock"
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "apiKey": api_key, "language": "en", "sortBy": "publishedAt", "pageSize": 20},
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        articles = []
        for item in resp.json().get("articles", []):
            articles.append({
                "title": item.get("title", ""),
                "summary": (item.get("description") or "")[:500],
                "url": item.get("url", ""),
                "published": (item.get("publishedAt") or "")[:16].replace("T", " "),
                "source": item.get("source", {}).get("name", "NewsAPI"),
            })
        return articles
    except Exception:
        return []


def get_all_news(symbol: str, company_name: str = "") -> list[dict]:
    rss = get_rss_news(symbol)
    api = get_newsapi_news(symbol, company_name)

    combined = {a["url"]: a for a in rss if a["url"]}
    for a in api:
        if a["url"] and a["url"] not in combined:
            combined[a["url"]] = a

    result = list(combined.values())
    result.sort(key=lambda x: x["published"], reverse=True)
    return result[:50]
