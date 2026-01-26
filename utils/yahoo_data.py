import yfinance as yf
import pandas as pd

def fetch_intraday(symbol: str, period: str = "1d", interval: str = "1m"):
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    if data is None or data.empty:
        return None

    df = data.reset_index()
    df = df.rename(columns={
        "Open": "Open",
        "Close": "Close",
        "High": "High",
        "Low": "Low",
        "Volume": "Volume"
    })
    return df


def fetch_daily(symbol: str, start: str, end: str):
    data = yf.download(symbol, start=start, end=end, interval="1d", progress=False)

    if data is None or data.empty:
        return None

    df = data.reset_index()

    # Normalize date column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    elif "Datetime" in df.columns:
        df["Date"] = pd.to_datetime(df["Datetime"]).dt.date
    else:
        return None

    # Normalize OHLC columns
    rename_map = {}
    for col in df.columns:
        if col.lower() == "open":
            rename_map[col] = "Open"
        if col.lower() == "close":
            rename_map[col] = "Close"
        if col.lower() == "high":
            rename_map[col] = "High"
        if col.lower() == "low":
            rename_map[col] = "Low"
        if col.lower() == "volume":
            rename_map[col] = "Volume"

    df = df.rename(columns=rename_map)

    required = ["Date", "Open", "Close"]
    if not all(col in df.columns for col in required):
        return None

    return df[["Date", "Open", "Close", "High", "Low", "Volume"]]

