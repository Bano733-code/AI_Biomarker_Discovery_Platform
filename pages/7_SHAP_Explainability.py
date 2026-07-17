import streamlit as st

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

    st.warning(
        "Please train the ML model first."
    )

    st.stop()

# =====================================================
# CHECK DATA
# =====================================================

if "processed_data" not in st.session_state:

    st.warning(
        "Please preprocess the dataset first."
    )

    st.stop()

# =====================================================
# LOAD DATA
# =====================================================

expression_df = st.session_state["processed_data"]

model = st.session_state["trained_model"]

# =====================================================
# PREPARE FEATURE MATRIX
# =====================================================

gene_names = expression_df.iloc[:, 0]

expression = expression_df.iloc[:, 1:]

X = expression.T

X.columns = gene_names

X = X.apply(
    lambda col: col.astype(float)
)

# =====================================================
# DATASET INFO
# =====================================================

st.subheader("Dataset Used for SHAP")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Samples",
        X.shape[0]
    )

with col2:

    st.metric(
        "Genes",
        X.shape[1]
    )

# =====================================================
# RUN SHAP
# =====================================================

if st.button(
    "🚀 Generate SHAP Explanation",
    use_container_width=True
):

    with st.spinner("Calculating SHAP values..."):

        shap_values, explainer = calculate_shap_values(
            model,
            X
        )

        importance = get_feature_importance(
            X,
            shap_values
        )

        st.session_state["shap_values"] = shap_values
        st.session_state["shap_features"] = X
        st.session_state["shap_importance"] = importance

    st.success(
        "SHAP analysis completed successfully!"
    )

# =====================================================
# DISPLAY RESULTS
# =====================================================

if "shap_importance" in st.session_state:

    importance = st.session_state["shap_importance"]

    shap_values = st.session_state["shap_values"]

    X = st.session_state["shap_features"]

    # -------------------------------------------------

    st.subheader("🧬 Top Biomarkers")

    st.dataframe(
        importance.head(20),
        use_container_width=True
    )

    # -------------------------------------------------

    st.subheader("📊 Global Feature Importance")

    fig = shap_bar_plot(
        shap_values,
        X
    )

    st.pyplot(
        fig,
        clear_figure=True
    )

    # -------------------------------------------------

    st.subheader("📈 SHAP Summary Plot")

    fig = shap_summary_plot(
        shap_values,
        X
    )

    st.pyplot(
        fig,
        clear_figure=True
    )

    # -------------------------------------------------

    st.subheader("📋 Top 10 Important Biomarkers")

    st.dataframe(
        importance.head(10),
        use_container_width=True
    )

    csv = importance.to_csv(
        index=False
    )

    st.download_button(
        label="⬇ Download SHAP Importance",
        data=csv,
        file_name="shap_biomarkers.csv",
        mime="text/csv"
    )
