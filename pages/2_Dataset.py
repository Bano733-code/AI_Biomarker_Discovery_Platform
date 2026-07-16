import streamlit as st
import os

from utils.data_loader import (
    load_dataset,
    validate_dataset
)


st.title("📂 Dataset Upload")


st.write(
    """
    Upload a gene expression dataset or use
    the provided example dataset.
    """
)


# ----------------------------
# Dataset Selection
# ----------------------------

option = st.radio(
    "Choose Dataset Source",
    [
        "Upload CSV",
        "Use Example Dataset"
    ]
)


df = None


# ----------------------------
# Upload CSV
# ----------------------------

if option == "Upload CSV":

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )


    if uploaded_file:

        df = load_dataset(uploaded_file)



# ----------------------------
# Example Dataset
# ----------------------------

else:

    example_path = (
        "data/example_dataset.csv"
    )

    if os.path.exists(example_path):

        df = load_dataset(
            example_path
        )

        st.success(
            "Example dataset loaded"
        )

    else:

        st.error(
            "Example dataset not found"
        )


# ----------------------------
# Display Dataset
# ----------------------------

if df is not None:


    st.subheader(
        "Dataset Preview"
    )


    st.dataframe(
        df.head(10)
    )


    st.subheader(
        "Dataset Information"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Genes",
            df.shape[0]
        )


    with col2:

        st.metric(
            "Samples",
            df.shape[1]-1
        )


    st.subheader(
        "Validation Report"
    )


    report = validate_dataset(df)


    st.json(report)


    # Save for next pages

    st.session_state[
        "dataset"
    ] = df


    st.success(
        "Dataset saved successfully"
    )
