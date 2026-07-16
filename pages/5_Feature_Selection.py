import streamlit as st


from utils.feature_selection import (
    prepare_features,
    anova_selection,
    mutual_information_selection,
    random_forest_selection,
    combine_rankings
)



st.title(
    "🧬 Biomarker Feature Selection"
)



if "processed_dataset" not in st.session_state:

    st.warning(
        "Please complete preprocessing first."
    )

    st.stop()



df = st.session_state[
    "processed_dataset"
]



if df.shape[1] < 3:

    st.error(
        "Dataset needs gene expression values and Group labels."
    )

    st.stop()



X, y = prepare_features(df)



st.subheader(
    "Feature Selection Methods"
)



if st.button(
    "Run Feature Selection"
):


    anova = anova_selection(
        X,
        y
    )


    mi = mutual_information_selection(
        X,
        y
    )


    rf = random_forest_selection(
        X,
        y
    )


    final = combine_rankings(
        anova,
        mi,
        rf
    )


    st.session_state[
        "selected_biomarkers"
    ] = final



    st.success(
        "Feature selection completed!"
    )


    st.subheader(
        "Top Biomarkers"
    )


    st.dataframe(
        final.head(10)
    )
