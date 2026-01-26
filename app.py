import streamlit as st
import pandas as pd

from utils.learning import run_es_vix_engine
from utils.alpha_live import live_divergence_signal
from utils.alpha_history import fetch_history


st.set_page_config(page_title="Learning Lab", layout="wide")

st.title("📈 Learning Lab — ES+VIX Divergence Engine")

# ---------------------------------------------------------
# CREATE TWO TABS (NO CSV UPLOADS)
# ---------------------------------------------------------
tab1, tab2 = st.tabs(
    [
        "Live Signals",
        "Historical Auto‑Fetch"
    ]
)

# ---------------------------------------------------------
# TAB 1 — LIVE SIGNALS
# ---------------------------------------------------------
with tab1:
    st.subheader("Live ES/VIX Divergence Signal (via Alpha Vantage)")

    st.caption("Uses SPY as ES proxy and VIX from Alpha Vantage. Refresh to update.")

    if st.button("Refresh live data"):
        pass  # Streamlit reruns the script automatically

    live = live_divergence_signal()

    if live is None:
        st.error("Could not fetch live data. Check your ALPHA_VANTAGE_KEY secret or API rate limits.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("SPY Price (ES proxy)", f"{live['spy_close']:.2f}")
        col2.metric("VIX Level", f"{live['vix_close']:.2f}")
        col3.metric("Signal", live["signal"])

        st.write(f"ES proxy move (SPY): {live['es_move']:.2f}")
        st.write(f"VIX move: {live['vix_move']:.2f}")

        if live["signal"] == "LONG":
            st.success("🚀 LONG signal: ES up, VIX down (divergence).")
        elif live["signal"] == "SHORT":
            st.error("🔻 SHORT signal: ES down, VIX up (divergence).")
        else:
            st.info("No clean divergence signal right now.")

# ---------------------------------------------------------
# TAB 2 — HISTORICAL AUTO‑FETCH
# ---------------------------------------------------------
with tab2:
    st.subheader("Automated Historical Backtest (No Uploads)")

    start = st.date_input("Start date")
    end = st.date_input("End date")

    if st.button("Run historical backtest"):
        es_df, vix_df = fetch_history(start, end)

        if es_df is None or vix_df is None or es_df.empty or vix_df.empty:
            st.error("Could not fetch historical data. Check API key or date range.")
        else:
            monthly, stats, full_data = run_es_vix_engine(es_df, vix_df)

            st.markdown("### 📅 Monthly P&L Summary")
            st.dataframe(monthly)

            st.markdown("### 📊 Stats")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Trades", stats["Trades"])
            col2.metric("Wins", stats["Wins"])
            col3.metric("Losses", stats["Losses"])
            col4.metric("Win Rate (%)", stats["Win Rate (%)"])

            st.markdown("### 📝 Trade Log")
            st.dataframe(
                full_data[
                    [
                        "Date",
                        "signal",
                        "ES_move",
                        "VIX_move",
                        "ATR14",
                        "vix_regime",
                        "size_mult",
                        "PnL_MES",
                    ]
                ]
            )
