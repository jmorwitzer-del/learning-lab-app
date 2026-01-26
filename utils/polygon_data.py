import os
import requests
import pandas as pd

API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io/v2/aggs/ticker"


def fetch_intraday(symbol, timespan="minute", limit=2):
    url = f"{BASE_URL}/{symbol}/range/1/{timespan}/now"
    params = {"apiKey": API_KEY, "limit": limit}

    r = requests.get(url, params=params)
    data = r.json()

    if "results" not in data:
        return None

    df = pd.DataFrame(data["results"])
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    df = df.rename(columns={
        "t": "Date",
        "o": "Open",
        "h": "High",
        "l": "Low",
        "c": "Close",
        "v": "Volume"
    })
    return df.sort_values("Date")


def fetch_daily(symbol, start, end):
    url = f"{BASE_URL}/{symbol}/range/1/day/{start}/{end}"
    params = {"apiKey": API_KEY}

    r = requests.get(url, params=params)
    data = r.json()

    if "results" not in data:
        return None

    df = pd.DataFrame(data["results"])
    df["t"] = pd.to_datetime(df["t"], unit="ms")
    df = df.rename(columns={
        "t": "Date",
        "o": "Open",
        "h": "High",
        "l": "Low",
        "c": "Close",
        "v": "Volume"
    })
    return df.sort_values("Date")
