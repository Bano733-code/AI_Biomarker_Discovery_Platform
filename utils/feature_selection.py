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
# DATA PREPARATION
# =====================================================


def prepare_features(
        expression_df,
        metadata_df
):

    """
    Convert RNA-seq matrix into ML format.

    Input:
        Genes x Samples

    Output:
        Samples x Genes
        Labels
    """



    # Remove gene column

    expression = expression_df.iloc[:,1:]



    # Samples as rows

    X = expression.T



    # Gene names

    X.columns = expression_df.iloc[:,0]



    # Numeric conversion

    X = X.apply(

        pd.to_numeric,

        errors="coerce"

    )



    # Remove invalid values

    X = X.replace(

        [np.inf,-np.inf],

        np.nan

    )



    # Remove empty genes

    X = X.dropna(

        axis=1,

        how="all"

    )



    # Remove empty samples

    X = X.dropna(

        axis=0,

        how="all"

    )



    # Fill missing values

    X = X.fillna(
        X.mean()
    )


    X = X.fillna(0)



    # -------------------------------
    # Label detection
    # -------------------------------


    label_columns=[

        "Group",
        "group",
        "condition",
        "Condition"

    ]


    label=None



    for col in label_columns:

        if col in metadata_df.columns:

            label=col

            break



    if label is None:

        raise ValueError(
            "No label column found"
        )



    y = metadata_df[label]



    # Sample ID alignment

    y.index = metadata_df.iloc[:,0]



    common = X.index.intersection(

        y.index

    )


    X=X.loc[common]

    y=y.loc[common]



    return X,y







# =====================================================
# NORMALIZATION
# =====================================================


def log_normalization(X):

    """
    RNA-seq log1p normalization
    """



    X = X.astype(float)



    X = X.replace(

        [np.inf,-np.inf],

        np.nan

    )



    X = X.fillna(0)



    X = np.log1p(X)



    X = X.replace(

        [np.inf,-np.inf],

        np.nan

    )



    X = X.fillna(0)



    return X







# =====================================================
# VARIANCE FILTERING
# =====================================================


def variance_filter(

        X,

        threshold=0.01

):


    """
    Remove low variance genes
    """



    X = X.replace(

        [np.inf,-np.inf],

        np.nan

    )


    X = X.fillna(0)



    selector = VarianceThreshold(

        threshold=threshold

    )



    filtered = selector.fit_transform(

        X

    )



    genes = X.columns[

        selector.get_support()

    ]



    X_filtered=pd.DataFrame(

        filtered,

        columns=genes,

        index=X.index

    )



    return X_filtered







# =====================================================
# ANOVA
# =====================================================


def anova_selection(

        X,

        y

):


    X=X.replace(

        [np.inf,-np.inf],

        np.nan

    )


    X=X.fillna(0)



    scores,p_values=f_classif(

        X,

        y

    )



    result=pd.DataFrame({

        "Gene":X.columns,

        "ANOVA Score":scores,

        "P Value":p_values

    })



    result=result.replace(

        [np.inf,-np.inf],

        np.nan

    )


    result=result.dropna()



    return result.sort_values(

        "ANOVA Score",

        ascending=False

    )









# =====================================================
# MUTUAL INFORMATION
# =====================================================


def mutual_information_selection(

        X,

        y

):


    X=X.fillna(0)



    scores=mutual_info_classif(

        X,

        y,

        random_state=42

    )



    result=pd.DataFrame({

        "Gene":X.columns,

        "MI Score":scores

    })



    return result.sort_values(

        "MI Score",

        ascending=False

    )









# =====================================================
# RANDOM FOREST IMPORTANCE
# =====================================================


def random_forest_selection(

        X,

        y

):


    X=X.fillna(0)



    model=RandomForestClassifier(

        n_estimators=300,

        random_state=42,

        class_weight="balanced",

        n_jobs=-1

    )



    model.fit(

        X,

        y

    )



    result=pd.DataFrame({

        "Gene":X.columns,

        "Importance":model.feature_importances_

    })



    return result.sort_values(

        "Importance",

        ascending=False

    )









# =====================================================
# COMBINE RANKINGS
# =====================================================


def combine_rankings(

        anova,

        mi,

        rf

):


    merged=anova.merge(

        mi,

        on="Gene",

        how="inner"

    )



    merged=merged.merge(

        rf,

        on="Gene",

        how="inner"

    )



    merged["ANOVA Rank"]=merged[
        "ANOVA Score"
    ].rank(
        ascending=False
    )


    merged["MI Rank"]=merged[
        "MI Score"
    ].rank(
        ascending=False
    )


    merged["RF Rank"]=merged[
        "Importance"
    ].rank(
        ascending=False
    )



    merged["Final Score"]=(

        merged["ANOVA Rank"]

        +

        merged["MI Rank"]

        +

        merged["RF Rank"]

    )



    return merged.sort_values(

        "Final Score",

        ascending=True

    )









# =====================================================
# TOP BIOMARKERS
# =====================================================


def get_top_genes(

        ranking_df,

        n_genes=100

):


    return ranking_df.head(
        n_genes
    )









# =====================================================
# COMPLETE PIPELINE
# =====================================================


def run_feature_selection_pipeline(

        X,

        y,

        top_genes=100,

        variance_threshold=0.01

):


    print(
        "Original:",
        X.shape
    )



    # Normalization

    X=log_normalization(X)



    print(
        "Normalized:",
        X.shape
    )



    # Variance filtering

    X_filtered=variance_filter(

        X,

        threshold=variance_threshold

    )



    print(
        "Variance filtered:",
        X_filtered.shape
    )



    if X_filtered.shape[1]==0:

        raise ValueError(
            "No genes left after variance filtering. Lower threshold."
        )



    # Feature selection


    anova=anova_selection(

        X_filtered,

        y

    )



    mi=mutual_information_selection(

        X_filtered,

        y

    )



    rf=random_forest_selection(

        X_filtered,

        y

    )



    # Ranking


    ranking=combine_rankings(

        anova,

        mi,

        rf

    )



    biomarkers=get_top_genes(

        ranking,

        top_genes

    )



    selected_genes=biomarkers["Gene"]



    X_selected=X_filtered[

        selected_genes

    ]



    print(

        "Selected biomarkers:",

        X_selected.shape

    )



    return (

        X_selected,

        biomarkers

    )
