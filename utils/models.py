# utils/models.py


import os
import joblib
import pandas as pd
import numpy as np


from sklearn.model_selection import train_test_split


from sklearn.ensemble import RandomForestClassifier


from sklearn.linear_model import LogisticRegression


from sklearn.pipeline import Pipeline


from sklearn.preprocessing import StandardScaler


from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)





# =====================================================
# PREPARE MACHINE LEARNING DATA
# =====================================================


def prepare_ml_data(
        expression_df,
        metadata_df
):

    """
    Convert expression matrix into ML format.

    Input:

        Genes x Samples

    Output:

        X = Samples x Genes

        y = Labels

    """



    # Gene names

    genes = expression_df.iloc[:,0]



    # Expression values

    expression = expression_df.iloc[:,1:]



    # Samples become rows

    X = expression.T



    # Genes become features

    X.columns = genes



    # Numeric conversion

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )



    X = X.fillna(0)



    # -------------------------
    # Label
    # -------------------------


    if "Group" in metadata_df.columns:

        y = metadata_df["Group"]

    elif "group" in metadata_df.columns:

        y = metadata_df["group"]

    elif "Condition" in metadata_df.columns:

        y = metadata_df["Condition"]

    else:

        raise ValueError(
            "No label column found"
        )



    # Align labels

    y.index = metadata_df.iloc[:,0]


    common = X.index.intersection(
        y.index
    )


    X = X.loc[common]

    y = y.loc[common]



    return X,y





# =====================================================
# TRAIN TEST SPLIT
# =====================================================


def split_data(
        X,
        y
):


    # Remove classes with only one sample

    counts = y.value_counts()


    valid_classes = counts[
        counts >= 2
    ].index



    mask = y.isin(
        valid_classes
    )


    X = X[mask]

    y = y[mask]



    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.3,

        random_state=42,

        stratify=y

    )


    return (
        X_train,
        X_test,
        y_train,
        y_test
    )





# =====================================================
# RANDOM FOREST
# =====================================================


def train_random_forest(
        X_train,
        y_train
):


    model = RandomForestClassifier(

        n_estimators=300,

        random_state=42,

        class_weight="balanced",

        n_jobs=-1

    )


    model.fit(

        X_train,

        y_train

    )


    return model





# =====================================================
# LOGISTIC REGRESSION
# =====================================================


def train_logistic_regression(
        X_train,
        y_train
):


    model = Pipeline(

        [

            (
                "scaler",

                StandardScaler()

            ),


            (

                "classifier",

                LogisticRegression(

                    max_iter=3000,

                    class_weight="balanced"

                )

            )

        ]

    )


    model.fit(

        X_train,

        y_train

    )


    return model





# =====================================================
# MODEL EVALUATION
# =====================================================


def evaluate_model(
        model,
        X_test,
        y_test
):


    predictions = model.predict(
        X_test
    )


    metrics={}



    metrics["Accuracy"] = accuracy_score(

        y_test,

        predictions

    )


    metrics["Precision"] = precision_score(

        y_test,

        predictions,

        average="weighted",

        zero_division=0

    )


    metrics["Recall"] = recall_score(

        y_test,

        predictions,

        average="weighted",

        zero_division=0

    )


    metrics["F1 Score"] = f1_score(

        y_test,

        predictions,

        average="weighted",

        zero_division=0

    )



    # ROC-AUC

    try:

        probabilities = model.predict_proba(
            X_test
        )


        if probabilities.shape[1] == 2:

            metrics["ROC-AUC"] = roc_auc_score(

                y_test,

                probabilities[:,1]

            )

        else:

            metrics["ROC-AUC"] = roc_auc_score(

                y_test,

                probabilities,

                multi_class="ovr"

            )


    except:

        metrics["ROC-AUC"] = None





    metrics["Confusion Matrix"] = confusion_matrix(

        y_test,

        predictions

    )



    metrics["Classification Report"] = pd.DataFrame(

        classification_report(

            y_test,

            predictions,

            output_dict=True

        )

    ).T



    return metrics





# =====================================================
# FEATURE IMPORTANCE (FOR SHAP)
# =====================================================


def get_feature_importance(
        model,
        features
):


    """
    Extract important genes
    for interpretation.
    """


    if hasattr(
        model,
        "feature_importances_"
    ):


        importance = model.feature_importances_


    else:

        return None



    return pd.DataFrame({

        "Gene":features,

        "Importance":importance

    }).sort_values(

        "Importance",

        ascending=False

    )





# =====================================================
# SAVE MODEL
# =====================================================


def save_model(

        model,

        filename="models/biomarker_model.pkl"

):


    os.makedirs(

        "models",

        exist_ok=True

    )


    joblib.dump(

        model,

        filename

    )
