import pandas as pd



def normalize_scores(series):
    """
    Normalize scores between 0 and 1.
    """

    if series.max() == series.min():

        return series * 0

    return (
        series - series.min()
    ) / (
        series.max() - series.min()
    )



def combine_biomarker_scores(
        feature_results,
        shap_results
):
    """
    Combine feature selection
    and SHAP importance.

    Final score =
    Feature score + SHAP score
    """


    feature_results = feature_results.copy()

    shap_results = shap_results.copy()



    # Normalize values

    if "Final_Score" in feature_results.columns:

        feature_results["Feature_Score"] = (
            normalize_scores(
                feature_results["Final_Score"]
            )
        )


    else:

        feature_results["Feature_Score"] = 0




    shap_results["SHAP_Score"] = (
        normalize_scores(
            shap_results["SHAP Importance"]
        )
    )



    combined = feature_results.merge(
        shap_results,
        on="Gene",
        how="outer"
    )



    combined = combined.fillna(0)



    combined["Biomarker_Score"] = (
        combined["Feature_Score"]
        +
        combined["SHAP_Score"]
    )



    combined = combined.sort_values(
        by="Biomarker_Score",
        ascending=False
    )



    return combined



def get_top_biomarkers(
        df,
        number=10
):
    """
    Return top N biomarkers.
    """

    return df.head(number)
