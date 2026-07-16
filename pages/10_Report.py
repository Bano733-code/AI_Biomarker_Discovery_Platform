import streamlit as st
import os


from utils.report import generate_report



st.title(
    "📄 Automated Research Report"
)



required = [

    "final_biomarkers",

    "model_metrics",

    "gene_annotations",

    "pathways"

]



for item in required:

    if item not in st.session_state:

        st.warning(
            f"Missing: {item}"
        )

        st.stop()



# Dataset Information


df = st.session_state[
    "processed_dataset"
]


dataset_info = {

    "Genes":
        df.shape[0],

    "Samples":
        df.shape[1]-2,

    "Pipeline":
        "AI Biomarker Discovery"

}



metrics = st.session_state[
    "model_metrics"
]


biomarkers = st.session_state[
    "final_biomarkers"
]


annotations = st.session_state[
    "gene_annotations"
]


pathways = st.session_state[
    "pathways"
]



if st.button(
    "Generate PDF Report"
):


    os.makedirs(
        "reports/generated_reports",
        exist_ok=True
    )


    filename = (
        "reports/generated_reports/"
        "AI_Biomarker_Report.pdf"
    )


    generate_report(

        filename,

        dataset_info,

        metrics,

        biomarkers,

        annotations,

        pathways

    )


    st.session_state[
        "report_file"
    ] = filename



    st.success(
        "Report generated successfully!"
    )



if "report_file" in st.session_state:


    with open(
        st.session_state["report_file"],
        "rb"
    ) as file:


        st.download_button(

            label="⬇️ Download PDF Report",

            data=file,

            file_name="AI_Biomarker_Report.pdf",

            mime="application/pdf"

        )
