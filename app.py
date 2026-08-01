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

```text
        📥 Upload GEO Dataset
                │
                ▼
        🧹 Preprocessing
                │
                ▼
        📊 Exploratory Analysis
                │
                ▼
        🧬 Differential Expression
                │
                ▼
        🎯 Feature Selection
                │
                ▼
        🤖 Machine Learning
                │
                ▼
        🔍 SHAP Explainability
                │
                ▼
        🧪 Biomarker Discovery
                │
                ▼
        📄 Automated Report
""")


st.info(
    "Navigate using the pages on the left sidebar."
)
