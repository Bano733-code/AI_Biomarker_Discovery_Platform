import pandas as pd
import joblib

from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)



def prepare_ml_data(df):
    """
    Prepare dataset for machine learning.

    First column:
    Gene names

    Last column:
    Disease labels
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




def split_data(X, y):

    """
    Split dataset into train and test.
    """

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




def train_random_forest(
        X_train,
        y_train
):

    """
    Train Random Forest classifier.
    """


    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )


    model.fit(
        X_train,
        y_train
    )


    return model





def train_logistic_regression(
        X_train,
        y_train
):

    """
    Train Logistic Regression model.
    """


    model = LogisticRegression(
        max_iter=1000
    )


    model.fit(
        X_train,
        y_train
    )


    return model





def evaluate_model(
        model,
        X_test,
        y_test
):

    """
    Calculate model performance metrics.
    """


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


    return metrics





def save_model(
        model,
        filename="models/biomarker_model.pkl"
):

    """
    Save trained model.
    """


    joblib.dump(
        model,
        filename
    )
