import streamlit as st
import pandas as pd
import numpy as np

from utils.alpha_live import live_divergence_signal
from utils.alpha_history import fetch_history

# ---------------------------------------------------------
# LIVE SIGNAL SECTION (SPY + ^VIX via Yahoo)
# ---------------------------------------------------------

st.header("📡 Live ES + VIX Divergence Signal")

live = live_divergence_signal()

if live is None:
    st.info(
        "No intraday candles available right now. This usually happens when the US market is closed "
        "or Yahoo Finance hasn't published the latest minute bars yet."
    )
else:
    st.success(f"Signal: {live['signal']}")
    st.write(f"SPY move: {live['es_move']:.2f}")
    st.write(f"VIX move: {live['vix_move']:.2f}")
    st.write(f"SPY close: {live['spy_close']:.2f}")
    st.write(f"VIX close: {live['vix_close']:.2f}")
# ---------------------------------------------------------
# LIVE MARKET DASHBOARD (Stage 3)
# ---------------------------------------------------------

st.header("📊 Live Market Dashboard")

live = live_divergence_signal()

if live is None:
    st.info("Waiting for intraday data… market may be closed or data not yet available.")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("SPY Move (1m)", f"{live['es_move']:.4f}")

    with col2:
        st.metric("VIX Move (1m)", f"{live['vix_move']:.4f}")

    with col3:
        st.metric("Current Signal", live["signal"])

    st.write("---")

    # Signal preview if market closed now
    es_pct = (live["es_move"] / live["spy_close"]) * 100
    vix_pct = (live["vix_move"] / live["vix_close"]) * 100

    if es_pct > 0.05 and vix_pct < -0.05:
        preview = "LONG"
    elif es_pct < -0.05 and vix_pct > 0.05:
        preview = "SHORT"
    else:
        preview = "NONE"

    st.subheader("📌 If the market closed right now…")
    st.success(f"Tomorrow's signal would be: **{preview}**")

    st.write("---")

    # Live charts (SPY + VIX intraday)
    st.subheader("📈 Live SPY & VIX Charts")

    try:
        spy_live = fetch_intraday("SPY", period="1d", interval="1m")
        vix_live = fetch_intraday("^VIX", period="1d", interval="1m")

        if spy_live is not None:
            st.line_chart(spy_live["Close"], height=200)

        if vix_live is not None:
            st.line_chart(vix_live["Close"], height=200)

    except Exception as e:
        st.warning(f"Could not load live charts: {e}")

    st.write("---")

    # Sentiment gauge
    st.subheader("🧭 Market Sentiment Gauge")

    vix_level = live["vix_close"]

    if vix_level < 15:
        sentiment = "Low Fear (Bullish Bias)"
    elif vix_level < 25:
        sentiment = "Normal Volatility"
    else:
        sentiment = "High Fear (Bearish Bias)"

    st.info(f"VIX Level: **{vix_level:.2f}** → {sentiment}")

# ---------------------------------------------------------
# ---------------------------------------------------------
# BACKTEST SECTION (SPY + ^VIX via Yahoo)
# ---------------------------------------------------------

st.header("📅 Backtest ES + VIX Divergence Strategy")

start_date = st.date_input("Start date", key="bt_start")
end_date = st.date_input("End date", key="bt_end")

if st.button("Run Backtest", key="bt_run"):
    if start_date >= end_date:
        st.error("End date must be after start date.")
    else:
        spy, vix = fetch_history(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        if spy is None or vix is None or spy.empty or vix.empty:
            st.warning("Yahoo Finance returned no historical data for the selected range.")
        else:
            st.success("Historical data loaded successfully.")

            # Merge on Date
            df = pd.merge(spy, vix, on="Date", suffixes=("_SPY", "_VIX"))
            df = df.sort_values("Date").reset_index(drop=True)

            # Flatten MultiIndex columns
            df.columns = [
                f"{col[0]}{col[1]}" if isinstance(col, tuple) else col
                for col in df.columns
            ]

            # DEBUG: Show columns
            st.write("🔍 Columns returned by Yahoo Finance:", list(df.columns))

            # FIX: Rename Yahoo’s weird suffixes to expected names
            rename_map = {
                "OpenSPY": "Open_SPY",
                "CloseSPY": "Close_SPY",
                "HighSPY": "High_SPY",
                "LowSPY": "Low_SPY",
                "VolumeSPY": "Volume_SPY",

                "Open^VIX": "Open_VIX",
                "Close^VIX": "Close_VIX",
                "High^VIX": "High_VIX",
                "Low^VIX": "Low_VIX",
                "Volume^VIX": "Volume_VIX",
            }

            df = df.rename(columns=rename_map)

            # Validate required columns
            required_cols = ["Open_SPY", "Close_SPY", "Open_VIX", "Close_VIX"]
            missing = [c for c in required_cols if c not in df.columns]

            if missing:
                st.error(f"Missing expected columns after renaming: {missing}")
                st.stop()

            # ---------------------------------------------------------
            # Divergence logic with aggressive thresholds (0.05%)
            # ---------------------------------------------------------
            df["ES_pct"] = (df["Close_SPY"] - df["Open_SPY"]) / df["Open_SPY"]
            df["VIX_pct"] = (df["Close_VIX"] - df["Open_VIX"]) / df["Open_VIX"]

            threshold = 0.0005  # 0.05%

            df["Signal"] = np.where(
                (df["ES_pct"] > threshold) & (df["VIX_pct"] < -threshold), "LONG",
                np.where(
                    (df["ES_pct"] < -threshold) & (df["VIX_pct"] > threshold), "SHORT",
                    "NONE"
                )
            )

            # ---------------------------------------------------------
            # Trade simulation
            # ---------------------------------------------------------
            trades = []
            equity = 10000
            position_size = 10000

            for i in range(len(df)):
                row = df.iloc[i]

                if row["Signal"] == "LONG":
                    ret = (row["Close_SPY"] - row["Open_SPY"]) / row["Open_SPY"]
                    pnl = position_size * ret
                    trades.append([row["Date"], "LONG", pnl])
                    equity += pnl

                elif row["Signal"] == "SHORT":
                    ret = (row["Open_SPY"] - row["Close_SPY"]) / row["Open_SPY"]
                    pnl = position_size * ret
                    trades.append([row["Date"], "SHORT", pnl])
                    equity += pnl

            trades_df = pd.DataFrame(trades, columns=["Date", "Side", "PnL"])

            if len(trades_df) > 0:
                trades_df["Equity"] = 10000 + trades_df["PnL"].cumsum()

            # ---------------------------------------------------------
            # Display results
            # ---------------------------------------------------------
            st.subheader("📈 Trade Log")
            st.dataframe(trades_df)

            st.subheader("💰 Final Equity")
            st.metric("Final Value", f"${equity:,.2f}")

            st.subheader("📉 Equity Curve")
            if len(trades_df) > 0:
                st.line_chart(trades_df.set_index("Date")["Equity"])

            # ---------------------------------------------------------
            # 📊 Strategy Analytics (Stage 1)
            # ---------------------------------------------------------
            if len(trades_df) > 0:
                trades_df["Return"] = trades_df["PnL"] / position_size

                total_return = (equity / 10000) - 1
                wins = trades_df[trades_df["PnL"] > 0]
                losses = trades_df[trades_df["PnL"] < 0]

                win_rate = len(wins) / len(trades_df) if len(trades_df) > 0 else 0
                avg_win = wins["PnL"].mean() if len(wins) > 0 else 0
                avg_loss = losses["PnL"].mean() if len(losses) > 0 else 0

                expectancy = win_rate * avg_win + (1 - win_rate) * avg_loss

                equity_curve = trades_df["Equity"]
                running_max = equity_curve.cummax()
                drawdown = (equity_curve - running_max) / running_max
                max_drawdown = drawdown.min()

                if trades_df["Return"].std() != 0:
                    sharpe = (trades_df["Return"].mean() / trades_df["Return"].std()) * np.sqrt(252)
                else:
                    sharpe = 0.0

                st.subheader("📊 Strategy Stats")
                st.write(f"**Total Return:** {total_return:.2%}")
                st.write(f"**Win Rate:** {win_rate:.2%}")
                st.write(f"**Average Win:** ${avg_win:,.2f}")
                st.write(f"**Average Loss:** ${avg_loss:,.2f}")
                st.write(f"**Expectancy per Trade:** ${expectancy:,.2f}")
                st.write(f"**Max Drawdown:** {max_drawdown:.2%}")
                st.write(f"**Sharpe Ratio (approx):** {sharpe:.2f}")

            # ---------------------------------------------------------
            # CSV Export
            # ---------------------------------------------------------
            st.subheader("⬇️ Download Results")
            csv = trades_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "backtest_results.csv", "text/csv")



