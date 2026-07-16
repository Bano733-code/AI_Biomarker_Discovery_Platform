import streamlit as st

from utils.preprocessing import (
    remove_duplicate_genes,
    handle_missing_values,
    log_transform,
    scale_data
)


st.title("⚙️ Data Preprocessing")


if "dataset" not in st.session_state:

    st.warning(
        "Please upload a dataset first."
    )

    st.stop()



expression_df = st.session_state["expression_data"]

metadata_df = st.session_state["metadata"]


st.subheader(
    "Original Dataset"
)

st.dataframe(
    df.head()
)


processed_df = df.copy()



# -------------------------
# Duplicate Removal
# -------------------------

if st.checkbox(
    "Remove duplicate genes",
    value=True
):

    processed_df = remove_duplicate_genes(
        processed_df
    )


# -------------------------
# Missing Values
# -------------------------

if st.checkbox(
    "Handle missing values",
    value=True
):

    processed_df = handle_missing_values(
        processed_df
    )



# -------------------------
# Log Transformation
# -------------------------

if st.checkbox(
    "Apply Log2 Transformation"
):

    processed_df = log_transform(
        processed_df
    )



# -------------------------
# Scaling
# -------------------------

scaling_option = st.selectbox(
    "Select Scaling Method",
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



# -------------------------
# Preview
# -------------------------

st.subheader(
    "Processed Dataset"
)


st.dataframe(
    processed_df.head()
)



# -------------------------
# Save
# -------------------------

if st.button(
    "Save Processed Dataset"
):

    st.session_state["processed_data"] = processed_df


    st.success(
        "Processed dataset saved successfully!"
    )
