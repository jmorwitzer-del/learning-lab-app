import streamlit as st
import pandas as pd
import yfinance as yf

# ---------------------------------------------------------
# APP CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Learning Lab",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("📘 Learning Lab")
section = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Market Data", "Indicators", "News", "Journal", "Learning"]
)

# ---------------------------------------------------------
# HELPER: LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_price_data(ticker, period="1y", interval="1d"):
    try:
        data = yf.download(ticker, period=period, interval=interval)
        if data.empty:
            return None
        return data
    except Exception:
        return None

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------
if section == "Dashboard":
    st.title("📈 Learning Lab Dashboard")
    st.write("Welcome to your personal market learning environment.")

    st.subheader("Quick Start")
    st.markdown("""
    - Choose **Market Data** to view charts  
    - Choose **Indicators** to explore technical tools  
    - Choose **News** for market context  
    - Choose **Journal** to record insights  
    - Choose **Learning** for definitions and routines  
    """)

# ---------------------------------------------------------
# MARKET DATA
# ---------------------------------------------------------
elif section == "Market Data":
    st.title("📊 Market Data")

    ticker = st.text_input("Enter a ticker symbol", "AAPL")
    period = st.selectbox("Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"])
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d", "1wk"])

    data = load_price_data(ticker, period, interval)

    if data is None:
        st.error("No data found. Try another ticker.")
    else:
        st.line_chart(data["Close"])
        st.dataframe(data.tail())

# ---------------------------------------------------------
# INDICATORS (placeholder until utils/indicators.py is added)
# ---------------------------------------------------------
elif section == "Indicators":
    st.title("📐 Indicators")
    st.info("Technical indicators will appear here once indicator utilities are added.")

# ---------------------------------------------------------
# NEWS (placeholder until utils/news.py is added)
# ---------------------------------------------------------
elif section == "News":
    st.title("📰 Market News")

    from utils.news import get_news, fetch_price_reaction

    query = st.text_input("Search ticker or keyword", "AAPL")

    if query:
        st.subheader(f"Latest news for: {query}")

        df = get_news(query)

        if df.empty:
            st.warning("No news found.")
        else:
            for _, row in df.iterrows():
                with st.expander(f"{row['title']}"):
                    st.write(f"**Source:** {row['source']}")
                    st.write(f"**Published:** {row['published']}")
                    if row["sentiment"] is not None:
                        st.write(f"**Sentiment:** {row['sentiment']:.2f}")
                    st.write(f"[Read article]({row['url']})")

            st.subheader("📈 Price Reaction (AlphaVantage)")
            price = fetch_price_reaction(query)

            if price is not None:
                st.line_chart(price["close"])
            else:
                st.info("No price data available.")


# ---------------------------------------------------------
# JOURNAL (CSV persistence added later)
# ---------------------------------------------------------
elif section == "Journal":
    st.title("📝 Journal")

    st.write("Record your thoughts, insights, and observations.")

    entry = st.text_area("New entry")
    if st.button("Save Entry"):
        st.success("Entry saved (persistence will be added soon).")

# ---------------------------------------------------------
# LEARNING CENTER
# ---------------------------------------------------------
elif section == "Learning":
    st.title("📚 Learning Center")

    st.markdown("""
    This section will include:
    - Definitions  
    - Examples  
    - Routines  
    - Father–son guided prompts  
    """)

    st.info("Learning modules will be added shortly.")
