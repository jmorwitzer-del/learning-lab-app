from utils.polygon_data import fetch_daily

def fetch_history(start, end):
    spy = fetch_daily("SPY", start, end)
    vix = fetch_daily("VIX", start, end)

    if spy is None or vix is None:
        return None, None

    return spy, vix

