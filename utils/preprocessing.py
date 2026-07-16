import pandas as pd
import numpy as np

from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler
)


def remove_duplicate_genes(df: pd.DataFrame):
    """
    Remove duplicate gene names.
    
    Assumes first column contains gene names.
    """

    gene_column = df.columns[0]

    df = df.drop_duplicates(
        subset=[gene_column]
    )

    return df



def handle_missing_values(df: pd.DataFrame):
    """
    Replace missing values.

    Numeric columns:
    filled with median value.
    """

    numeric_columns = (
        df.select_dtypes(
            include=np.number
        )
        .columns
    )

    for col in numeric_columns:

        df[col] = df[col].fillna(
            df[col].median()
        )

    return df



def log_transform(df: pd.DataFrame):
    """
    Apply log2 transformation
    to expression values.
    """

    gene_column = df.columns[0]

    genes = df[gene_column]

    expression = df.drop(
        columns=[gene_column]
    )

    expression = np.log2(
        expression + 1
    )

    result = pd.concat(
        [
            genes,
            expression
        ],
        axis=1
    )

    return result



def scale_data(
    df: pd.DataFrame,
    method="standard"
):
    """
    Scale gene expression values.
    
    Methods:
    - standard
    - minmax
    """

    gene_column = df.columns[0]


    genes = df[gene_column]


    expression = df.drop(
        columns=[gene_column]
    )


    if method == "standard":

        scaler = StandardScaler()

    elif method == "minmax":

        scaler = MinMaxScaler()

    else:

        raise ValueError(
            "Invalid scaling method"
        )


    scaled = scaler.fit_transform(
        expression
    )


    scaled_df = pd.DataFrame(
        scaled,
        columns=expression.columns
    )


    result = pd.concat(
        [
            genes.reset_index(drop=True),
            scaled_df
        ],
        axis=1
    )


    return result
