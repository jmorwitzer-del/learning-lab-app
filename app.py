import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Learning Lab",
    page_icon="📈",
    layout="wide"
)

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("📘 Learning Lab")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Market Data", "Indicators", "News", "Journal", "Learning"]
)

# -----------------------------
# HOME PAGE
# -----------------------------
if page == "Home":
    st.title("📈 Learning Lab Dashboard")
    st.write("Welcome to your personal market learning environment.")

    st.subheader("Quick Start")
    st.write("""
    - Choose **Market Data** to view charts  
    - Choose **Indicators** to explore technical tools  
    - Choose **News** for market context  
    - Choose **Journal** to record insights  
    - Choose **Learning** for definitions and routines  
    """)

# -----------------------------
# MARKET DATA PAGE
# -----------------------------
elif page == "Market Data":
    st.title("📊 Market Data")

    ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, BTC-USD):", "AAPL")

    period = st.selectbox(
        "Select time period:",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"]
    )

    if st.button("Load Data"):
        data = yf.download(ticker, period=period)

        if data.empty:
            st.error("No data found. Check the ticker symbol.")
        else:
            st.line_chart(data["Close"])
            st.write(data.tail())

# -----------------------------
# INDICATORS PAGE
# -----------------------------
elif page == "Indicators":
    st.title("📐 Technical Indicators")

    ticker = st.text_input("Ticker:", "AAPL")
    period = st.selectbox("Period:", ["1mo", "3mo", "6mo", "1y"])

    if st.button("Calculate Indicators"):
        data = yf.download(ticker, period=period)

        if data.empty:
            st.error("No data found.")
        else:
            data["SMA_20"] = data["Close"].rolling(20).mean()
            data["SMA_50"] = data["Close"].rolling(50).mean()

            st.line_chart(data[["Close", "SMA_20", "SMA_50"]])
            st.write(data.tail())

# -----------------------------
# NEWS PAGE (STATIC PLACEHOLDER)
# -----------------------------
elif page == "News":
    st.title("📰 Market News")
    st.write("News integration will be added later using API keys.")
    st.info("For now, this is a placeholder.")

# -----------------------------
# JOURNAL PAGE
# -----------------------------
elif page == "Journal":
    st.title("📝 Market Journal")

    entry = st.text_area("Write your thoughts:")

    if st.button("Save Entry"):
        st.success("Entry saved (local session only).")

# -----------------------------
# LEARNING PAGE
# -----------------------------
elif page == "Learning":
    st.title("📚 Learning Center")

    st.subheader("Common Terms")
    st.write("""
    **SMA** — Simple Moving Average  
    **RSI** — Relative Strength Index  
    **MACD** — Moving Average Convergence Divergence  
    """)

    st.subheader("Daily Routine")
    st.write("""
    1. Check overnight news  
    2. Review charts  
    3. Note key levels  
    4. Record insights  
    """)
