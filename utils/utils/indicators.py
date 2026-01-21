import pandas as pd

def sma(data, period=20):
    return data['Close'].rolling(window=period).mean()

def ema(data, period=20):
    return data['Close'].ewm(span=period, adjust=False).mean()

def rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(data):
    ema12 = ema(data, 12)
    ema26 = ema(data, 26)
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def bollinger_bands(data, period=20, std_factor=2):
    mid = sma(data, period)
    std = data['Close'].rolling(period).std()
    upper = mid + std_factor * std
    lower = mid - std_factor * std
    return mid, upper, lower
