from utils.alpha_live import live_divergence_signal

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

