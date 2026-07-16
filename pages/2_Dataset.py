import os
import streamlit as st

from utils.data_loader import (
    load_expression_data,
    load_metadata,
    validate_expression_data,
    validate_metadata,
)

st.title("📂 Dataset Upload")

st.write(
    """
    Upload a gene expression matrix and its corresponding
    sample metadata, or use the provided example dataset.
    """
)

# ======================================================
# DATASET SOURCE
# ======================================================

option = st.radio(
    "Choose Dataset Source",
    [
        "Use Example Dataset",
        "Upload Your Own Dataset"
    ]
)

expression_df = None
metadata_df = None

# ======================================================
# EXAMPLE DATASET
# ======================================================

if option == "Use Example Dataset":

    expression_path = "data/example_expression.csv"
    metadata_path = "data/sample_metadata.csv"

    if os.path.exists(expression_path) and os.path.exists(metadata_path):

        expression_df = load_expression_data(expression_path)
        metadata_df = load_metadata(metadata_path)

        st.success("Example dataset loaded successfully.")

    else:

        st.error("Example dataset files not found.")

# ======================================================
# USER UPLOAD
# ======================================================

else:

    st.subheader("🧬 Upload Expression Matrix")

    expression_file = st.file_uploader(
        "Upload Expression Matrix (.csv)",
        type=["csv"],
        key="expression_file"
    )

    st.subheader("📋 Upload Sample Metadata")

    metadata_file = st.file_uploader(
        "Upload Sample Metadata (.csv)",
        type=["csv"],
        key="metadata_file"
    )

    if expression_file is not None and metadata_file is not None:

        expression_df = load_expression_data(expression_file)
        metadata_df = load_metadata(metadata_file)

# ======================================================
# DISPLAY
# ======================================================

if expression_df is not None and metadata_df is not None:

    st.divider()

    st.header("🧬 Expression Matrix")

    st.dataframe(expression_df.head())

    st.header("📋 Sample Metadata")

    st.dataframe(metadata_df)

    # ==================================================
    # DATASET INFORMATION
    # ==================================================

    st.header("📊 Dataset Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Genes",
            expression_df.shape[0]
        )

    with col2:
        st.metric(
            "Samples",
            expression_df.shape[1] - 1
        )

    with col3:
        st.metric(
            "Groups",
            metadata_df["Group"].nunique()
        )

    # ==================================================
    # VALIDATION
    # ==================================================

    st.header("✅ Validation Report")

    expression_report = validate_expression_data(
        expression_df
    )

    metadata_report = validate_metadata(
        metadata_df,
        expression_df
    )

    st.subheader("Expression Matrix")

    st.json(expression_report)

    st.subheader("Sample Metadata")

    st.json(metadata_report)

    # ==================================================
    # SAVE
    # ==================================================

    if st.button("💾 Save Dataset"):

        st.session_state["expression_data"] = expression_df

        st.session_state["metadata"] = metadata_df

        st.success(
            "Dataset saved successfully."
        )
