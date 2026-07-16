import pandas as pd

from sklearn.feature_selection import (
    f_classif,
    mutual_info_classif
)

from sklearn.ensemble import RandomForestClassifier



def prepare_features(df):

    """
    Prepare X and y for feature selection.
    """

    gene_column = df.columns[0]
    label_column = df.columns[-1]


    X = df.drop(
        columns=[
            gene_column,
            label_column
        ]
    )


    y = df[label_column]


    return X.T, y



def anova_selection(X, y):

    """
    ANOVA feature selection.
    """

    scores, p_values = f_classif(
        X,
        y
    )


    result = pd.DataFrame(
        {
            "Gene": X.columns,
            "ANOVA_Score": scores,
            "P_Value": p_values
        }
    )


    result = result.sort_values(
        by="ANOVA_Score",
        ascending=False
    )


    return result



def mutual_information_selection(X, y):

    """
    Mutual information ranking.
    """

    scores = mutual_info_classif(
        X,
        y
    )


    result = pd.DataFrame(
        {
            "Gene": X.columns,
            "MI_Score": scores
        }
    )


    result = result.sort_values(
        by="MI_Score",
        ascending=False
    )


    return result



def random_forest_selection(X, y):

    """
    Random Forest feature importance.
    """


    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )


    model.fit(
        X,
        y
    )


    result = pd.DataFrame(
        {
            "Gene": X.columns,
            "Importance":
                model.feature_importances_
        }
    )


    result = result.sort_values(
        by="Importance",
        ascending=False
    )


    return result



def combine_rankings(
        anova,
        mi,
        rf
):

    """
    Combine feature ranking results.
    """


    merged = anova.merge(
        mi,
        on="Gene"
    )


    merged = merged.merge(
        rf,
        on="Gene"
    )


    merged["Final_Score"] = (
        merged["ANOVA_Score"].rank()
        +
        merged["MI_Score"].rank()
        +
        merged["Importance"].rank()
    )


    return merged.sort_values(
        by="Final_Score",
        ascending=False
    )
