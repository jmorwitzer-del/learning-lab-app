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

            # Divergence logic
            df["ES_move"] = df["Close_SPY"] - df["Open_SPY"]
            df["VIX_move"] = df["Close_VIX"] - df["Open_VIX"]

            df["ES_dir"] = np.where(df["ES_move"] > 0, 1,
                             np.where(df["ES_move"] < 0, -1, 0))
            df["VIX_dir"] = np.where(df["VIX_move"] > 0, 1,
                              np.where(df["VIX_move"] < 0, -1, 0))

            df["Signal"] = np.where(
                (df["ES_dir"] == 1) & (df["VIX_dir"] == -1), "LONG",
                np.where(
                    (df["ES_dir"] == -1) & (df["VIX_dir"] == 1), "SHORT",
                    "NONE"
                )
            )

            # Trade simulation
            trades = []
            equity = 10000
            position_size = 10000

            for i in range(len(df)):
                row = df.iloc[i]

                if row["Signal"] == "LONG":
                    ret = (row["Close_SPY"] - row["Open_SPY"]) / row["Open_SPY"]
                    pnl = position_size * ret
                    trades.append([row["Date"], "LONG", pnl])

                elif row["Signal"] == "SHORT":
                    ret = (row["Open_SPY"] - row["Close_SPY"]) / row["Open_SPY"]
                    pnl = position_size * ret
                    trades.append([row["Date"], "SHORT", pnl])

                equity += pnl

            trades_df = pd.DataFrame(trades, columns=["Date", "Side", "PnL"])

            if len(trades_df) > 0:
                trades_df["Equity"] = 10000 + trades_df["PnL"].cumsum()

            # Display results
            st.subheader("📈 Trade Log")
            st.dataframe(trades_df)

            st.subheader("💰 Final Equity")
            st.metric("Final Value", f"${equity:,.2f}")

            st.subheader("📉 Equity Curve")
            if len(trades_df) > 0:
                st.line_chart(trades_df.set_index("Date")["Equity"])

            # 📊 Strategy Analytics (Stage 1)
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

            # CSV Export
            st.subheader("⬇️ Download Results")
            csv = trades_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "backtest_results.csv", "text/csv")


