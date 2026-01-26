import streamlit as st
import pandas as pd
from utils.learning import run_es_vix_engine

st.title("Learning Lab — ES+VIX Divergence Engine")

st.write("Upload ES and VIX CSV files to run the engine.")

es_file = st.file_uploader("Upload ES CSV", type="csv")
vix_file = st.file_uploader("Upload VIX CSV", type="csv")

if es_file and vix_file:
    es_df = pd.read_csv(es_file, parse_dates=['Date'])
    vix_df = pd.read_csv(vix_file, parse_dates=['Date'])

    monthly, stats, full_data = run_es_vix_engine(es_df, vix_df)

    st.subheader("Monthly P&L Summary")
    st.dataframe(monthly)

    st.subheader("Stats")
    for k, v in stats.items():
        st.write(f"{k}: {v}")

    st.subheader("Trade Log")
    st.dataframe(full_data[['Date','signal','ES_move','VIX_move','ATR14','vix_regime','size_mult','PnL_MES']])

with st.sidebar:
    st.header("Learning Lab Modules")
    st.markdown("[Model Comparison](lab_modules/es_vix_model_comparison.md)")
    st.markdown("[HFT Concepts](lab_modules/hft_concepts.md)")
    st.markdown("[Father–Son Prompts](lab_modules/father_son_prompts.md)")
    st.markdown("[Probability Engine Notes](lab_modules/probability_engine_notes.md)")

