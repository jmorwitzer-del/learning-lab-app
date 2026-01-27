import datetime

def calculate_signal(spy_open, spy_now, vix_open, vix_now):
    # Calculate percentage changes
    spy_change = ((spy_now - spy_open) / spy_open) * 100
    vix_change = ((vix_now - vix_open) / vix_open) * 100

    # Determine signal
    if spy_change > 0 and vix_change < 0:
        signal = "LONG"
        confidence = min(abs(spy_change - vix_change), 5)
        reason = "SPY is rising while VIX is falling — bullish divergence."
    elif spy_change < 0 and vix_change > 0:
        signal = "SHORT"
        confidence = min(abs(spy_change - vix_change), 5)
        reason = "SPY is falling while VIX is rising — bearish divergence."
    else:
        signal = "FLAT"
        confidence = 0
        reason = "SPY and VIX are moving together — no clear divergence."

    # Confidence scale: 0 (low) to 5 (high)
    return {
        "signal": signal,
        "confidence": round(confidence, 2),
        "spy_change": round(spy_change, 2),
        "vix_change": round(vix_change, 2),
        "reason": reason,
        "timestamp": datetime.datetime.now().isoformat()
    }
