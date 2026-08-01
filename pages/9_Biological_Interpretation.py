import streamlit as st

import os
from utils.biology import (
    annotate_genes,
    pathway_enrichment
)



st.title(
    "🧬 Biological Interpretation"
)



if "final_biomarkers" not in st.session_state:


    st.warning(
        "Please generate biomarker results first."
    )


    st.stop()



biomarkers = st.session_state[
    "final_biomarkers"
]



# Select top genes


top_genes = biomarkers.head(
    10
)["Gene"].tolist()



st.subheader(
    "Selected Biomarkers"
)


st.write(
    top_genes
)



# -----------------------------
# Gene Information
# -----------------------------


if st.button(
    "Get Gene Information"
):


    annotations = annotate_genes(
        top_genes
    )

    # Create results folder
    os.makedirs("results", exist_ok=True)
    
    # Save gene annotations
    annotations.to_csv(
        "results/gene_annotations.csv",
        index=False
    )
    st.session_state[
        "gene_annotations"
    ] = annotations
    # Save path for report generation
    st.session_state[
        "gene_annotation_file"
    ] = "results/gene_annotations.csv"


if "gene_annotations" in st.session_state:


    st.subheader(
        "Gene Functions"
    )


    st.dataframe(
        st.session_state[
            "gene_annotations"
        ]
    )



# -----------------------------
# Pathway Analysis
# -----------------------------
if st.button(
    "Run Pathway Enrichment"
):
    pathways = pathway_enrichment(
    top_genes
    )

    st.session_state["pathways"] = pathways

    # Create results folder
    os.makedirs("results", exist_ok=True)
    
    # Save pathway enrichment
    pathways.to_csv(
        "results/pathway_enrichment.csv",
        index=False
    )
    # Save path for report generation
    st.session_state[
        "pathway_file"
    ] = "results/pathway_enrichment.csv"

if "pathways" in st.session_state:


    st.subheader(
        "GO / KEGG Pathway Enrichment"
    )


    st.dataframe(
        st.session_state[
            "pathways"
        ]
    )
