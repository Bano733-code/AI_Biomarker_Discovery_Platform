import streamlit as st


st.set_page_config(
    page_title="AI Biomarker Discovery Platform",
    page_icon="🧬",
    layout="wide"
)


st.title("🧬 AI Biomarker Discovery Platform")

st.markdown(
    """
    ## Welcome

    This platform uses Machine Learning and Explainable AI
    to identify potential biomarkers from gene expression datasets.

    ### Pipeline

    Dataset Upload
    ↓
    Preprocessing
    ↓
    Exploration
    ↓
    Feature Selection
    ↓
    Machine Learning
    ↓
    SHAP Explainability
    ↓
    Biomarker Discovery
    ↓
    Report Generation

    """
)


st.info(
    "Navigate using the pages on the left sidebar."
)
