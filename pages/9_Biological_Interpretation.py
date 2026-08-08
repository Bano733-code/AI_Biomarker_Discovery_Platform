import os

import numpy as np
import pandas as pd
import streamlit as st

from utils.biology import (
    annotate_genes,
    pathway_enrichment,
)


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🧬 Biological Interpretation")

st.markdown(
    """
Interpret the highest-ranked biomarkers using gene annotation
and pathway enrichment analysis.
"""
)


# ============================================================
# CHECK BIOMARKER RESULTS
# ============================================================

if "final_biomarkers" not in st.session_state:

    st.warning(
        "⚠️ Please generate biomarker results first."
    )

    st.stop()


biomarkers = st.session_state["final_biomarkers"]


if biomarkers is None or biomarkers.empty:

    st.error(
        "No biomarker results are available."
    )

    st.stop()


if "Gene" not in biomarkers.columns:

    st.error(
        "The biomarker results do not contain a 'Gene' column."
    )

    st.write(
        "Available columns:",
        list(biomarkers.columns)
    )

    st.stop()


# ============================================================
# SELECT NUMBER OF BIOMARKERS
# ============================================================

max_genes = min(20, len(biomarkers))

default_genes = min(10, max_genes)

top_n = st.slider(
    "Number of biomarkers to interpret",
    min_value=1,
    max_value=max_genes,
    value=default_genes,
    step=1,
)


# ============================================================
# GET TOP BIOMARKERS
# ============================================================

top_genes = (
    biomarkers
    .head(top_n)["Gene"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)


# Remove empty strings and duplicates
top_genes = list(
    dict.fromkeys(
        gene
        for gene in top_genes
        if gene
    )
)


if not top_genes:

    st.error(
        "No valid biomarker identifiers were found."
    )

    st.stop()


# ============================================================
# DISPLAY SELECTED BIOMARKERS
# ============================================================

st.subheader("🔬 Selected Biomarkers")

selected_df = pd.DataFrame(
    {
        "Rank": range(1, len(top_genes) + 1),
        "Gene / Feature": top_genes,
    }
)

st.dataframe(
    selected_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# RESULTS DIRECTORY
# ============================================================

os.makedirs(
    "results",
    exist_ok=True,
)


# ============================================================
# GENE ANNOTATION
# ============================================================

st.divider()

st.subheader("🧬 Gene Information")

if st.button(
    "🔎 Get Gene Information",
    use_container_width=True,
):

    with st.spinner(
        "Retrieving gene information..."
    ):

        try:

            annotations = annotate_genes(
                top_genes
            )

            if (
                annotations is None
                or annotations.empty
            ):

                st.warning(
                    "No gene information could be retrieved."
                )

                st.session_state[
                    "gene_annotations"
                ] = pd.DataFrame()

            else:

                annotation_path = (
                    "results/gene_annotations.csv"
                )

                annotations.to_csv(
                    annotation_path,
                    index=False,
                )

                st.session_state[
                    "gene_annotations"
                ] = annotations

                st.session_state[
                    "gene_annotation_file"
                ] = annotation_path

                st.success(
                    "✅ Gene information retrieved successfully."
                )

        except Exception as e:

            st.error(
                f"Gene annotation failed: {e}"
            )


# ============================================================
# DISPLAY ANNOTATIONS
# ============================================================

if "gene_annotations" in st.session_state:

    annotations = st.session_state[
        "gene_annotations"
    ]

    if (
        annotations is not None
        and not annotations.empty
    ):

        st.subheader(
            "📋 Functional Gene Annotation"
        )

        st.dataframe(
            annotations,
            use_container_width=True,
            hide_index=True,
        )


        # ====================================================
        # INDIVIDUAL GENE DETAILS
        # ====================================================

        if "Gene" in annotations.columns:

            st.subheader(
                "🔬 Gene Details"
            )

            available_genes = (
                annotations["Gene"]
                .astype(str)
                .tolist()
            )

            selected_gene = st.selectbox(
                "Select a biomarker",
                available_genes,
            )

            selected_rows = annotations[
                annotations["Gene"].astype(str)
                == selected_gene
            ]

            if not selected_rows.empty:

                row = selected_rows.iloc[0]

                col1, col2 = st.columns(2)

                with col1:

                    if "Symbol" in annotations.columns:

                        st.write(
                            "**Gene Symbol**"
                        )

                        st.write(
                            str(
                                row.get(
                                    "Symbol",
                                    "Not available",
                                )
                            )
                        )


                    if "Name" in annotations.columns:

                        st.write(
                            "**Gene Name**"
                        )

                        st.write(
                            str(
                                row.get(
                                    "Name",
                                    "Not available",
                                )
                            )
                        )

                with col2:

                    if "Summary" in annotations.columns:

                        st.write(
                            "**Biological Summary**"
                        )

                        st.write(
                            str(
                                row.get(
                                    "Summary",
                                    "No description available.",
                                )
                            )
                        )


# ============================================================
# PATHWAY ENRICHMENT
# ============================================================

st.divider()

st.subheader(
    "🌿 Pathway Enrichment"
)

st.markdown(
    """
Identify biological pathways and functional terms
associated with the selected biomarkers.
"""
)


if st.button(
    "🚀 Run Pathway Enrichment",
    use_container_width=True,
):

    with st.spinner(
        "Running pathway enrichment analysis..."
    ):

        try:

            pathways = pathway_enrichment(
                top_genes
            )

            if (
                pathways is None
                or pathways.empty
            ):

                st.warning(
                    """
No enriched pathways were returned.

Possible reasons:

• The selected features may be probe IDs rather than gene symbols.
• Too few biomarkers were selected.
• The genes may have limited pathway annotations.
• The enrichment service may have returned no significant results.
"""
                )

                st.session_state[
                    "pathways"
                ] = pd.DataFrame()

            else:

                pathway_path = (
                    "results/pathway_enrichment.csv"
                )

                pathways.to_csv(
                    pathway_path,
                    index=False,
                )

                st.session_state[
                    "pathways"
                ] = pathways

                st.session_state[
                    "pathway_file"
                ] = pathway_path

                st.success(
                    "✅ Pathway enrichment completed."
                )

        except Exception as e:

            st.error(
                f"Pathway enrichment failed: {e}"
            )


# ============================================================
# DISPLAY PATHWAYS
# ============================================================

if "pathways" in st.session_state:

    pathways = st.session_state[
        "pathways"
    ]

    if (
        pathways is not None
        and not pathways.empty
    ):

        st.subheader(
            "📊 Enriched Biological Pathways"
        )

        st.dataframe(
            pathways,
            use_container_width=True,
            hide_index=True,
        )


        # ====================================================
        # PATHWAY SIGNIFICANCE
        # ====================================================

        if "P-value" in pathways.columns:

            st.subheader(
                "📈 Pathway Significance"
            )

            plot_df = pathways.copy()

            plot_df["P-value"] = pd.to_numeric(
                plot_df["P-value"],
                errors="coerce",
            )

            plot_df = plot_df.dropna(
                subset=["P-value"]
            )

            # Remove zero/negative values
            plot_df = plot_df[
                plot_df["P-value"] > 0
            ]

            if not plot_df.empty:

                plot_df = plot_df.head(15)

                plot_df["-log10(P-value)"] = (
                    -np.log10(
                        plot_df["P-value"]
                    )
                )

                chart_df = plot_df[
                    ["Term", "-log10(P-value)"]
                ].set_index("Term")

                st.bar_chart(
                    chart_df
                )


# ============================================================
# DOWNLOAD RESULTS
# ============================================================

st.divider()

st.subheader(
    "📥 Download Results"
)


if "gene_annotations" in st.session_state:

    annotations = st.session_state[
        "gene_annotations"
    ]

    if (
        annotations is not None
        and not annotations.empty
    ):

        st.download_button(
            label="Download Gene Annotations",
            data=annotations.to_csv(
                index=False
            ),
            file_name="gene_annotations.csv",
            mime="text/csv",
            use_container_width=True,
        )


if "pathways" in st.session_state:

    pathways = st.session_state[
        "pathways"
    ]

    if (
        pathways is not None
        and not pathways.empty
    ):

        st.download_button(
            label="Download Pathway Enrichment",
            data=pathways.to_csv(
                index=False
            ),
            file_name="pathway_enrichment.csv",
            mime="text/csv",
            use_container_width=True,
        )
