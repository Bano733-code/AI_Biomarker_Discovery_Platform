import streamlit as st


st.title("🧬 About the Project")


st.write(
    """
    The AI Biomarker Discovery Platform is a machine learning
    based system designed to identify important biological
    features from gene expression datasets.
    """
)


st.subheader("Features")


features = [
    "Gene expression dataset analysis",
    "Data preprocessing",
    "Feature selection",
    "Machine learning classification",
    "Biomarker ranking",
    "SHAP explainability",
    "Biological interpretation",
    "Automated reports"
]


for feature in features:
    st.success(feature)
