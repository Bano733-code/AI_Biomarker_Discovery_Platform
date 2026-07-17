import streamlit as st
import numpy as np

from utils.shap_analysis import (
    calculate_shap_values,
    get_feature_importance,
    shap_summary_plot,
    shap_bar_plot
)

st.title("🔍 SHAP Explainable AI")

# =====================================================
# CHECK MODEL
# =====================================================

if "trained_model" not in st.session_state:
    st.warning("Please train the ML model first.")
    st.stop()

# =====================================================
# CHECK DATA
# =====================================================

if "processed_data" not in st.session_state:
    st.warning("Processed dataset not found.")
    st.stop()

expression_df = st.session_state["processed_data"]
model = st.session_state["trained_model"]

# =====================================================
# PREPARE FEATURES
# =====================================================

gene_names = expression_df.iloc[:, 0]

expression = expression_df.iloc[:, 1:]

X = expression.T

X.columns = gene_names

st.subheader("Dataset Used For Explanation")

col1, col2 = st.columns(2)

with col1:
    st.metric("Samples", X.shape[0])

with col2:
    st.metric("Genes", X.shape[1])

# =====================================================
# RUN SHAP
# =====================================================

if st.button(
    "🚀 Generate SHAP Explanation",
    use_container_width=True
):

    shap_values, explainer = calculate_shap_values(
        model,
        X
    )

    # -----------------------------
    # DEBUG INFORMATION
    # -----------------------------

    st.write("Model Type:", type(model))

    if hasattr(shap_values, "values"):

        st.write(
            "SHAP values shape:",
            shap_values.values.shape
        )

    else:

        st.write(
            "SHAP values shape:",
            np.array(shap_values).shape
        )

    importance = get_feature_importance(
        X,
        shap_values
    )

    st.session_state["shap_importance"] = importance
    st.session_state["shap_values"] = shap_values
    st.session_state["shap_features"] = X

    st.success("SHAP analysis completed!")

# =====================================================
# DISPLAY RESULTS
# =====================================================

if "shap_importance" in st.session_state:

    importance = st.session_state["shap_importance"]

    shap_values = st.session_state["shap_values"]

    X = st.session_state["shap_features"]

    st.subheader("🧬 Top Biomarkers by SHAP")

    st.dataframe(importance.head(20))

    st.subheader("📊 SHAP Global Importance")

    fig = shap_bar_plot(
        shap_values,
        X
    )

    st.pyplot(fig)

    st.subheader("📈 SHAP Summary Plot")

    fig = shap_summary_plot(
        shap_values,
        X
    )

    st.pyplot(fig)
