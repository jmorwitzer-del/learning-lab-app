import streamlit as st
from pathlib import Path

st.title("ES + VIX Divergence — Old vs New Model")

md_path = Path("lab_modules/es_vix_model_comparison.md")

if md_path.exists():
    st.markdown(md_path.read_text(), unsafe_allow_html=False)
else:
    st.warning("Model comparison notes file not found at lab_modules/es_vix_model_comparison.md")
