import pandas as pd
import plotly.express as px

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import matplotlib.pyplot as plt
import seaborn as sns



def dataset_statistics(df: pd.DataFrame):
    """
    Generate dataset statistics.
    """

    stats = {
        "Number of Genes": df.shape[0],
        "Number of Samples": df.shape[1] - 1,
        "Missing Values": df.isnull().sum().sum(),
        "Duplicate Rows": df.duplicated().sum()
    }

    return stats

def prepare_expression_data(df):

    """
    Prepare numeric expression matrix
    for ML and visualization.
    """

    gene_column = df.columns[0]

    expression = df.drop(
        columns=[gene_column]
    )


    # Convert all values to numeric
    expression = expression.apply(
        pd.to_numeric,
        errors="coerce"
    )


    # Remove columns that became empty
    expression = expression.dropna(
        axis=1,
        how="all"
    )


    # Fill remaining missing values
    expression = expression.fillna(
        expression.median()
    )


    return expression



def perform_pca(df: pd.DataFrame):

    """
    Perform PCA on gene expression data.
    """

    expression = prepare_expression_data(df)


    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(
        expression.T
    )


    pca = PCA(
        n_components=2
    )


    components = pca.fit_transform(
        scaled_data
    )


    pca_df = pd.DataFrame(
        components,
        columns=[
            "PC1",
            "PC2"
        ]
    )


    pca_df["Sample"] = expression.columns


    return pca_df, pca.explained_variance_ratio_



def create_pca_plot(pca_df):

    """
    Create interactive PCA plot.
    """

    fig = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        text="Sample",
        title="PCA Analysis of Samples"
    )


    return fig



def correlation_heatmap(df):

    """
    Generate correlation heatmap.
    """

    expression = prepare_expression_data(df)


    correlation = expression.corr()


    fig, ax = plt.subplots(
        figsize=(10,6)
    )


    sns.heatmap(
        correlation,
        cmap="coolwarm",
        ax=ax
    )


    ax.set_title(
        "Sample Correlation Heatmap"
    )


    return fig



def sample_clustering(df):

    """
    Create sample correlation clustering.
    """

    expression = prepare_expression_data(df)


    correlation = expression.corr()


    fig = px.imshow(
        correlation,
        title="Sample Clustering Matrix",
        text_auto=True
    )


    return fig
