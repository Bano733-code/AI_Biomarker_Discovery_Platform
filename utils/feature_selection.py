# utils/feature_selection.py

import numpy as np
import pandas as pd

from sklearn.feature_selection import (
    f_classif,
    mutual_info_classif,
    VarianceThreshold
)

from sklearn.ensemble import RandomForestClassifier



# =====================================================
# PREPARE FEATURES
# =====================================================

def prepare_features(
    expression_df,
    metadata_df
):
    """
    Convert RNA-seq expression matrix into ML format.

    Input:
        Rows = Genes
        Columns = Samples

    Output:
        X = Samples × Genes
        y = Labels
    """

    # -----------------------------------------------
    # Remove Gene column
    # -----------------------------------------------

    expression = expression_df.iloc[:, 1:]


    # -----------------------------------------------
    # Transpose
    # Samples become rows
    # Genes become columns
    # -----------------------------------------------

    X = expression.T


    # Gene names as columns

    X.columns = expression_df.iloc[:, 0]


    # -----------------------------------------------
    # Convert numeric
    # -----------------------------------------------

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )


    # -----------------------------------------------
    # Replace infinite values
    # -----------------------------------------------

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )


    # -----------------------------------------------
    # Remove empty genes
    # -----------------------------------------------

    X = X.dropna(
        axis=1,
        how="all"
    )


    # -----------------------------------------------
    # Remove empty samples
    # -----------------------------------------------

    X = X.dropna(
        axis=0,
        how="all"
    )


    # -----------------------------------------------
    # Fill missing values
    # -----------------------------------------------

    X = X.fillna(
        X.mean()
    )

    X = X.fillna(0)



    # =================================================
    # Find label column
    # =================================================

    label_columns = [
        "Group",
        "group",
        "condition",
        "Condition"
    ]


    label = None


    for col in label_columns:

        if col in metadata_df.columns:

            label = col
            break



    if label is None:

        raise ValueError(
            "No class label found. "
            "Expected Group/group/condition/Condition column."
        )



    y = metadata_df[label]



    # -----------------------------------------------
    # Align samples
    # -----------------------------------------------

    y.index = metadata_df.iloc[:,0]


    common_samples = X.index.intersection(
        y.index
    )


    X = X.loc[common_samples]

    y = y.loc[common_samples]


    return X, y
# =====================================================
# RNA-SEQ NORMALIZATION
# =====================================================

def log_normalization(X):

    """
    Log1p normalization for RNA-seq data.
    """

    X = X.astype(float)

    X = np.log1p(X)

    return pd.DataFrame(

        X,

        columns=X.columns,

        index=X.index

    )




# =====================================================
# VARIANCE FILTERING
# =====================================================

def variance_filter(
    X,
    threshold=0.01
):
    """
    Remove low variance genes.

    Helps RNA-seq feature selection by
    removing genes with little information.
    """


    selector = VarianceThreshold(
        threshold=threshold
    )


    filtered = selector.fit_transform(
        X
    )


    selected_genes = X.columns[
        selector.get_support()
    ]


    X_filtered = pd.DataFrame(

        filtered,

        columns=selected_genes,

        index=X.index

    )


    return X_filtered





# =====================================================
# ANOVA FEATURE SELECTION
# =====================================================

def anova_selection(
    X,
    y
):

    X = X.astype(float)


    scores, p_values = f_classif(
        X,
        y
    )


    result = pd.DataFrame({

        "Gene": X.columns,

        "ANOVA Score": scores,

        "P Value": p_values

    })


    # remove invalid values

    result = result.replace(
        [np.inf, -np.inf],
        np.nan
    )


    result = result.dropna()



    return result.sort_values(

        by="ANOVA Score",

        ascending=False

    )





# =====================================================
# MUTUAL INFORMATION
# =====================================================

def mutual_information_selection(
    X,
    y
):

    X = X.astype(float)



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





# =====================================================
# RANDOM FOREST FEATURE IMPORTANCE
# =====================================================

def random_forest_selection(
    X,
    y
):

    X = X.astype(float)



    model = RandomForestClassifier(

        n_estimators=300,

        max_depth=None,

        random_state=42,

        n_jobs=-1,

        class_weight="balanced"

    )


    model.fit(

        X,

        y

    )



    result = pd.DataFrame({

        "Gene": X.columns,

        "Importance": model.feature_importances_

    })



    return result.sort_values(

        by="Importance",

        ascending=False

    )





# =====================================================
# COMBINE FEATURE RANKINGS
# =====================================================

def combine_rankings(

    anova,

    mi,

    rf

):


    merged = anova.merge(

        mi,

        on="Gene",

        how="inner"

    )


    merged = merged.merge(

        rf,

        on="Gene",

        how="inner"

    )



    # Rank each method

    merged["ANOVA Rank"] = (

        merged["ANOVA Score"]

        .rank(
            ascending=False
        )

    )


    merged["MI Rank"] = (

        merged["MI Score"]

        .rank(
            ascending=False
        )

    )


    merged["RF Rank"] = (

        merged["Importance"]

        .rank(
            ascending=False
        )

    )



    # Lower rank = better

    merged["Final Score"] = (

        merged["ANOVA Rank"]

        +

        merged["MI Rank"]

        +

        merged["RF Rank"]

    )



    return merged.sort_values(

        by="Final Score",

        ascending=True

    )





# =====================================================
# GET TOP BIOMARKERS
# =====================================================

def get_top_genes(

    ranking_df,

    n_genes=50

):

    """
    Return top ranked biomarkers.
    """

    return ranking_df.head(
        n_genes
    )


# =====================================================
# COMPLETE BIOMARKER DISCOVERY PIPELINE
# =====================================================


def run_feature_selection_pipeline(

    X,

    y,

    top_genes=100,

    variance_threshold=0.01

):

    """
    Complete RNA-seq biomarker pipeline:


    Expression Data

          |
          ↓

    Log Normalization

          |
          ↓

    Variance Filtering

          |
          ↓

    ANOVA

          +

    Mutual Information

          +

    Random Forest

          |
          ↓

    Top Biomarkers

          |
          ↓

    ML-ready expression matrix

    """



    # ----------------------------------
    # Step 1
    # Normalization
    # ----------------------------------

    X = log_normalization(
        X
    )


    print(
        "After normalization:",
        X.shape
    )



    # ----------------------------------
    # Step 2
    # Variance filtering
    # ----------------------------------

    X_filtered = variance_filter(

        X,

        threshold=variance_threshold

    )


    print(
        "After variance filtering:",
        X_filtered.shape
    )



    # ----------------------------------
    # Step 3
    # Feature selection
    # ----------------------------------

    anova = anova_selection(

        X_filtered,

        y

    )


    mi = mutual_information_selection(

        X_filtered,

        y

    )


    rf = random_forest_selection(

        X_filtered,

        y

    )



    # ----------------------------------
    # Step 4
    # Combine rankings
    # ----------------------------------

    ranking = combine_rankings(

        anova,

        mi,

        rf

    )



    # ----------------------------------
    # Step 5
    # Select top genes
    # ----------------------------------

    biomarkers = get_top_genes(

        ranking,

        top_genes

    )



    selected_genes = biomarkers["Gene"]



    # Final ML matrix

    X_selected = X_filtered[
        selected_genes
    ]



    return (

        X_selected,

        biomarkers

    )
