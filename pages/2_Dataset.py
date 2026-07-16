import os
import streamlit as st

from utils.data_loader import (
    load_expression_data,
    load_metadata,
    validate_expression_data,
    validate_metadata,
)

st.title("📂 Dataset Upload")

st.markdown("""
Upload a **Gene Expression Matrix** together with its
**Sample Metadata**, or use the provided example dataset.
""")

# ======================================================
# DATASET SOURCE
# ======================================================

option = st.radio(
    "Choose Dataset Source",
    [
        "🧪 Use Example Dataset",
        "📤 Upload Your Own Dataset"
    ]
)

expression_df = None
metadata_df = None

# ======================================================
# EXAMPLE DATASET
# ======================================================

if option == "🧪 Use Example Dataset":

    expression_path = "data/example_expression.csv"
    metadata_path = "data/sample_metadata.csv"

    if os.path.exists(expression_path) and os.path.exists(metadata_path):

        expression_df = load_expression_data(expression_path)
        metadata_df = load_metadata(metadata_path)

        st.success("✅ Example dataset loaded successfully.")

    else:

        st.error("Example dataset files not found.")

# ======================================================
# USER DATASET
# ======================================================

else:

    expression_file = st.file_uploader(
        "Upload Expression Matrix (.csv)",
        type=["csv"]
    )

    metadata_file = st.file_uploader(
        "Upload Sample Metadata (.csv)",
        type=["csv"]
    )

    if expression_file is not None and metadata_file is not None:

        expression_df = load_expression_data(expression_file)
        metadata_df = load_metadata(metadata_file)

    elif expression_file is not None or metadata_file is not None:

        st.warning("Please upload BOTH Expression Matrix and Metadata.")

# ======================================================
# DISPLAY
# ======================================================

if expression_df is not None and metadata_df is not None:

    # ------------------------
    # Validate Metadata Format
    # ------------------------

    required_columns = ["Sample", "Group"]

    missing = [
        col
        for col in required_columns
        if col not in metadata_df.columns
    ]

    if missing:

        st.error(
            f"Metadata file is missing columns: {missing}"
        )

        st.stop()

    # ------------------------
    # Summary
    # ------------------------

    st.divider()

    st.header("📊 Dataset Summary")

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
            "Classes",
            metadata_df["Group"].nunique()
        )

    # ------------------------
    # Preview
    # ------------------------

    with st.expander("🧬 Expression Matrix Preview"):

        st.dataframe(
            expression_df.head()
        )

    with st.expander("📋 Metadata Preview"):

        st.dataframe(
            metadata_df
        )

    # ------------------------
    # Validation
    # ------------------------

    st.header("✅ Validation Report")

    expression_report = validate_expression_data(
        expression_df
    )

    metadata_report = validate_metadata(
        metadata_df,
        expression_df
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Expression Matrix")

        st.json(expression_report)

    with col2:

        st.subheader("Metadata")

        st.json(metadata_report)

    # ------------------------
    # Save Dataset
    # ------------------------

    if st.button(
        "💾 Save Dataset",
        use_container_width=True
    ):

        st.session_state["expression_data"] = expression_df
        st.session_state["metadata"] = metadata_df

        st.success(
            "Dataset saved successfully."
        )
