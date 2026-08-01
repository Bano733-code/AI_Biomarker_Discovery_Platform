import streamlit as st
import os
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
# Create results folder
os.makedirs("results", exist_ok=True)

# Save complete biomarker ranking
final_results.to_csv(
    "results/final_biomarker_ranking.csv",
    index=False
)

# Save for report generation
st.session_state["final_biomarkers"] = final_results
st.session_state["final_biomarker_file"] = (
    "results/final_biomarker_ranking.csv"
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

top10.to_csv(
    "results/top10_biomarkers.csv",
    index=False
)

st.session_state["top10_file"] = (
    "results/top10_biomarkers.csv"
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

top20.to_csv(
    "results/top20_biomarkers.csv",
    index=False
)

st.session_state["top20_file"] = (
    "results/top20_biomarkers.csv"
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
