import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


# =====================================================
# CALCULATE SHAP VALUES
# =====================================================

def calculate_shap_values(model, X):
    """
    Calculate SHAP values for supported models.
    """

    if isinstance(model, RandomForestClassifier):

        explainer = shap.TreeExplainer(model)

    elif isinstance(model, LogisticRegression):

        explainer = shap.LinearExplainer(model, X)

    else:

        raise Exception(
            f"Unsupported model type: {type(model)}"
        )

    shap_values = explainer(X)

    return shap_values, explainer


# =====================================================
# EXTRACT SHAP ARRAY
# =====================================================

def extract_values(shap_values):
    """
    Extract raw SHAP values regardless of SHAP version.
    """

    # New SHAP API
    if hasattr(shap_values, "values"):

        values = shap_values.values

    else:

        values = shap_values

    values = np.asarray(values)

    # Binary classifier may return:
    # (samples, features, classes)

    if values.ndim == 3:

        values = values[:, :, 1]

    return values


# =====================================================
# FEATURE IMPORTANCE
# =====================================================

def get_feature_importance(X, shap_values):
    """
    Calculate mean absolute SHAP importance.
    """

    values = extract_values(shap_values)

    importance = np.abs(values).mean(axis=0)

    importance_df = pd.DataFrame({

        "Gene": X.columns,

        "SHAP Importance": importance

    })

    importance_df = importance_df.sort_values(

        by="SHAP Importance",

        ascending=False

    )

    return importance_df


# =====================================================
# SUMMARY PLOT
# =====================================================

def shap_summary_plot(shap_values, X):

    values = extract_values(shap_values)

    plt.figure(figsize=(10,6))

    shap.summary_plot(

        values,

        X,

        show=False

    )

    return plt.gcf()


# =====================================================
# BAR PLOT
# =====================================================

def shap_bar_plot(shap_values, X):

    values = extract_values(shap_values)

    plt.figure(figsize=(10,6))

    shap.summary_plot(

        values,

        X,

        plot_type="bar",

        show=False

    )

    return plt.gcf()
