import pandas as pd


# ============================================================
# LOAD EXPRESSION DATA
# ============================================================

def load_expression_data(file):
    """
    Load a gene expression matrix from CSV.

    Expected format:

        Gene    Sample1    Sample2    Sample3
        TP53    10.2       11.4       9.8
        BRCA1   5.2        6.1        5.8

    The first column should contain gene identifiers.
    """

    try:

        expression_df = pd.read_csv(file)

    except Exception as e:

        raise Exception(
            f"Expression dataset loading failed: {e}"
        )


    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if expression_df.empty:

        raise Exception(
            "Expression dataset is empty."
        )


    # --------------------------------------------------------
    # Standardize first column
    # --------------------------------------------------------

    if expression_df.columns[0] != "Gene":

        expression_df = expression_df.rename(
            columns={
                expression_df.columns[0]: "Gene"
            }
        )


    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    expression_df = expression_df.dropna(
        how="all"
    )


    # --------------------------------------------------------
    # Clean gene identifiers
    # --------------------------------------------------------

    expression_df["Gene"] = (
        expression_df["Gene"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Remove invalid gene identifiers
    # --------------------------------------------------------

    expression_df = expression_df[
        expression_df["Gene"].notna()
    ]

    expression_df = expression_df[
        expression_df["Gene"] != ""
    ]

    expression_df = expression_df[
        expression_df["Gene"].str.lower() != "nan"
    ]


    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    expression_df = expression_df.reset_index(
        drop=True
    )


    return expression_df


# ============================================================
# LOAD SAMPLE METADATA
# ============================================================

def load_metadata(file):
    """
    Load sample metadata from CSV.

    Expected format:

        Sample      Group
        GSM001      Control
        GSM002      Control
        GSM003      Disease
        GSM004      Disease
    """

    try:

        metadata_df = pd.read_csv(file)

    except Exception as e:

        raise Exception(
            f"Metadata loading failed: {e}"
        )


    # --------------------------------------------------------
    # Empty dataset check
    # --------------------------------------------------------

    if metadata_df.empty:

        raise Exception(
            "Metadata file is empty."
        )


    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    metadata_df.columns = [
        str(column).strip()
        for column in metadata_df.columns
    ]


    # --------------------------------------------------------
    # Sample column check
    # --------------------------------------------------------

    if "Sample" not in metadata_df.columns:

        raise Exception(
            "Metadata file must contain a 'Sample' column."
        )


    # --------------------------------------------------------
    # Clean Sample identifiers
    # --------------------------------------------------------

    metadata_df["Sample"] = (
        metadata_df["Sample"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    metadata_df = metadata_df.dropna(
        how="all"
    )


    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    metadata_df = metadata_df.reset_index(
        drop=True
    )


    return metadata_df


# ============================================================
# VALIDATE EXPRESSION DATA
# ============================================================

def validate_expression_data(expression_df):
    """
    Validate the gene expression matrix.

    Returns
    -------
    dict
        Validation report containing:

        Genes
        Samples
        Missing Values
        Duplicate Genes
        Empty Gene IDs
    """

    report = {}


    # --------------------------------------------------------
    # Basic checks
    # --------------------------------------------------------

    if expression_df is None:

        return {
            "Valid": False,
            "Error": "Expression dataset is None.",
        }


    if expression_df.empty:

        return {
            "Valid": False,
            "Error": "Expression dataset is empty.",
        }


    # --------------------------------------------------------
    # Gene column
    # --------------------------------------------------------

    if "Gene" not in expression_df.columns:

        return {
            "Valid": False,
            "Error": "Expression dataset must contain a 'Gene' column.",
        }


    # --------------------------------------------------------
    # Number of genes
    # --------------------------------------------------------

    report["Genes"] = int(
        expression_df.shape[0]
    )


    # --------------------------------------------------------
    # Number of samples
    # --------------------------------------------------------

    report["Samples"] = int(
        expression_df.shape[1] - 1
    )


    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    report["Missing Values"] = int(
        expression_df.isnull()
        .sum()
        .sum()
    )


    # --------------------------------------------------------
    # Duplicate genes
    # --------------------------------------------------------

    report["Duplicate Genes"] = int(
        expression_df["Gene"]
        .duplicated()
        .sum()
    )


    # --------------------------------------------------------
    # Empty gene identifiers
    # --------------------------------------------------------

    empty_genes = (
        expression_df["Gene"]
        .astype(str)
        .str.strip()
        .isin(["", "nan", "None"])
        .sum()
    )

    report["Empty Gene IDs"] = int(
        empty_genes
    )


    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    report["Valid"] = (
        report["Genes"] > 0
        and report["Samples"] > 0
        and report["Empty Gene IDs"] == 0
    )


    return report


# ============================================================
# VALIDATE METADATA
# ============================================================

def validate_metadata(
    metadata_df,
    expression_df,
):
    """
    Validate sample metadata against the expression matrix.

    Expected metadata columns:

        Sample
        Group

    The function checks:

        - Sample column
        - Group column
        - Missing samples
        - Extra metadata samples
        - Duplicate samples
        - Group distribution
    """

    report = {}


    # --------------------------------------------------------
    # Basic checks
    # --------------------------------------------------------

    if metadata_df is None:

        return {
            "Valid": False,
            "Error": "Metadata is None.",
        }


    if metadata_df.empty:

        return {
            "Valid": False,
            "Error": "Metadata is empty.",
        }


    # --------------------------------------------------------
    # Sample column
    # --------------------------------------------------------

    if "Sample" not in metadata_df.columns:

        return {
            "Valid": False,
            "Sample Column": "Missing",
            "Error": (
                "Metadata must contain a 'Sample' column."
            ),
        }


    report["Sample Column"] = "Present"


    # --------------------------------------------------------
    # Group column
    # --------------------------------------------------------

    if "Group" not in metadata_df.columns:

        report["Group Column"] = "Missing"

    else:

        report["Group Column"] = "Present"


    # --------------------------------------------------------
    # Expression sample IDs
    # --------------------------------------------------------

    if (
        expression_df is not None
        and "Gene" in expression_df.columns
    ):

        expression_samples = [
            column
            for column in expression_df.columns
            if column != "Gene"
        ]

    else:

        expression_samples = []


    # --------------------------------------------------------
    # Metadata sample IDs
    # --------------------------------------------------------

    metadata_samples = (
        metadata_df["Sample"]
        .astype(str)
        .str.strip()
        .tolist()
    )


    expression_samples = [
        str(sample).strip()
        for sample in expression_samples
    ]


    # --------------------------------------------------------
    # Missing metadata samples
    # --------------------------------------------------------

    missing_metadata = [
        sample
        for sample in expression_samples
        if sample not in metadata_samples
    ]


    report["Missing Samples"] = (
        missing_metadata
    )


    # --------------------------------------------------------
    # Extra metadata samples
    # --------------------------------------------------------

    extra_metadata = [
        sample
        for sample in metadata_samples
        if sample not in expression_samples
    ]


    report["Extra Metadata Samples"] = (
        extra_metadata
    )


    # --------------------------------------------------------
    # Duplicate metadata samples
    # --------------------------------------------------------

    duplicate_count = int(
        metadata_df["Sample"]
        .duplicated()
        .sum()
    )


    report["Duplicate Metadata"] = (
        duplicate_count
    )


    # --------------------------------------------------------
    # Group information
    # --------------------------------------------------------

    if "Group" in metadata_df.columns:

        group_series = (
            metadata_df["Group"]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
        )

        report["Groups"] = (
            group_series
            .value_counts()
            .to_dict()
        )

        report["Number of Groups"] = int(
            group_series.nunique()
        )

    else:

        report["Groups"] = {}

        report["Number of Groups"] = 0


    # --------------------------------------------------------
    # Overall validation
    # --------------------------------------------------------

    report["Valid"] = (
        len(missing_metadata) == 0
        and duplicate_count == 0
    )


    return report
