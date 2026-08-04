import streamlit as st
import os
import json
import pandas as pd
from utils.models import (
    split_data,
    train_random_forest,
    train_logistic_regression,
    evaluate_model,
    save_model
) 

from utils.feature_selection import (
    prepare_features,
    run_feature_selection_pipeline
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

X, y = prepare_features(
    expression_df,
    metadata_df
)
X, biomarkers = run_feature_selection_pipeline(

    X,

    y,

    top_genes=100

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
    # Save model
    save_model(model)
    
    # Save session state
    st.session_state["trained_model"] = model
    st.session_state["model_metrics"] = metrics
    
    # Save metrics to JSON
    metrics_json = {}
    
    for key, value in metrics.items():
    
        if key not in [
            "Classification Report",
            "Confusion Matrix"
        ]:
    
            metrics_json[key] = value
    
    with open(
        "results/model_metrics.json",
        "w"
    ) as f:
    
        json.dump(
            metrics_json,
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
    
        cm_df = pd.DataFrame(
            metrics["Confusion Matrix"]
        )
    
        cm_df.to_csv(
            "results/confusion_matrix.csv",
            index=False
        )
    
    # Save file paths
    st.session_state["metrics_file"] = "results/model_metrics.json"
    st.session_state["classification_report_file"] = "results/classification_report.csv"
    st.session_state["confusion_matrix_file"] = "results/confusion_matrix.csv"

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
    
        # Create dataframe again for display + download
        report_df = pd.DataFrame(
            metrics["Classification Report"]
        ).transpose()
    
    
        st.dataframe(
            report_df
        )
    
    
        # Ensure results folder exists
        os.makedirs(
            "results",
            exist_ok=True
        )
    
    
        # Save button for report generator
        if st.button(
            "💾 Save Classification Report",
            use_container_width=True
        ):
    
            report_df.to_csv(
                "results/classification_report.csv",
                index=True
            )
    
            st.success(
                "Classification report saved for PDF report generation."
            )
    
    
        # Download button
        st.download_button(
            "📥 Download Classification Report",
            data=report_df.to_csv(),
            file_name="classification_report.csv",
            mime="text/csv"
        )
