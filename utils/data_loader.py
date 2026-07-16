import pandas as pd


def load_dataset(file):
    """
    Load gene expression CSV dataset.
    """ 

    try:
        df = pd.read_csv(file)

        return df

    except Exception as e:
        raise Exception(
            f"Dataset loading failed: {str(e)}"
        )


def validate_dataset(df):
    """
    Basic dataset validation.
    """

    report = {}

    report["rows"] = df.shape[0]
    report["columns"] = df.shape[1]

    report["missing_values"] = (
        df.isnull()
        .sum()
        .sum()
    )

    report["duplicate_rows"] = (
        df.duplicated()
        .sum()
    )

    return report
