import os
import streamlit as st

from utils.data_loader import (
    load_expression_data,
    load_metadata,
    validate_expression_data,
    validate_metadata,
)

from utils.geo_downloader import load_geo_dataset


# ============================================================
# PAGE CONFIG
# ============================================================

st.title("📂 Dataset Upload")

st.markdown(
    """
Upload a **Gene Expression Matrix** together with its
**Sample Metadata**, or automatically download a dataset
from **NCBI GEO** using a GEO accession such as `GSE113994`.
"""
)


# ============================================================
# DATASET SOURCE
# ============================================================

option = st.radio(
    "Choose Dataset Source",
    [
        "📥 Download GEO Dataset",
        "🧪 Use Example Dataset",
        "📂 Upload Your Own Dataset",
    ],
)


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "expression_data" not in st.session_state:
    st.session_state["expression_data"] = None

if "metadata" not in st.session_state:
    st.session_state["metadata"] = None

if "dataset_report" not in st.session_state:
    st.session_state["dataset_report"] = None

if "dataset_accession" not in st.session_state:
    st.session_state["dataset_accession"] = None


expression_df = None
metadata_df = None
report = None


# ============================================================
# 1. DOWNLOAD GEO DATASET
# ============================================================

if option == "📥 Download GEO Dataset":

    st.subheader("🌐 Download Dataset from GEO")

    accession = st.text_input(
        "Enter GEO Accession",
        placeholder="Example: GSE113994",
        help="Enter a GEO Series accession such as GSE113994.",
    ).strip().upper()

    if st.button(
        "⬇️ Download Dataset",
        type="primary",
        use_container_width=True,
    ):

        if not accession:

            st.warning("Please enter a GEO accession.")

        elif not accession.startswith("GSE"):

            st.error(
                "Please enter a GEO Series accession beginning with GSE "
                "(for example: GSE113994)."
            )

        else:

            with st.spinner(
                f"Downloading and processing {accession}..."
            ):

                try:

                    (
                        expression_df,
                        metadata_df,
                        report,
                    ) = load_geo_dataset(accession)

                    # ----------------------------------------
                    # Save to session state
                    # ----------------------------------------

                    st.session_state["expression_data"] = expression_df

                    st.session_state["metadata"] = metadata_df

                    st.session_state["dataset_report"] = report

                    st.session_state["dataset_accession"] = accession

                    st.success(
                        f"✅ {accession} downloaded and processed successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"❌ Failed to load {accession}: {str(e)}"
                    )

    # --------------------------------------------------------
    # Load previously downloaded GEO dataset
    # --------------------------------------------------------

    if (
        st.session_state.get("dataset_accession")
        and st.session_state.get("expression_data") is not None
        and st.session_state.get("metadata") is not None
    ):

        expression_df = st.session_state["expression_data"]

        metadata_df = st.session_state["metadata"]

        report = st.session_state["dataset_report"]


# ============================================================
# 2. EXAMPLE DATASET
# ============================================================

elif option == "🧪 Use Example Dataset":

    st.subheader("🧪 Example Dataset")

    expression_path = "data/example_expression.csv"

    metadata_path = "data/sample_metadata.csv"

    if (
        os.path.exists(expression_path)
        and os.path.exists(metadata_path)
    ):

        try:

            expression_df = load_expression_data(
                expression_path
            )

            metadata_df = load_metadata(
                metadata_path
            )

            st.session_state["expression_data"] = expression_df

            st.session_state["metadata"] = metadata_df

            st.session_state["dataset_report"] = None

            st.session_state["dataset_accession"] = None

            st.success(
                "✅ Example dataset loaded successfully."
            )

        except Exception as e:

            st.error(
                f"❌ Failed to load example dataset: {str(e)}"
            )

    else:

        st.error(
            "❌ Example dataset files were not found."
        )


# ============================================================
# 3. UPLOAD USER DATASET
# ============================================================

elif option == "📂 Upload Your Own Dataset":

    st.subheader("📂 Upload Your Dataset")

    expression_file = st.file_uploader(
        "Upload Expression Matrix (.csv)",
        type=["csv"],
        help=(
            "CSV should contain one Gene column followed "
            "by sample expression columns."
        ),
    )

    metadata_file = st.file_uploader(
        "Upload Sample Metadata (.csv)",
        type=["csv"],
        help=(
            "CSV should contain Sample and Group columns."
        ),
    )

    if (
        expression_file is not None
        and metadata_file is not None
    ):

        try:

            expression_df = load_expression_data(
                expression_file
            )

            metadata_df = load_metadata(
                metadata_file
            )

            st.session_state["expression_data"] = expression_df

            st.session_state["metadata"] = metadata_df

            st.session_state["dataset_report"] = None

            st.session_state["dataset_accession"] = None

            st.success(
                "✅ Dataset uploaded successfully."
            )

        except Exception as e:

            st.error(
                f"❌ Dataset loading failed: {str(e)}"
            )

    elif (
        expression_file is not None
        or metadata_file is not None
    ):

        st.warning(
            "⚠️ Please upload BOTH the expression matrix "
            "and sample metadata."
        )


# ============================================================
# LOAD DATA FROM SESSION STATE
# ============================================================

if (
    expression_df is None
    and st.session_state.get("expression_data") is not None
):

    expression_df = st.session_state["expression_data"]


if (
    metadata_df is None
    and st.session_state.get("metadata") is not None
):

    metadata_df = st.session_state["metadata"]


if (
    report is None
    and st.session_state.get("dataset_report") is not None
):

    report = st.session_state["dataset_report"]


# ============================================================
# DATASET DISPLAY
# ============================================================

if expression_df is not None and metadata_df is not None:

    st.divider()

    # ========================================================
    # DATASET TITLE
    # ========================================================

    accession = st.session_state.get(
        "dataset_accession"
    )

    if accession:

        st.header(
            f"🧬 Dataset: {accession}"
        )

    else:

        st.header(
            "🧬 Dataset Summary"
        )


    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if "Gene" not in expression_df.columns:

        st.error(
            "❌ Expression matrix must contain a 'Gene' column."
        )

        st.stop()


    if "Sample" not in metadata_df.columns:

        st.error(
            "❌ Metadata must contain a 'Sample' column."
        )

        st.stop()


    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    n_genes = expression_df.shape[0]

    n_samples = expression_df.shape[1] - 1

    n_metadata_samples = metadata_df.shape[0]


    if "Group" in metadata_df.columns:

        n_groups = metadata_df["Group"].nunique()

    else:

        n_groups = 0


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "🧬 Genes",
            n_genes,
        )


    with col2:

        st.metric(
            "🧪 Expression Samples",
            n_samples,
        )


    with col3:

        st.metric(
            "📋 Metadata Samples",
            n_metadata_samples,
        )


    with col4:

        st.metric(
            "🏷️ Groups",
            n_groups,
        )


    # ========================================================
    # GEO VALIDATION REPORT
    # ========================================================

    if (
        accession
        and report is not None
    ):

        st.header(
            "✅ GEO Dataset Validation"
        )

        # Show the important validation information
        # instead of hiding it.

        validation_status = report.get(
            "is_valid",
            False,
        )

        if validation_status:

            st.success(
                "✅ Dataset validation passed."
            )

        else:

            st.warning(
                "⚠️ Dataset loaded, but validation found "
                "some issues. Review the report below."
            )

        with st.expander(
            "🔍 View Full GEO Validation Report"
        ):

            st.json(report)


    # ========================================================
    # EXPRESSION MATRIX PREVIEW
    # ========================================================

    with st.expander(
        "🧬 Expression Matrix Preview",
        expanded=True,
    ):

        st.dataframe(
            expression_df.head(10),
            use_container_width=True,
        )


    # ========================================================
    # METADATA PREVIEW
    # ========================================================

    with st.expander(
        "📋 Sample Metadata",
        expanded=True,
    ):

        st.dataframe(
            metadata_df.head(20),
            use_container_width=True,
        )


    # ========================================================
    # GROUP DISTRIBUTION
    # ========================================================

    if "Group" in metadata_df.columns:

        st.header(
            "🏷️ Sample Groups"
        )

        group_counts = (
            metadata_df["Group"]
            .value_counts()
            .rename_axis("Group")
            .reset_index(name="Samples")
        )

        st.dataframe(
            group_counts,
            use_container_width=True,
            hide_index=True,
        )


    # ========================================================
    # LOCAL DATASET VALIDATION
    # ========================================================

    st.header(
        "🔎 Dataset Validation"
    )

    # GEO datasets already have a detailed validation report
    # from geo_downloader.py.

    if accession and report is not None:

        st.info(
            "GEO validation was performed automatically during "
            "dataset download."
        )

    else:

        try:

            expression_report = validate_expression_data(
                expression_df
            )

            metadata_report = validate_metadata(
                metadata_df,
                expression_df
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "🧬 Expression Validation"
                )

                st.json(
                    expression_report
                )

            with col2:

                st.subheader(
                    "📋 Metadata Validation"
                )

                st.json(
                    metadata_report
                )

        except Exception as e:

            st.error(
                f"Validation failed: {str(e)}"
            )


    # ========================================================
    # SAVE DATASET
    # ========================================================

    st.divider()

    if st.button(
        "💾 Save Dataset",
        type="primary",
        use_container_width=True,
    ):

        st.session_state["expression_data"] = expression_df

        st.session_state["metadata"] = metadata_df

        st.success(
            "✅ Dataset saved successfully and is now "
            "available to the other analysis pages."
        )
