import pandas as pd
from utils.yahoo_data import fetch_daily


def fetch_history(start: str, end: str):
    """
    Fetch daily SPY and VIX (^VIX) history between start and end (YYYY-MM-DD).
    Returns (spy_df, vix_df) or (None, None) if either is missing.
    """
    spy = fetch_daily("SPY", start, end)
    vix = fetch_daily("^VIX", start, end)

    if spy is None or vix is None or spy.empty or vix.empty:
        return None, None

    spy["Date"] = pd.to_datetime(spy["Date"]).dt.date
    vix["Date"] = pd.to_datetime(vix["Date"]).dt.date

    return spy, vix
