import yfinance as yf
import pandas as pd


def fetch_intraday(symbol: str, period: str = "1d", interval: str = "1m") -> pd.DataFrame | None:
    """
    Fetch recent intraday data for a symbol from Yahoo Finance.
    Default: last 1 day, 1-minute bars.
    """
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    if data is None or data.empty:
        return None

    df = data.reset_index()
    # Standardize column names
    df = df.rename(columns={
        "Open": "Open",
        "Close": "Close",
        "High": "High",
        "Low": "Low",
        "Volume": "Volume"
    })
    return df


def fetch_daily(symbol: str, start: str, end: str) -> pd.DataFrame | None:
    """
    Fetch daily OHLC data for a symbol between start and end (YYYY-MM-DD).
    """
    data = yf.download(symbol, start=start, end=end, interval="1d", progress=False)
    if data is None or data.empty:
        return None

    df = data.reset_index()
    # Ensure a clean Date column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    elif "Datetime" in df.columns:
        df["Date"] = pd.to_datetime(df["Datetime"]).dt.date

    df = df.rename(columns={
        "Open": "Open",
        "Close": "Close",
        "High": "High",
        "Low": "Low",
        "Volume": "Volume"
    })

    return df[["Date", "Open", "Close", "High", "Low", "Volume"]]
