import streamlit as st
import os
import pandas as pd
from utils.preprocessing import (
    remove_duplicate_genes,
    handle_missing_values,
    log_transform,
    scale_data
)

# =====================================================
# PAGE TITLE
# =====================================================

st.title("⚙️ Data Preprocessing")

# =====================================================
# CHECK DATASET
# =====================================================

if "expression_data" not in st.session_state:

    st.warning(
        "Please upload or load a dataset first."
    )

    st.stop()

expression_df = st.session_state["expression_data"]
metadata_df = st.session_state["metadata"]

# =====================================================
# ORIGINAL DATASET
# =====================================================

st.subheader("🧬 Original Expression Matrix")

st.dataframe(
    expression_df.head()
)

processed_df = expression_df.copy()

# =====================================================
# PREPROCESSING OPTIONS
# =====================================================

st.header("Preprocessing Options")

# -------------------------
# Remove Duplicate Genes
# -------------------------

remove_duplicates = st.checkbox(
    "Remove Duplicate Genes",
    value=True
)

if remove_duplicates:

    processed_df = remove_duplicate_genes(
        processed_df
    )

# -------------------------
# Handle Missing Values
# -------------------------

handle_missing = st.checkbox(
    "Handle Missing Values",
    value=True
)

if handle_missing:

    processed_df = handle_missing_values(
        processed_df
    )

# -------------------------
# Log2 Transformation
# -------------------------

apply_log = st.checkbox(
    "Apply Log2 Transformation"
)

if apply_log:

    processed_df = log_transform(
        processed_df
    )

# -------------------------
# Scaling
# -------------------------

scaling_option = st.selectbox(
    "Scaling Method",
    [
        "None",
        "Standard Scaling",
        "MinMax Scaling"
    ]
)

if scaling_option == "Standard Scaling":

    processed_df = scale_data(
        processed_df,
        "standard"
    )

elif scaling_option == "MinMax Scaling":

    processed_df = scale_data(
        processed_df,
        "minmax"
    )

# =====================================================
# PROCESSED DATASET
# =====================================================

st.divider()

st.subheader("✅ Processed Expression Matrix")

st.dataframe(
    processed_df.head()
)

# =====================================================
# DATASET SUMMARY
# =====================================================

st.subheader("📊 Dataset Summary")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Genes",
        processed_df.shape[0]
    )

with col2:

    st.metric(
        "Samples",
        processed_df.shape[1] - 1
    )

with col3:

    st.metric(
        "Groups",
        metadata_df["Group"].nunique()
    )

# =====================================================
# SAVE
# =====================================================

if st.button(
    "💾 Save Processed Dataset",
    use_container_width=True
):

    st.session_state["processed_data"] = processed_df

       # Create results folder
    os.makedirs("results", exist_ok=True)

    # Save processed dataset
    processed_df.to_csv(
        "results/processed_dataset.csv",
        index=False
    )

    # Create preprocessing summary
    summary = {
        "Metric": [
            "Total Genes",
            "Total Samples",
            "Groups",
            "Missing Values",
            "Duplicate Genes"
        ],
        "Value": [
            processed_df.shape[0],
            processed_df.shape[1]-1,
            metadata_df["Group"].nunique(),
            processed_df.isnull().sum().sum(),
            processed_df.duplicated().sum()
        ]
    }

    summary_df = pd.DataFrame(summary)

    summary_df.to_csv(
        "results/dataset_statistics.csv",
        index=False
    )

    # Save paths
    st.session_state["processed_dataset_file"] = "results/processed_dataset.csv"
    st.session_state["dataset_statistics_file"] = "results/dataset_statistics.csv"

    st.success(
        "✅ Processed dataset saved successfully."
    )
