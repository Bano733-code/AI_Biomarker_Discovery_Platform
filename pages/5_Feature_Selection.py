import streamlit as st
import os
from utils.feature_selection import (
    prepare_features,
    anova_selection,
    mutual_information_selection,
    random_forest_selection,
    combine_rankings
)

st.title("🧬 Biomarker Feature Selection")

# ---------------------------------
# Check Session State
# ---------------------------------

if "processed_data" not in st.session_state:

    st.warning("Please complete preprocessing first.")

    st.stop()

if "metadata" not in st.session_state:

    st.warning("Metadata not found.")

    st.stop()

expression_df = st.session_state["processed_data"]
metadata_df = st.session_state["metadata"]

# ---------------------------------
# Prepare Features
# ---------------------------------

X, y = prepare_features(
    expression_df,
    metadata_df
)

st.write(f"Samples: {X.shape[0]}")
st.write(f"Genes: {X.shape[1]}")

st.subheader("Feature Selection Methods")

if st.button("Run Feature Selection"):

    anova = anova_selection(X, y)

    mi = mutual_information_selection(X, y)

    rf = random_forest_selection(X, y)

    final = combine_rankings(
        anova,
        mi,
        rf
    )
# Save in session
    st.session_state["selected_biomarkers"] = final
    
    # Create results folder
    os.makedirs("results", exist_ok=True)
    
    # Save biomarkers
    final.to_csv(
        "results/selected_biomarkers.csv",
        index=False
    )
    
    # Save path for report generation
    st.session_state["biomarker_file"] = (
        "results/selected_biomarkers.csv"
    )
    st.success("Feature selection completed!")

    st.subheader("Top Ranked Biomarkers")

    st.dataframe(
        final.head(20)
    )
    st.success("Biomarker table saved successfully.")
    
    st.download_button(
        label="📥 Download Biomarker Ranking",
        data=final.to_csv(index=False),
        file_name="Selected_Biomarkers.csv",
        mime="text/csv"
    )
