import pandas as pd
import shap

import matplotlib.pyplot as plt



def calculate_shap_values(
        model,
        X
):
    """
    Calculate SHAP values.

    Uses TreeExplainer for
    tree-based models.
    """

    explainer = shap.TreeExplainer(
        model
    )


    shap_values = explainer.shap_values(
        X
    )


    return shap_values, explainer





def get_feature_importance(
        X,
        shap_values
):
    """
    Rank biomarkers according
    to mean absolute SHAP value.
    """


    # Binary classification
    # SHAP sometimes returns list

    if isinstance(shap_values, list):

        values = shap_values[1]

    else:

        values = shap_values



    importance = pd.DataFrame(
        {
            "Gene": X.columns,
            "SHAP Importance":
                abs(values).mean(axis=0)
        }
    )


    importance = importance.sort_values(
        by="SHAP Importance",
        ascending=False
    )


    return importance




def shap_summary_plot(
        shap_values,
        X
):

    """
    Generate SHAP summary plot.
    """


    if isinstance(shap_values, list):

        values = shap_values[1]

    else:

        values = shap_values



    fig = plt.figure()


    shap.summary_plot(
        values,
        X,
        show=False
    )


    return fig




def shap_bar_plot(
        shap_values,
        X
):

    """
    Generate SHAP bar plot.
    """


    if isinstance(shap_values,list):

        values = shap_values[1]

    else:

        values = shap_values



    fig = plt.figure()


    shap.summary_plot(
        values,
        X,
        plot_type="bar",
        show=False
    )


    return fig
