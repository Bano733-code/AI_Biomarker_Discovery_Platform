import os
import streamlit as st


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



if "selected_biomarkers" not in st.session_state:

    st.warning(
        "Biomarker results not found. Please complete feature selection first."
    )

    st.stop()



# =====================================================
# LOAD DATA
# =====================================================


expression_df = st.session_state[
    "processed_data"
]


biomarkers = st.session_state[
    "selected_biomarkers"
]



# Optional ML results

if "model_metrics" in st.session_state:

    model_metrics = st.session_state[
        "model_metrics"
    ]

else:

    model_metrics = None



# Optional SHAP results

if "shap_importance" in st.session_state:

    shap_results = st.session_state[
        "shap_importance"
    ]

else:

    shap_results = None



# =====================================================
# REPORT PREVIEW
# =====================================================


st.header(
    "🔬 AI Biomarker Discovery Summary"
)



# Dataset information

dataset_info = {

    "Total Genes":
        expression_df.shape[0],

    "Total Samples":
        expression_df.shape[1] - 1

}



st.subheader(
    "Dataset Information"
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
# BIOMARKER RESULTS
# =====================================================


st.subheader(
    "🧬 Top Biomarkers"
)



st.dataframe(

    biomarkers.head(10)

)



# =====================================================
# ML RESULTS
# =====================================================


if model_metrics is not None:


    st.subheader(
        "🤖 Machine Learning Performance"
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


        if model_metrics["ROC-AUC"] is not None:

            st.metric(

                "ROC-AUC",

                round(
                    model_metrics["ROC-AUC"],
                    3
                )

            )



# =====================================================
# SHAP RESULTS
# =====================================================


if shap_results is not None:


    st.subheader(
        "🔍 SHAP Explainability"
    )


    st.dataframe(

        shap_results.head(10)

    )



# =====================================================
# GENERATE PDF REPORT
# =====================================================


st.divider()



st.subheader(
    "Generate PDF Report"
)



if st.button(
    "📄 Create Research Report"
):


    # create reports folder

    os.makedirs(
        "reports",
        exist_ok=True
    )


    report_file = (
        "reports/"
        "AI_Biomarker_Discovery_Report.pdf"
    )



    generate_report(

        report_file,

        dataset_info,

        model_metrics,

        biomarkers,

        shap_results

    )



    st.success(
        "Report generated successfully!"
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
