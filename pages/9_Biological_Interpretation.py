```python
import os
import streamlit as st
import pandas as pd

from utils.biology import (
    get_gene_information,
    annotate_genes,
    pathway_enrichment,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.title("🧬 Biological Interpretation")

st.markdown(
    """
Use the highest-ranked candidate biomarkers to retrieve
gene-level biological information and perform pathway
enrichment analysis.
"""
)


# ============================================================
# CHECK BIOMARKERS
# ============================================================

if "final_biomarkers" not in st.session_state:

    st.warning(
        "⚠️ Please generate biomarker results first."
    )

    st.stop()


biomarkers = st.session_state["final_biomarkers"]


# ============================================================
# VALIDATE BIOMARKER DATA
# ============================================================

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
# SELECT TOP BIOMARKERS
# ============================================================

top_n = st.slider(
    "Number of biomarkers to interpret",
    min_value=5,
    max_value=min(20, len(biomarkers)),
    value=min(10, len(biomarkers)),
    step=1
)


top_genes = (
    biomarkers
    .head(top_n)["Gene"]
    .dropna()
    .astype(str)
    .str.strip()
    .tolist()
)


# Remove empty values and duplicates
top_genes = list(
    dict.fromkeys(
        gene for gene in top_genes
        if gene
    )
)


# ============================================================
# SELECTED BIOMARKERS
# ============================================================

st.subheader("🔬 Selected Biomarkers")

if not top_genes:

    st.warning(
        "No valid biomarker identifiers were found."
    )

    st.stop()


st.write(
    f"Using the top {len(top_genes)} biomarkers:"
)

st.dataframe(
    pd.DataFrame(
        {
            "Rank": range(1, len(top_genes) + 1),
            "Gene / Feature": top_genes
        }
    ),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# RESULTS DIRECTORY
# ============================================================

os.makedirs(
    "results",
    exist_ok=True
)


# ============================================================
# GENE INFORMATION
# ============================================================

st.divider()

st.subheader("🧬 Gene Information")

if st.button(
    "🔎 Get Gene Information",
    use_container_width=True
):

    with st.spinner(
        "Retrieving gene information..."
    ):

        try:

            annotations = annotate_genes(
                top_genes
            )

            if annotations is None or annotations.empty:

                st.warning(
                    "No gene information could be retrieved."
                )

            else:

                # Save annotations
                annotation_path = (
                    "results/gene_annotations.csv"
                )

                annotations.to_csv(
                    annotation_path,
                    index=False
                )

                # Store in session state
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
# DISPLAY GENE INFORMATION
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
            hide_index=True
        )

        # ----------------------------------------------------
        # Individual Gene Details
        # ----------------------------------------------------

        if "Gene" in annotations.columns:

            st.subheader(
                "🔬 Gene Details"
            )

            selected_gene = st.selectbox(
                "Select a biomarker",
                annotations["Gene"].astype(str).tolist()
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

                        st.metric(
                            "Gene Symbol",
                            str(
                                row.get(
                                    "Symbol",
                                    "Not available"
                                )
                            )
                        )

                    if "Name" in annotations.columns:

                        st.write("**Gene Name**")

                        st.write(
                            row.get(
                                "Name",
                                "Not available"
                            )
                        )

                with col2:

                    st.write(
                        "**Biological Summary**"
                    )

                    st.write(
                        row.get(
                            "Summary",
                            "No description available."
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
Identify biological processes and pathways that are
over-represented among the selected biomarkers.
"""
)


if st.button(
    "🚀 Run Pathway Enrichment",
    use_container_width=True
):

    with st.spinner(
        "Running pathway enrichment analysis..."
    ):

        try:

            pathways = pathway_enrichment(
                top_genes
            )

            if pathways is None or pathways.empty:

                st.warning(
                    """
                    No significantly enriched pathways were returned.

                    This can happen when:
                    - the selected features are probe IDs rather than gene symbols
                    - too few biomarkers were selected
                    - the genes do not have sufficient pathway annotations
                    - the enrichment service returned no significant results
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
                    index=False
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

    if pathways is not None and not pathways.empty:

        st.subheader(
            "📊 Enriched Biological Pathways"
        )

        st.dataframe(
            pathways,
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # Simple visualization
        # ----------------------------------------------------

        if "P-value" in pathways.columns:

            st.subheader(
                "📈 Pathway Significance"
            )

            plot_df = pathways.copy()

            plot_df["P-value"] = pd.to_numeric(
                plot_df["P-value"],
                errors="coerce"
            )

            plot_df = plot_df.dropna(
                subset=["P-value"]
            )

            if not plot_df.empty:

                plot_df = plot_df.head(15)

                plot_df["-log10(P-value)"] = (
                    -__import__("numpy").log10(
                        plot_df["P-value"]
                    )
                )

                st.bar_chart(
                    plot_df.set_index("Term")[
                        "-log10(P-value)"
                    ]
                )


# ============================================================
# DOWNLOAD RESULTS
# ============================================================

st.divider()

st.subheader(
    "📥 Download Biological Results"
)


if "gene_annotations" in st.session_state:

    annotations = st.session_state[
        "gene_annotations"
    ]

    if annotations is not None and not annotations.empty:

        st.download_button(
            label="Download Gene Annotations",
            data=annotations.to_csv(
                index=False
            ),
            file_name="gene_annotations.csv",
            mime="text/csv",
            use_container_width=True
        )


if "pathways" in st.session_state:

    pathways = st.session_state[
        "pathways"
    ]

    if pathways is not None and not pathways.empty:

        st.download_button(
            label="Download Pathway Enrichment",
            data=pathways.to_csv(
                index=False
            ),
            file_name="pathway_enrichment.csv",
            mime="text/csv",
            use_container_width=True
        )
```
