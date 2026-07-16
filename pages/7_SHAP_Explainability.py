import streamlit as st


from utils.shap_analysis import (
    calculate_shap_values,
    get_feature_importance,
    shap_summary_plot,
    shap_bar_plot
)



st.title(
    "🔍 SHAP Explainable AI"
)



if "trained_model" not in st.session_state:

    st.warning(
        "Please train the ML model first."
    )

    st.stop()



if "processed_dataset" not in st.session_state:

    st.warning(
        "Dataset not found."
    )

    st.stop()



model = st.session_state[
    "trained_model"
]


df = st.session_state[
    "processed_dataset"
]



# Prepare data

gene_column = df.columns[0]

label_column = df.columns[-1]


X = df.drop(
    columns=[
        gene_column,
        label_column
    ]
)


X = X.T



st.subheader(
    "Dataset Used For Explanation"
)


st.write(
    X.shape
)



if st.button(
    "Generate SHAP Explanation"
):


    shap_values, explainer = calculate_shap_values(
        model,
        X
    )


    importance = get_feature_importance(
        X,
        shap_values
    )


    st.session_state[
        "shap_importance"
    ] = importance


    st.session_state[
        "shap_values"
    ] = shap_values



    st.success(
        "SHAP analysis completed!"
    )



if "shap_importance" in st.session_state:


    importance = st.session_state[
        "shap_importance"
    ]


    st.subheader(
        "Top Biomarkers by SHAP"
    )


    st.dataframe(
        importance.head(10)
    )



    st.subheader(
        "Global SHAP Importance"
    )


    fig1 = shap_bar_plot(
        st.session_state["shap_values"],
        X
    )


    st.pyplot(
        fig1
    )



    st.subheader(
        "SHAP Summary Plot"
    )


    fig2 = shap_summary_plot(
        st.session_state["shap_values"],
        X
    )


    st.pyplot(
        fig2
    )
