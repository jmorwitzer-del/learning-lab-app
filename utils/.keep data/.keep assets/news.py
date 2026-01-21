import requests
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# API KEYS (replace placeholders)
# -----------------------------
NEWSAPI_KEY = "8ba145b0434342d0b6fd7ae32a4ea0c8"
FINNHUB_KEY = "d5n0fb9r01qj2afii6pgd5n0fb9r01qj2afii6q0"
MARKETAUX_KEY = "syf8Is3MD7bwkQRihpo9p0z8Hb70GmVL8qEmsAhg"
ALPHAVANTAGE_KEY = "Z0QQ8PAUM5E999U6"


# -----------------------------
# NewsAPI
# -----------------------------
def fetch_newsapi(query):
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}"
    )
    r = requests.get(url).json()
    if "articles" not in r:
        return []
    return [
        {
            "source": a.get("source", {}).get("name"),
            "title": a.get("title"),
            "url": a.get("url"),
            "published": a.get("publishedAt"),
            "sentiment": None,
        }
        for a in r["articles"]
    ]


# -----------------------------
# Finnhub
# -----------------------------
def fetch_finnhub(query):
    now = datetime.utcnow()
    frm = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    to = now.strftime("%Y-%m-%d")

    url = (
        f"https://finnhub.io/api/v1/company-news?"
        f"symbol={query}&from={frm}&to={to}&token={FINNHUB_KEY}"
    )
    r = requests.get(url).json()
    if not isinstance(r, list):
        return []
    return [
        {
            "source": a.get("source"),
            "title": a.get("headline"),
            "url": a.get("url"),
            "published": a.get("datetime"),
            "sentiment": a.get("sentiment"),
        }
        for a in r
    ]


# -----------------------------
# MarketAux
# -----------------------------
def fetch_marketaux(query):
    url = (
        f"https://api.marketaux.com/v1/news/all?"
        f"symbols={query}&filter_entities=true&language=en&api_token={MARKETAUX_KEY}"
    )
    r = requests.get(url).json()
    if "data" not in r:
        return []
    return [
        {
            "source": a.get("source"),
            "title": a.get("title"),
            "url": a.get("url"),
            "published": a.get("published_at"),
            "sentiment": a.get("entities", [{}])[0].get("sentiment_score"),
        }
        for a in r["data"]
    ]


# -----------------------------
# AlphaVantage price reaction
# -----------------------------
def fetch_price_reaction(symbol):
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHAVANTAGE_KEY}"
    )
    r = requests.get(url).json()
    if "Time Series (Daily)" not in r:
        return None

    df = pd.DataFrame(r["Time Series (Daily)"]).T
    df.index = pd.to_datetime(df.index)
    df = df.rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        }
    )
    df = df.astype(float)
    return df.sort_index()


# -----------------------------
# Unified feed
# -----------------------------
def get_news(query):
    feed = []
    feed.extend(fetch_newsapi(query))
    feed.extend(fetch_finnhub(query))
    feed.extend(fetch_marketaux(query))

    # Clean + sort
    df = pd.DataFrame(feed)
    if df.empty:
        return df

    df["published"] = pd.to_datetime(df["published"], errors="coerce")
    df = df.dropna(subset=["published"])
    df = df.sort_values("published", ascending=False)

    return df
