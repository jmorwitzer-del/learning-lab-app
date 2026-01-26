import pandas as pd
import numpy as np

def run_es_vix_engine(es_df, vix_df):
    # Clean numeric columns
    for df in [es_df, vix_df]:
        for col in ['Open', 'High', 'Low', 'Close']:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)

    # Sort and merge
    es_df = es_df[['Date', 'Open', 'High', 'Low', 'Close']].sort_values('Date')
    vix_df = vix_df[['Date', 'Open', 'High', 'Low', 'Close']].sort_values('Date')
    data = pd.merge(es_df, vix_df, on='Date', suffixes=('_ES', '_VIX'), how='inner')

    # ES/VIX moves
    data['ES_move'] = data['Close_ES'] - data['Open_ES']
    data['VIX_move'] = data['Close_VIX'] - data['Open_VIX']

    data['ES_dir'] = data['ES_move'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    data['VIX_dir'] = data['VIX_move'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))

    # Raw signal
    def signal(row):
        if row['ES_dir'] == 1 and row['VIX_dir'] == -1:
            return 1
        elif row['ES_dir'] == -1 and row['VIX_dir'] == 1:
            return -1
        return 0

    data['signal_raw'] = data.apply(signal, axis=1)

    # ATR(14)
    high = data['High_ES']
    low = data['Low_ES']
    close = data['Close_ES']
    prev_close = close.shift(1)

    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    data['ATR14'] = tr.rolling(14).mean()
    data['atr_ok'] = data['ATR14'] >= 20

    # VIX regimes
    def vix_regime(v):
        if v < 10 or v > 35:
            return 'skip'
        if v < 12 or v > 30:
            return 'half'
        return 'full'

    data['vix_regime'] = data['Close_VIX'].apply(vix_regime)

    # ES move filter
    data['valid_move'] = data['ES_move'].abs() >= 10

    # Volatility boost
    data['vol_boost'] = data['VIX_move'].abs() > 2

    # Final signal
    def final_signal(row):
        if row['signal_raw'] == 0:
            return 0
        if not row['valid_move']:
            return 0
        if not row['atr_ok']:
            return 0
        if row['vix_regime'] == 'skip':
            return 0
        return row['signal_raw']

    data['signal'] = data.apply(final_signal, axis=1)

    # Size multipliers
    data['size_mult_vol'] = data['vol_boost'].apply(lambda x: 2 if x else 1)
    data['size_mult_regime'] = data['vix_regime'].apply(lambda r: 0.5 if r == 'half' else (1 if r == 'full' else 0))
    data['size_mult'] = data['size_mult_vol'] * data['size_mult_regime']

    # P&L (flat)
    def pnl(row, tick_value, base_contracts, cost):
        if row['signal'] == 0:
            return 0
        points = row['ES_move'] * row['signal']
        contracts = base_contracts * row['size_mult']
        dollars = points / 0.25 * tick_value * contracts
        return dollars - cost

    data['PnL_MES'] = data.apply(lambda r: pnl(r, 1.25, 2, 1.0), axis=1)
    data['PnL_ES'] = data.apply(lambda r: pnl(r, 12.5, 2, 8.6), axis=1)

    # Monthly summary
    data['month'] = data['Date'].dt.to_period('M')
    monthly = data.groupby('month')[['PnL_MES', 'PnL_ES']].sum()

    # Stats
    trades = data[data['signal'] != 0]
    stats = {
        "Trades": len(trades),
        "Wins": (trades['PnL_MES'] > 0).sum(),
        "Losses": (trades['PnL_MES'] < 0).sum(),
        "Win Rate (%)": round((trades['PnL_MES'] > 0).mean() * 100, 2)
    }

    return monthly, stats, data
