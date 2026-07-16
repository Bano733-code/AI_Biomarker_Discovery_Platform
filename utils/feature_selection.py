import pandas as pd

from sklearn.feature_selection import (
    f_classif,
    mutual_info_classif
)

from sklearn.ensemble import RandomForestClassifier


def prepare_features(
    expression_df,
    metadata_df
):
    """
    Prepare X and y for feature selection.

    Rows = Samples
    Columns = Genes
    """

    # Remove Gene column

    expression = expression_df.iloc[:, 1:]

    # Samples become rows

    X = expression.T

    # Gene names become feature names

    X.columns = expression_df.iloc[:, 0]

    # Labels

    y = metadata_df["Group"]

    return X, y


def anova_selection(X, y):

    scores, p_values = f_classif(
        X,
        y
    )

    result = pd.DataFrame({

        "Gene": X.columns,

        "ANOVA Score": scores,

        "P Value": p_values

    })

    return result.sort_values(
        by="ANOVA Score",
        ascending=False
    )


def mutual_information_selection(X, y):

    scores = mutual_info_classif(
        X,
        y,
        random_state=42
    )

    result = pd.DataFrame({

        "Gene": X.columns,

        "MI Score": scores

    })

    return result.sort_values(
        by="MI Score",
        ascending=False
    )


def random_forest_selection(X, y):

    model = RandomForestClassifier(

        n_estimators=200,

        random_state=42

    )

    model.fit(X, y)

    result = pd.DataFrame({

        "Gene": X.columns,

        "Importance": model.feature_importances_

    })

    return result.sort_values(
        by="Importance",
        ascending=False
    )


def combine_rankings(
    anova,
    mi,
    rf
):

    merged = anova.merge(
        mi,
        on="Gene"
    )

    merged = merged.merge(
        rf,
        on="Gene"
    )

    merged["Final Score"] = (

        merged["ANOVA Score"].rank(ascending=False)

        +

        merged["MI Score"].rank(ascending=False)

        +

        merged["Importance"].rank(ascending=False)

    )

    merged = merged.sort_values(
        by="Final Score"
    )

    return merged
