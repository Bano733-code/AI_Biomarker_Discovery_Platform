import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier

from sklearn.linear_model import LogisticRegression

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
    Prepare expression matrix for ML.

    Input:

    expression_df:
        Genes x Samples

    metadata_df:
        Sample labels

    Output:

    X:
        Samples x Genes

    y:
        Disease labels
    """


    # Remove gene column

    genes = expression_df.iloc[:, 0]


    expression = expression_df.iloc[:, 1:]


    # Samples as rows

    X = expression.T


    # Gene names become features

    X.columns = genes


    # Target labels

    y = metadata_df["Group"]


    return X, y



# =====================================================
# TRAIN TEST SPLIT
# =====================================================

def split_data(
        X,
        y
):

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

        n_estimators=200,

        random_state=42

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

    model = LogisticRegression(

        max_iter=2000

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


    metrics = {}


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
        )[:,1]


        metrics["ROC-AUC"] = roc_auc_score(

            y_test,

            probabilities

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
