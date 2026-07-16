import streamlit as st

from utils.biomarker_ranking import (
    combine_biomarker_scores,
    get_top_biomarkers
)



st.title(
    "🧬 Biomarker Discovery Results"
)



# Check data availability


if "selected_biomarkers" not in st.session_state:

    st.warning(
        "Please run Feature Selection first."
    )

    st.stop()



if "shap_importance" not in st.session_state:

    st.warning(
        "Please generate SHAP results first."
    )

    st.stop()



feature_results = st.session_state[
    "selected_biomarkers"
]


shap_results = st.session_state[
    "shap_importance"
]



# Combine rankings


final_results = combine_biomarker_scores(
    feature_results,
    shap_results
)



st.session_state[
    "final_biomarkers"
] = final_results



st.success(
    "Biomarker ranking generated successfully!"
)



# --------------------------
# Top 10
# --------------------------


st.header(
    "🏆 Top 10 Biomarkers"
)


top10 = get_top_biomarkers(
    final_results,
    10
)


st.dataframe(
    top10
)



# --------------------------
# Top 20
# --------------------------


st.header(
    "Top 20 Biomarkers"
)


top20 = get_top_biomarkers(
    final_results,
    20
)


st.dataframe(
    top20
)



# --------------------------
# Complete Table
# --------------------------


st.header(
    "Complete Biomarker Ranking"
)


st.dataframe(
    final_results
)



# --------------------------
# Download
# --------------------------


csv = final_results.to_csv(
    index=False
)



st.download_button(

    label="Download Biomarker Results CSV",

    data=csv,

    file_name="biomarker_results.csv",

    mime="text/csv"

)
