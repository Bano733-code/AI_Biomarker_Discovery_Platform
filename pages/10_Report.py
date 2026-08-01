import os
import streamlit as st
import pandas as pd

from utils.report import generate_report


st.title(
    "📄 Automated Research Report"
)


# =====================================================
# CHECK REQUIRED DATA
# =====================================================


if "processed_data" not in st.session_state:

    st.warning(
        "Processed dataset not found. Please complete preprocessing first."
    )

    st.stop()



expression_df = st.session_state[
    "processed_data"
]



# =====================================================
# LOAD AVAILABLE RESULTS
# =====================================================


# Dataset summary

dataset_info = {

    "Total Genes":
        expression_df.shape[0],

    "Total Samples":
        expression_df.shape[1] - 1

}



# ML Results

model_metrics = st.session_state.get(
    "model_metrics",
    None
)



# Biomarkers

final_biomarkers = st.session_state.get(
    "final_biomarkers",
    None
)



# SHAP

shap_results = st.session_state.get(
    "shap_importance",
    None
)



# =====================================================
# REPORT PREVIEW
# =====================================================


st.header(
    "🔬 AI Biomarker Discovery Summary"
)



col1, col2 = st.columns(2)



with col1:

    st.metric(
        "Genes",
        dataset_info["Total Genes"]
    )



with col2:

    st.metric(
        "Samples",
        dataset_info["Total Samples"]
    )



# =====================================================
# SHOW AVAILABLE RESULTS
# =====================================================


if final_biomarkers is not None:

    st.subheader(
        "🧬 Top Biomarkers"
    )

    st.dataframe(
        final_biomarkers.head(10)
    )



if model_metrics is not None:

    st.subheader(
        "🤖 Machine Learning Performance"
    )


    col1,col2,col3 = st.columns(3)


    with col1:

        st.metric(
            "Accuracy",
            round(
                model_metrics["Accuracy"],
                3
            )
        )


    with col2:

        st.metric(
            "F1 Score",
            round(
                model_metrics["F1 Score"],
                3
            )
        )


    with col3:

        if model_metrics["ROC-AUC"]:

            st.metric(
                "ROC-AUC",
                round(
                    model_metrics["ROC-AUC"],
                    3
                )
            )



if shap_results is not None:


    st.subheader(
        "🔍 SHAP Explainability"
    )


    st.dataframe(
        shap_results.head(10)
    )



# =====================================================
# GENERATE PDF
# =====================================================


st.divider()


st.subheader(
    "Generate Complete Research Report"
)



if st.button(
    "📄 Create Research Report"
):


    os.makedirs(
        "reports",
        exist_ok=True
    )


    report_file = (
        "reports/"
        "AI_Biomarker_Discovery_Report.pdf"
    )



    # Paths of generated files


    qc_results = (
        "results/qc_results.csv"
        if os.path.exists(
            "results/qc_results.csv"
        )
        else None
    )


    pca_plot = (
        "results/pca_plot.png"
        if os.path.exists(
            "results/pca_plot.png"
        )
        else None
    )


    heatmap_plot = (
        "results/heatmap.png"
        if os.path.exists(
            "results/heatmap.png"
        )
        else None
    )


    clustering_plot = (
        "results/clustering.png"
        if os.path.exists(
            "results/clustering.png"
        )
        else None
    )


    deg_results = (
        "results/deg_results.csv"
        if os.path.exists(
            "results/deg_results.csv"
        )
        else None
    )


    feature_results = (
        "results/selected_biomarkers.csv"
        if os.path.exists(
            "results/selected_biomarkers.csv"
        )
        else None
    )


    classification_report = (
        "results/classification_report.csv"
        if os.path.exists(
            "results/classification_report.csv"
        )
        else None
    )


    confusion_matrix = (
        "results/confusion_matrix.csv"
        if os.path.exists(
            "results/confusion_matrix.csv"
        )
        else None
    )


    shap_summary_plot = (
        "results/shap_summary_plot.png"
        if os.path.exists(
            "results/shap_summary_plot.png"
        )
        else None
    )


    shap_bar_plot = (
        "results/shap_bar_plot.png"
        if os.path.exists(
            "results/shap_bar_plot.png"
        )
        else None
    )


    gene_annotations = (
        "results/gene_annotations.csv"
        if os.path.exists(
            "results/gene_annotations.csv"
        )
        else None
    )


    pathway_results = (
        "results/pathway_enrichment.csv"
        if os.path.exists(
            "results/pathway_enrichment.csv"
        )
        else None
    )



    generate_report(

        report_file,

        dataset_info,

        model_metrics,

        final_biomarkers,

        shap_results
    )



    st.success(
        "✅ Complete Research Report Generated!"
    )



    with open(
        report_file,
        "rb"
    ) as pdf:


        st.download_button(

            label="📥 Download PDF Report",

            data=pdf,

            file_name=
            "AI_Biomarker_Discovery_Report.pdf",

            mime=
            "application/pdf"

        )
