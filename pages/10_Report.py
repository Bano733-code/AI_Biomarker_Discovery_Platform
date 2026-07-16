import streamlit as st
from datetime import datetime

from utils.report import generate_report


st.title(
    "📄 Automated Research Report"
)


# =====================================================
# CHECK DATA
# =====================================================

if "processed_data" not in st.session_state:

    st.warning(
        "Processed dataset not found. Please complete preprocessing first."
    )

    st.stop()



if "selected_biomarkers" not in st.session_state:

    st.warning(
        "Biomarker results not found. Please complete feature selection first."
    )

    st.stop()



expression_df = st.session_state[
    "processed_data"
]


biomarkers = st.session_state[
    "selected_biomarkers"
]


# =====================================================
# OPTIONAL MODEL RESULTS
# =====================================================

model_metrics = None

if "model_metrics" in st.session_state:

    model_metrics = st.session_state[
        "model_metrics"
    ]



shap_results = None

if "shap_importance" in st.session_state:

    shap_results = st.session_state[
        "shap_importance"
    ]



# =====================================================
# REPORT PREVIEW
# =====================================================

st.header(
    "🔬 Biomarker Discovery Summary"
)



st.write(
    "Generated:",
    datetime.now().strftime("%Y-%m-%d")
)



st.subheader(
    "Dataset Information"
)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Genes",
        expression_df.shape[0]
    )


with col2:

    st.metric(
        "Samples",
        expression_df.shape[1]-1
    )



# =====================================================
# BIOMARKERS
# =====================================================

st.subheader(
    "🧬 Top Biomarkers"
)


st.dataframe(
    biomarkers.head(20)
)



# =====================================================
# SHAP RESULTS
# =====================================================

if shap_results is not None:


    st.subheader(
        "Explainable AI Results"
    )


    st.dataframe(
        shap_results.head(10)
    )



# =====================================================
# MODEL RESULTS
# =====================================================

if model_metrics is not None:


    st.subheader(
        "Machine Learning Performance"
    )


    col1, col2, col3 = st.columns(3)


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



# =====================================================
# DOWNLOAD REPORT
# =====================================================

if st.button(
    "Generate Report"
):


    report_text = generate_report(

        expression_df,

        biomarkers,

        model_metrics,

        shap_results

    )


    st.download_button(

        label="📥 Download Research Report",

        data=report_text,

        file_name="AI_Biomarker_Report.txt",

        mime="text/plain"

    )
