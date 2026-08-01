import streamlit as st
import os
import json
import pandas as pd
from utils.models import (
    prepare_ml_data,
    split_data,
    train_random_forest,
    train_logistic_regression,
    evaluate_model,
    save_model
)

st.title("🤖 Machine Learning Biomarker Classification")

# =====================================================
# CHECK SESSION STATE
# =====================================================

if "processed_data" not in st.session_state:

    st.warning(
        "Please complete preprocessing first."
    )

    st.stop()

if "metadata" not in st.session_state:

    st.warning(
        "Metadata not found."
    )

    st.stop()

expression_df = st.session_state["processed_data"]
metadata_df = st.session_state["metadata"]

# =====================================================
# PREPARE DATA
# =====================================================

X, y = prepare_ml_data(
    expression_df,
    metadata_df
)

st.subheader("Dataset Summary")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Samples",
        X.shape[0]
    )

with col2:
    st.metric(
        "Genes",
        X.shape[1]
    )

# =====================================================
# MODEL SELECTION
# =====================================================

model_choice = st.selectbox(
    "Select Machine Learning Model",
    [
        "Random Forest",
        "Logistic Regression"
    ]
)

# =====================================================
# TRAIN MODEL
# =====================================================

if st.button(
    "🚀 Train Model",
    use_container_width=True
):

    X_train, X_test, y_train, y_test = split_data(
        X,
        y
    )

    if model_choice == "Random Forest":

        model = train_random_forest(
            X_train,
            y_train
        )

    else:

        model = train_logistic_regression(
            X_train,
            y_train
        )

    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )
    # Save in Session State
    st.session_state["trained_model"] = model
    st.session_state["model_metrics"] = metrics
    
    # Create results folder
    os.makedirs("results", exist_ok=True)
    
    # Save metrics
    metrics_to_save = {}
    
    for key, value in metrics.items():
    
        if key not in [
            "Classification Report",
            "Confusion Matrix"
        ]:
    
            metrics_to_save[key] = value
    
    with open(
        "results/model_metrics.json",
        "w"
    ) as f:
    
        json.dump(
            metrics_to_save,
            f,
            indent=4
        )
    
    # Save Classification Report
    if "Classification Report" in metrics:
    
        report_df = pd.DataFrame(
            metrics["Classification Report"]
        )
    
        report_df.to_csv(
            "results/classification_report.csv"
        )
    
    # Save Confusion Matrix
    if "Confusion Matrix" in metrics:
    
        cm = pd.DataFrame(
            metrics["Confusion Matrix"]
        )
    
        cm.to_csv(
            "results/confusion_matrix.csv",
            index=False
        )
    
    # Save paths for report generation
    st.session_state["metrics_file"] = (
        "results/model_metrics.json"
    )
    
    st.session_state["classification_report_file"] = (
        "results/classification_report.csv"
    )
    
    st.session_state["confusion_matrix_file"] = (
        "results/confusion_matrix.csv"
    )
    save_model(model)

    st.success(
        "✅ Model trained successfully!"
    )

# =====================================================
# DISPLAY RESULTS
# =====================================================

if "model_metrics" in st.session_state:

    metrics = st.session_state["model_metrics"]

    st.header("📊 Model Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Accuracy",
            round(metrics["Accuracy"], 3)
        )

    with col2:
        st.metric(
            "Precision",
            round(metrics["Precision"], 3)
        )

    with col3:
        st.metric(
            "Recall",
            round(metrics["Recall"], 3)
        )

    col4, col5 = st.columns(2)

    with col4:
        st.metric(
            "F1 Score",
            round(metrics["F1 Score"], 3)
        )

    with col5:

        if metrics["ROC-AUC"] is not None:

            st.metric(
                "ROC-AUC",
                round(metrics["ROC-AUC"], 3)
            )

        else:

            st.metric(
                "ROC-AUC",
                "N/A"
            )

    st.subheader("Confusion Matrix")

    st.write(
        metrics["Confusion Matrix"]
    )

    if "Classification Report" in metrics:

        st.subheader("Classification Report")

        st.dataframe(
            metrics["Classification Report"]
        )
    st.download_button(
    "📥 Download Model Metrics",
    data=json.dumps(
        metrics_to_save,
        indent=4
    ),
    file_name="model_metrics.json",
    mime="application/json"
    )

    if "Classification Report" in metrics:
    
        st.download_button(
            "📥 Download Classification Report",
            data=report_df.to_csv(),
            file_name="classification_report.csv",
            mime="text/csv"
        )
