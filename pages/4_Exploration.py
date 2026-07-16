import streamlit as st


from utils.visualization import (
    dataset_statistics,
    perform_pca,
    create_pca_plot,
    correlation_heatmap,
    sample_clustering
)



st.title(
    "📊 Exploratory Data Analysis"
)



if "processed_dataset" not in st.session_state:

    st.warning(
        "Please complete preprocessing first."
    )

    st.stop()



expression_df = st.session_state["processed_data"]

metadata_df = st.session_state["metadata"]



# ----------------------------
# Dataset Statistics
# ----------------------------


st.header(
    "Dataset Statistics"
)


stats = dataset_statistics(df)


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



# ----------------------------
# PCA
# ----------------------------


st.header(
    "Principal Component Analysis (PCA)"
)

st.write("Data Types:")
st.write(df.dtypes)

pca_df, variance = perform_pca(df)



st.write(
    "Explained Variance:",
    variance
)



fig = create_pca_plot(
    pca_df
)


st.plotly_chart(
    fig,
    use_container_width=True
)



# ----------------------------
# Correlation
# ----------------------------


st.header(
    "Sample Correlation Heatmap"
)



heatmap = correlation_heatmap(
    df
)


st.pyplot(
    heatmap
)



# ----------------------------
# Clustering
# ----------------------------


st.header(
    "Sample Clustering"
)



cluster_fig = sample_clustering(
    df
)


st.plotly_chart(
    cluster_fig,
    use_container_width=True
)
