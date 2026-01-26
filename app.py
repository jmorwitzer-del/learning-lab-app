from utils.alpha_live import live_divergence_signal
import streamlit as st
from utils.alpha_live import live_divergence_signal
from utils.alpha_history import fetch_history

st.header("📡 Live ES + VIX Divergence Signal")

live = live_divergence_signal()

if live is None:
    st.warning("Live data unavailable. Polygon may be down or returning empty results.")
else:
    st.success(f"Signal: {live['signal']}")
    st.write(f"SPY move: {live['es_move']:.2f}")
    st.write(f"VIX move: {live['vix_move']:.2f}")
    st.write(f"SPY close: {live['spy_close']:.2f}")
    st.write(f"VIX close: {live['vix_close']:.2f}")
    st.header("📅 Backtest ES + VIX Divergence")
    st.header("📅 Backtest ES + VIX Divergence")

start_date = st.date_input("Start date")
end_date = st.date_input("End date")

if st.button("Run Backtest"):
    if start_date >= end_date:
        st.error("End date must be after start date.")
    else:
        spy, vix = fetch_history(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        if spy is None or vix is None:
            st.warning("Polygon returned no historical data for the selected range.")
        else:
            st.success("Historical data loaded successfully.")

            st.subheader("SPY Data")
            st.dataframe(spy)

            st.subheader("VIX Data")
            st.dataframe(vix)


start_date = st.date_input("Start date")
end_date = st.date_input("End date")

if st.button("Run Backtest"):
    if start_date >= end_date:
        st.error("End date must be after start date.")
    else:
        spy, vix = fetch_history(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        if spy is None or vix is None:
            st.warning("Polygon returned no historical data for the selected range.")
        else:
            st.success("Historical data loaded successfully.")

            st.subheader("SPY Data")
            st.dataframe(spy)

            st.subheader("VIX Data")
            st.dataframe(vix)


import streamlit as st
import pandas as pd
import numpy as np
from utils.alpha_history import fetch_history

st.header("📅 Backtest ES + VIX Divergence Strategy")

# --- UI ---
start_date = st.date_input("Start date")
end_date = st.date_input("End date")

if st.button("Run Backtest"):
    if start_date >= end_date:
        st.error("End date must be after start date.")
    else:
        spy, vix = fetch_history(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        if spy is None or vix is None:
            st.warning("Polygon returned no historical data for the selected range.")
        else:
            st.success("Historical data loaded successfully.")

            # --- Merge datasets ---
            df = pd.merge(spy, vix, on="Date", suffixes=("_SPY", "_VIX"))
            df = df.sort_values("Date").reset_index(drop=True)

            # --- Divergence logic ---
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

            # --- Trade simulation ---
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

                else:
                    continue

                equity += pnl

            # --- Convert trades to DataFrame ---
            trades_df = pd.DataFrame(trades, columns=["Date", "Side", "PnL"])

            # --- Equity curve ---
            if len(trades_df) > 0:
                trades_df["Equity"] = 10000 + trades_df["PnL"].cumsum()

            # --- Display results ---
            st.subheader("📈 Trade Log")
            st.dataframe(trades_df)

            st.subheader("💰 Final Equity")
            st.metric("Final Value", f"${equity:,.2f}")

            st.subheader("📉 Equity Curve")
            if len(trades_df) > 0:
                st.line_chart(trades_df.set_index("Date")["Equity"])

            # --- CSV Export ---
            st.subheader("⬇️ Download Results")
            csv = trades_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "backtest_results.csv", "text/csv")


