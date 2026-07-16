import pandas as pd
import shap

import matplotlib.pyplot as plt



# =====================================================
# CALCULATE SHAP VALUES
# =====================================================

def calculate_shap_values(
        model,
        X
):

    """
    Calculate SHAP values.

    Supports tree models
    like Random Forest.
    """


    explainer = shap.TreeExplainer(
        model
    )


    shap_values = explainer.shap_values(
        X
    )


    return shap_values, explainer




# =====================================================
# FEATURE IMPORTANCE
# =====================================================

def get_feature_importance(
        X,
        shap_values
):

    """
    Rank genes using
    mean absolute SHAP value.
    """


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




# =====================================================
# SHAP SUMMARY PLOT
# =====================================================

def shap_summary_plot(
        shap_values,
        X
):


    if isinstance(shap_values,list):

        values = shap_values[1]

    else:

        values = shap_values



    fig = plt.figure(
        figsize=(10,6)
    )


    shap.summary_plot(

        values,

        X,

        show=False

    )


    return fig




# =====================================================
# SHAP BAR PLOT
# =====================================================

def shap_bar_plot(
        shap_values,
        X
):


    if isinstance(shap_values,list):

        values = shap_values[1]

    else:

        values = shap_values



    fig = plt.figure(
        figsize=(10,6)
    )


    shap.summary_plot(

        values,

        X,

        plot_type="bar",

        show=False

    )


    return fig
