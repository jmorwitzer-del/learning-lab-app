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


