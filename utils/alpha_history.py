import os
import requests
import pandas as pd

ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"


def fetch_daily(symbol):
    """
    Fetch daily candles for a symbol from Alpha Vantage.
    Returns a DataFrame with Date, Open, High, Low, Close.
    """
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": ALPHA_KEY,
        "outputsize": "full"
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()

    if "Time Series (Daily)" not in data:
        return None

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close"
    })
    df = df[["Open", "High", "Low", "Close"]].astype(float)
    df["Date"] = df.index
    return df.reset_index(drop=True)


def fetch_history(start_date, end_date):
    """
    Fetch SPY + VIX daily data for a date range.
    Returns two DataFrames: ES proxy (SPY) and VIX.
    """
    spy = fetch_daily("SPY")
    vix = fetch_daily("VIX")

    if spy is None or vix is None:
        return None, None

    mask_spy = (spy["Date"] >= pd.to_datetime(start_date)) & (spy["Date"] <= pd.to_datetime(end_date))
    mask_vix = (vix["Date"] >= pd.to_datetime(start_date)) & (vix["Date"] <= pd.to_datetime(end_date))

    return spy[mask_spy].reset_index(drop=True), vix[mask_vix].reset_index(drop=True)
