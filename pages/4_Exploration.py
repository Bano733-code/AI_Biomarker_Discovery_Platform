import streamlit as st

from utils.visualization import (
    dataset_statistics,
    perform_pca,
    create_pca_plot,
    correlation_heatmap,
    sample_clustering,
)

st.title("📊 Exploratory Data Analysis")

# ----------------------------
# Check session state
# ----------------------------

if "processed_data" not in st.session_state:
    st.warning("Please complete preprocessing first.")
    st.stop()

if "metadata" not in st.session_state:
    st.warning("Metadata not found.")
    st.stop()

expression_df = st.session_state["processed_data"]
metadata_df = st.session_state["metadata"]

# ----------------------------
# Dataset Statistics
# ----------------------------

st.header("Dataset Statistics")

stats = dataset_statistics(expression_df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Genes", stats["Number of Genes"])

with col2:
    st.metric("Samples", stats["Number of Samples"])

with col3:
    st.metric("Missing Values", stats["Missing Values"])

with col4:
    st.metric("Duplicates", stats["Duplicate Rows"])

# ----------------------------
# PCA
# ----------------------------

st.header("Principal Component Analysis (PCA)")

pca_df, variance = perform_pca(
    expression_df,
    metadata_df,
)

st.write("Explained Variance")

st.write(
    f"PC1: {variance[0]*100:.2f}%   |   PC2: {variance[1]*100:.2f}%"
)

fig = create_pca_plot(pca_df)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# ----------------------------
# Correlation Heatmap
# ----------------------------

st.header("Sample Correlation Heatmap")

heatmap = correlation_heatmap(expression_df)

st.pyplot(heatmap)

# ----------------------------
# Sample Clustering
# ----------------------------

st.header("Sample Clustering")

cluster = sample_clustering(expression_df)

st.plotly_chart(
    cluster,
    use_container_width=True,
)
