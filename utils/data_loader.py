import pandas as pd


def load_expression_data(file):
    """
    Load gene expression matrix.
    """

    try:
        expression_df = pd.read_csv(file)
        return expression_df

    except Exception as e:
        raise Exception(
            f"Expression dataset loading failed: {e}"
        )


def load_metadata(file):
    """
    Load sample metadata.
    """

    try:
        metadata_df = pd.read_csv(file)
        return metadata_df

    except Exception as e:
        raise Exception(
            f"Metadata loading failed: {e}"
        )


def validate_expression_data(expression_df):
    """
    Validate expression matrix.
    """

    report = {}

    report["Genes"] = expression_df.shape[0]
    report["Samples"] = expression_df.shape[1] - 1

    report["Missing Values"] = (
        expression_df.isnull().sum().sum()
    )

    report["Duplicate Genes"] = (
        expression_df.duplicated(
            subset=[expression_df.columns[0]]
        ).sum()
    )

    return report


def validate_metadata(metadata_df, expression_df):
    """
    Validate metadata against expression matrix.
    """

    report = {}

    if "Sample" not in metadata_df.columns:
        report["Sample Column"] = "Missing"

    if "Group" not in metadata_df.columns:
        report["Group Column"] = "Missing"

    expression_samples = list(expression_df.columns[1:])
    metadata_samples = metadata_df["Sample"].tolist()

    missing_samples = [
        sample
        for sample in expression_samples
        if sample not in metadata_samples
    ]

    report["Missing Samples"] = missing_samples

    report["Duplicate Metadata"] = (
        metadata_df.duplicated(
            subset=["Sample"]
        ).sum()
    )

    report["Groups"] = (
        metadata_df["Group"]
        .value_counts()
        .to_dict()
    )

    return report
