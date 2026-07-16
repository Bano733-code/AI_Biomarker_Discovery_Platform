import pandas as pd
import plotly.express as px

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import matplotlib.pyplot as plt
import seaborn as sns


def dataset_statistics(expression_df):

    stats = {
        "Number of Genes": expression_df.shape[0],
        "Number of Samples": expression_df.shape[1] - 1,
        "Missing Values": expression_df.isnull().sum().sum(),
        "Duplicate Rows": expression_df.duplicated().sum(),
    }

    return stats


def prepare_expression_data(expression_df):

    expression = expression_df.iloc[:, 1:].copy()

    expression = expression.apply(
        pd.to_numeric,
        errors="coerce",
    )

    expression = expression.fillna(
        expression.median()
    )

    return expression


def perform_pca(expression_df, metadata_df):

    expression = prepare_expression_data(
        expression_df
    )

    # Rows = Samples
    # Columns = Genes

    expression = expression.T

    scaler = StandardScaler()

    scaled = scaler.fit_transform(expression)

    pca = PCA(
        n_components=2
    )

    components = pca.fit_transform(
        scaled
    )

    pca_df = pd.DataFrame(
        components,
        columns=["PC1", "PC2"],
    )

    pca_df["Sample"] = expression.index

    pca_df = pca_df.merge(
        metadata_df,
        on="Sample",
        how="left",
    )

    return pca_df, pca.explained_variance_ratio_


def create_pca_plot(pca_df):

    fig = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        color="Group",
        hover_name="Sample",
        text="Sample",
        title="PCA of Samples",
    )

    fig.update_traces(
        textposition="top center"
    )

    return fig


def correlation_heatmap(expression_df):

    expression = prepare_expression_data(
        expression_df
    )

    correlation = expression.corr()

    fig, ax = plt.subplots(
        figsize=(10, 8)
    )

    sns.heatmap(
        correlation,
        cmap="coolwarm",
        ax=ax,
    )

    ax.set_title(
        "Sample Correlation Heatmap"
    )

    return fig


def sample_clustering(expression_df):

    expression = prepare_expression_data(
        expression_df
    )

    correlation = expression.corr()

    fig = px.imshow(
        correlation,
        text_auto=True,
        title="Sample Clustering",
    )

    return fig
