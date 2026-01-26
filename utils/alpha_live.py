import os
import requests
import pandas as pd

ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")
BASE_URL = "https://www.alphavantage.co/query"

def fetch_intraday(symbol, interval="1min"):
    if ALPHA_KEY is None:
        return None

    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_KEY,
        "outputsize": "compact",
    }
    r = requests.get(BASE_URL, params=params)
    data = r.json()

    key = f"Time Series ({interval})"
    if key not in data:
        return None

    df = pd.DataFrame.from_dict(data[key], orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.rename(
        columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume",
        }
    )
    df = df.astype(float)
    return df

def get_latest_spy_vix():
    spy = fetch_intraday("SPY")
    vix = fetch_intraday("VIX")

    if spy is None or vix is None or spy.empty or vix.empty:
        return None, None

    return spy.iloc[-1], vix.iloc[-1]

def live_divergence_signal():
    spy, vix = get_latest_spy_vix()
    if spy is None or vix is None:
        return None

    es_move = float(spy["Close"]) - float(spy["Open"])
    vix_move = float(vix["Close"]) - float(vix["Open"])

    es_dir = 1 if es_move > 0 else (-1 if es_move < 0 else 0)
    vix_dir = 1 if vix_move > 0 else (-1 if vix_move < 0 else 0)

    if es_dir == 1 and vix_dir == -1:
        signal = "LONG"
    elif es_dir == -1 and vix_dir == 1:
        signal = "SHORT"
    else:
        signal = "NONE"

    return {
        "signal": signal,
        "es_move": es_move,
        "vix_move": vix_move,
        "spy_close": float(spy["Close"]),
        "vix_close": float(vix["Close"]),
    }
