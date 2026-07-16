import streamlit as st


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


    st.session_state[
        "gene_annotations"
    ] = annotations



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


    st.session_state[
        "pathways"
    ] = pathways




if "pathways" in st.session_state:


    st.subheader(
        "GO / KEGG Pathway Enrichment"
    )


    st.dataframe(
        st.session_state[
            "pathways"
        ]
    )
