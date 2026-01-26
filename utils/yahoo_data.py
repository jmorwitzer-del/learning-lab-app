import yfinance as yf
import pandas as pd

def fetch_intraday(symbol: str, period: str = "1d", interval: str = "1m"):
    """
    Fetch intraday data (1-minute bars) for the given symbol.
    """
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    if data is None or data.empty:
        return None

    df = data.reset_index()

    # Normalize column names
    df = df.rename(columns={
        "Open": "Open",
        "Close": "Close",
        "High": "High",
        "Low": "Low",
        "Volume": "Volume"
    })

    return df


def fetch_daily(symbol: str, start: str, end: str):
    """
    Fetch daily OHLCV data for the given symbol between start and end dates.
    Handles Yahoo Finance quirks, MultiIndex columns, and missing fields.
    """
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

    # Robust normalization of OHLCV columns
    rename_map = {}
    for col in df.columns:
        col_str = str(col).lower()  # Avoid AttributeError on non-string columns

        if col_str == "open":
            rename_map[col] = "Open"
        elif col_str == "close":
            rename_map[col] = "Close"
        elif col_str == "high":
            rename_map[col] = "High"
        elif col_str == "low":
            rename_map[col] = "Low"
        elif col_str == "volume":
            rename_map[col] = "Volume"

    df = df.rename(columns=rename_map)

    # Required fields
    required = ["Date", "Open", "Close"]
    if not all(col in df.columns for col in required):
        return None

    # Fill optional fields if missing
    for opt in ["High", "Low", "Volume"]:
        if opt not in df.columns:
            df[opt] = pd.NA

    return df[["Date", "Open", "Close", "High", "Low", "Volume"]]
