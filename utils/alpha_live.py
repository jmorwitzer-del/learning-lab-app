import numpy as np
from utils.yahoo_data import fetch_intraday


def live_divergence_signal():
    """
    Compute live ES (SPY) + VIX divergence using Yahoo intraday data.
    Uses the last two 1-minute bars for each.
    Returns:
        dict with keys: signal, es_move, vix_move, spy_close, vix_close
        or None if data unavailable.
    """
    spy_df = fetch_intraday("SPY", period="1d", interval="1m")
    vix_df = fetch_intraday("^VIX", period="1d", interval="1m")

    if spy_df is None or vix_df is None:
        return None

    # Need at least 2 bars to compute a move
    if len(spy_df) < 2 or len(vix_df) < 2:
        return None

    spy_last = spy_df.iloc[-1]
    spy_prev = spy_df.iloc[-2]

    vix_last = vix_df.iloc[-1]
    vix_prev = vix_df.iloc[-2]

    es_move = spy_last["Close"] - spy_prev["Close"]
    vix_move = vix_last["Close"] - vix_prev["Close"]

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
        "es_move": float(es_move),
        "vix_move": float(vix_move),
        "spy_close": float(spy_last["Close"]),
        "vix_close": float(vix_last["Close"]),
    }

from utils.polygon_data import fetch_intraday

def live_divergence_signal():
    spy = fetch_intraday("SPY", limit=2)
    vix = fetch_intraday("VIX", limit=2)

    if spy is None or vix is None:
        return None

    spy_latest = spy.iloc[-1]
    vix_latest = vix.iloc[-1]

    es_move = spy_latest["Close"] - spy_latest["Open"]
    vix_move = vix_latest["Close"] - vix_latest["Open"]

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
        "spy_close": spy_latest["Close"],
        "vix_close": vix_latest["Close"]
    }

