import streamlit as st


from utils.models import (
    prepare_ml_data,
    split_data,
    train_random_forest,
    train_logistic_regression,
    evaluate_model,
    save_model
)



st.title(
    "🤖 Machine Learning Biomarker Classification"
)



if "processed_dataset" not in st.session_state:

    st.warning(
        "Please preprocess dataset first."
    )

    st.stop()



df = st.session_state[
    "processed_dataset"
]



X, y = prepare_ml_data(
    df
)



st.write(
    "Feature Matrix Shape:",
    X.shape
)



model_choice = st.selectbox(
    "Select Model",
    [
        "Random Forest",
        "Logistic Regression"
    ]
)



if st.button(
    "Train Model"
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


    st.session_state[
        "trained_model"
    ] = model



    st.session_state[
        "model_metrics"
    ] = metrics



    save_model(
        model
    )


    st.success(
        "Model trained successfully!"
    )



# Display Results

if "model_metrics" in st.session_state:


    st.subheader(
        "Model Performance"
    )


    metrics = st.session_state[
        "model_metrics"
    ]


    col1, col2, col3 = st.columns(3)


    with col1:
        st.metric(
            "Accuracy",
            round(metrics["Accuracy"],3)
        )


    with col2:
        st.metric(
            "Precision",
            round(metrics["Precision"],3)
        )


    with col3:
        st.metric(
            "F1 Score",
            round(metrics["F1 Score"],3)
        )



    st.write(
        "Recall:",
        metrics["Recall"]
    )


    st.write(
        "ROC-AUC:",
        metrics["ROC-AUC"]
    )


    st.subheader(
        "Confusion Matrix"
    )


    st.write(
        metrics["Confusion Matrix"]
    )
