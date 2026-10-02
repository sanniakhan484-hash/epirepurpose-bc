"""Placeholder app. Will read cached results from data/processed/."""
import streamlit as st

st.set_page_config(page_title="EpiRepurpose-BC", layout="wide")
st.title("EpiRepurpose-BC")
st.warning(
    "Research prototype. Outputs are hypotheses for experimental follow-up, "
    "not clinical recommendations."
)
st.info("Pipeline modules are under development. See docs/PROJECT_PROPOSAL.md.")
