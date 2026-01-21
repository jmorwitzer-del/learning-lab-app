import streamlit as st
import pandas as pd
from utils.news import get_news, fetch_price_reaction

st.title("📰 Market News Intelligence")

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
