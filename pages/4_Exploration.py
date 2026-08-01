import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils.visualization import (
    dataset_statistics,
    perform_pca,
    create_pca_plot,
    correlation_heatmap,
    sample_clustering,
)

st.title("📊 Exploratory Data Analysis")

# =====================================================
# CHECK SESSION STATE
# =====================================================

if "processed_data" not in st.session_state:
    st.warning("Please complete preprocessing first.")
    st.stop()

if "metadata" not in st.session_state:
    st.warning("Metadata not found.")
    st.stop()

expression_df = st.session_state["processed_data"]
metadata_df = st.session_state["metadata"]

# =====================================================
# CREATE RESULTS DIRECTORY
# =====================================================

os.makedirs("results", exist_ok=True)

# =====================================================
# DATASET STATISTICS
# =====================================================

st.header("📋 Dataset Statistics")

stats = dataset_statistics(expression_df)

# Save statistics for PDF report
stats_df = pd.DataFrame([stats])
stats_df.to_csv(
    "results/dataset_statistics.csv",
    index=False
)

st.session_state["dataset_statistics"] = stats

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Genes",
        stats["Number of Genes"]
    )

with col2:
    st.metric(
        "Samples",
        stats["Number of Samples"]
    )

with col3:
    st.metric(
        "Missing Values",
        stats["Missing Values"]
    )

with col4:
    st.metric(
        "Duplicates",
        stats["Duplicate Rows"]
    )

# =====================================================
# PCA
# =====================================================

st.header("📈 Principal Component Analysis (PCA)")

pca_df, variance = perform_pca(
    expression_df,
    metadata_df
)

st.write(
    f"**Explained Variance:** "
    f"PC1 = {variance[0]*100:.2f}% | "
    f"PC2 = {variance[1]*100:.2f}%"
)

# Interactive Plotly figure
fig = create_pca_plot(pca_df)

st.plotly_chart(
    fig,
    use_container_width=True
)

# Save in session
st.session_state["pca_results"] = pca_df
st.session_state["pca_variance"] = variance
st.session_state["pca_plot"] = fig

# Save PCA as PNG using Matplotlib (for PDF)
plt.figure(figsize=(7, 6))

for group in pca_df["Group"].unique():

    temp = pca_df[
        pca_df["Group"] == group
    ]

    plt.scatter(
        temp["PC1"],
        temp["PC2"],
        s=80,
        label=group
    )

plt.xlabel("PC1")
plt.ylabel("PC2")
plt.title("Principal Component Analysis")
plt.legend()

plt.tight_layout()

plt.savefig(
    "results/pca_plot.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# =====================================================
# CORRELATION HEATMAP
# =====================================================

st.header("🔥 Sample Correlation Heatmap")

heatmap = correlation_heatmap(expression_df)

st.pyplot(heatmap)

# Save heatmap for PDF
try:
    heatmap.savefig(
        "results/heatmap.png",
        dpi=300,
        bbox_inches="tight"
    )
except:
    plt.savefig(
        "results/heatmap.png",
        dpi=300,
        bbox_inches="tight"
    )

plt.close()

# =====================================================
# SAMPLE CLUSTERING
# =====================================================

st.header("🧬 Sample Clustering")

cluster = sample_clustering(expression_df)

st.session_state["cluster_plot"] = cluster

# Display clustering
st.plotly_chart(
    cluster,
    use_container_width=True
)

st.info(
    "Clustering visualization generated successfully."
)

st.success(
    "✅ EDA results have been saved successfully."
)
