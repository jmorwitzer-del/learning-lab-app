import streamlit as st
import pandas as pd
from utils.learning import run_es_vix_engine
from utils.alpha_live import live_divergence_signal

st.set_page_config(page_title="Learning Lab", layout="wide")

st.title("📈 Learning Lab — ES+VIX Divergence Engine")

tab1, tab2 = st.tabs(["Backtest (CSV)", "Live Signals (Alpha Vantage)"])

# -----------------------------
# TAB 1: BACKTEST (CSV UPLOAD)
# -----------------------------
with tab1:
    st.subheader("Backtest with ES & VIX CSVs")

    es_file = st.file_uploader("Upload ES CSV", type="csv", key="es_csv")
    vix_file = st.file_uploader("Upload VIX CSV", type="csv", key="vix_csv")

    if es_file and vix_file:
        es_df = pd.read_csv(es_file, parse_dates=["Date"])
        vix_df = pd.read_csv(vix_file, parse_dates=["Date"])

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
    else:
        st.info("Upload both ES and VIX CSV files to run the backtest.")

# -----------------------------
# TAB 2: LIVE SIGNALS (ALPHA VANTAGE)
# -----------------------------
with tab2:
    st.subheader("Live ES/VIX Divergence Signal (via Alpha Vantage)")

    st.caption("Uses SPY as ES proxy and VIX from Alpha Vantage. Refresh to update.")

    if st.button("Refresh live data"):
        pass  # Streamlit reruns the script on button press

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

# -----------------------------
# SIDEBAR MODULES
# -----------------------------
with st.sidebar:
    st.header("📚 Learning Lab Modules")
    st.markdown("[ES+VIX Model Comparison](lab_modules/es_vix_model_comparison.md)")
    st.markdown("[HFT Concepts](lab_modules/hft_concepts.md)")
    st.markdown("[Father–Son Prompts](lab_modules/father_son_prompts.md)")
    st.markdown("[Probability Engine Notes](lab_modules/probability_engine_notes.md)")
    # -----------------------------
# TAB 3: HISTORICAL AUTO-FETCH
# -----------------------------
with tab3:
    st.subheader("Automated Historical Backtest (No Uploads)")

    start = st.date_input("Start date")
    end = st.date_input("End date")

    if st.button("Run historical backtest"):
        from utils.alpha_history import fetch_history

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

