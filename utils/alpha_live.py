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
