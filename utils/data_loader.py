import pandas as pd


def load_dataset(file):
    """
    Load gene expression dataset.

    Expected format:

    First column:
    Gene names

    Remaining columns:
    Samples

    """

    try:
        df = pd.read_csv(file)

        return df

    except Exception as e:
        raise Exception(
            f"Dataset loading failed: {e}"
        )
