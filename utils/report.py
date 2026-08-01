import os

import pandas as pd

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet



def add_table(content, dataframe, title, styles):

    content.append(
        Paragraph(
            title,
            styles["Heading2"]
        )
    )


    if dataframe is None:
        content.append(
            Paragraph(
                "No data available.",
                styles["BodyText"]
            )
        )

        return



    table_data = [
        list(dataframe.columns)
    ]


    for _, row in dataframe.head(10).iterrows():

        table_data.append(
            [
                str(x)
                for x in row.tolist()
            ]
        )



    table = Table(
        table_data,
        repeatRows=1
    )


    table.setStyle(

        TableStyle(

            [
                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    None
                )
            ]

        )

    )


    content.append(table)

    content.append(
        Spacer(1,20)
    )





def add_image(
        content,
        path,
        title,
        styles
):

    if os.path.exists(path):

        content.append(

            Paragraph(
                title,
                styles["Heading2"]
            )

        )


        content.append(

            Image(
                path,
                width=450,
                height=300
            )

        )


        content.append(
            Spacer(1,20)
        )





def generate_report(
        filename,
        dataset_info,
        metrics=None,
        biomarkers=None,
        shap_results=None
):


    doc = SimpleDocTemplate(
        filename
    )


    styles = getSampleStyleSheet()


    content = []



    # ==================================================
    # TITLE PAGE
    # ==================================================


    content.append(

        Paragraph(
            "AI Biomarker Discovery Platform",
            styles["Title"]
        )

    )


    content.append(

        Spacer(
            1,
            30
        )

    )


    content.append(

        Paragraph(
            """
            Automated machine learning and explainable AI
            workflow for discovering biological biomarkers
            from gene expression datasets.
            """,

            styles["BodyText"]

        )

    )


    content.append(
        Spacer(1,30)
    )



    content.append(

        Paragraph(
            "Generated Report",
            styles["Heading2"]
        )

    )


    content.append(
        PageBreak()
    )



    # ==================================================
    # DATASET SUMMARY
    # ==================================================


    content.append(

        Paragraph(
            "1. Dataset Summary",
            styles["Heading1"]
        )

    )


    for key,value in dataset_info.items():

        content.append(

            Paragraph(
                f"{key}: {value}",
                styles["BodyText"]
            )

        )


    content.append(
        Spacer(1,20)
    )



    # ==================================================
    # QUALITY CONTROL
    # ==================================================


    qc_file = (
        "results/dataset_statistics.csv"
    )


    if os.path.exists(qc_file):

        qc = pd.read_csv(
            qc_file
        )

        add_table(
            content,
            qc,
            "2. Quality Control Statistics",
            styles
        )



    # ==================================================
    # PCA
    # ==================================================


    add_image(

        content,

        "results/pca_plot.png",

        "3. Principal Component Analysis (PCA)",

        styles

    )



    # ==================================================
    # HEATMAP
    # ==================================================


    add_image(

        content,

        "results/heatmap.png",

        "4. Sample Correlation Heatmap",

        styles

    )



    # ==================================================
    # CLUSTERING
    # ==================================================


    add_image(

        content,

        "results/clustering.png",

        "5. Sample Clustering",

        styles

    )

    # ==================================================
    # DIFFERENTIAL EXPRESSION ANALYSIS
    # ==================================================


    deg_file = (
        "results/deg_results.csv"
    )


    if os.path.exists(deg_file):

        deg_results = pd.read_csv(
            deg_file
        )


        add_table(
            content,
            deg_results,
            "6. Differentially Expressed Genes (DEG)",
            styles
        )



    # ==================================================
    # FEATURE SELECTION RESULTS
    # ==================================================


    feature_file = (
        "results/selected_biomarkers.csv"
    )


    if os.path.exists(feature_file):

        feature_results = pd.read_csv(
            feature_file
        )


        add_table(
            content,
            feature_results,
            "7. Feature Selection Results",
            styles
        )



    # ==================================================
    # MACHINE LEARNING PERFORMANCE
    # ==================================================


    content.append(

        Paragraph(
            "8. Machine Learning Performance",
            styles["Heading1"]
        )

    )



    if metrics is not None:


        ml_table = [

            [
                "Metric",
                "Value"
            ]

        ]


        for key,value in metrics.items():


            if key not in [
                "Confusion Matrix",
                "Classification Report"
            ]:


                ml_table.append(

                    [

                        str(key),

                        str(value)

                    ]

                )



        table = Table(
            ml_table,
            repeatRows=1
        )


        table.setStyle(

            TableStyle(

                [

                    (
                        "GRID",
                        (0,0),
                        (-1,-1),
                        0.5,
                        None
                    )

                ]

            )

        )


        content.append(
            table
        )


        content.append(
            Spacer(1,20)
        )



    else:


        content.append(

            Paragraph(
                "Machine learning results not available.",
                styles["BodyText"]
            )

        )



    # ==================================================
    # CONFUSION MATRIX
    # ==================================================


    if metrics is not None:


        if "Confusion Matrix" in metrics:


            content.append(

                Paragraph(
                    "9. Confusion Matrix",
                    styles["Heading2"]
                )

            )


            cm = metrics[
                "Confusion Matrix"
            ]


            cm_table = [

                [
                    str(row)
                    for row in cm[0]
                ]

            ]


            for row in cm[1:]:

                cm_table.append(

                    [
                        str(x)
                        for x in row
                    ]

                )



            table = Table(
                cm_table
            )


            table.setStyle(

                TableStyle(

                    [

                        (
                            "GRID",
                            (0,0),
                            (-1,-1),
                            0.5,
                            None
                        )

                    ]

                )

            )


            content.append(
                table
            )


            content.append(
                Spacer(1,20)
            )



    # ==================================================
    # CLASSIFICATION REPORT
    # ==================================================


    if metrics is not None:


        if "Classification Report" in metrics:


            content.append(

                Paragraph(
                    "10. Classification Report",
                    styles["Heading2"]
                )

            )


            report = metrics[
                "Classification Report"
            ]


            if isinstance(
                report,
                pd.DataFrame
            ):


                add_table(

                    content,

                    report,

                    "Classification Metrics",

                    styles

                )
    
      # ==================================================
    # SHAP EXPLAINABILITY
    # ==================================================


    content.append(

        Paragraph(
            "11. SHAP Explainable AI Analysis",
            styles["Heading1"]
        )

    )


    shap_summary = (
        "results/shap_summary_plot.png"
    )


    shap_bar = (
        "results/shap_bar_plot.png"
    )


    # SHAP Summary Plot

    if os.path.exists(shap_summary):


        content.append(

            Paragraph(
                "SHAP Summary Plot",
                styles["Heading2"]
            )

        )


        content.append(

            Image(
                shap_summary,
                width=450,
                height=300
            )

        )


        content.append(
            Spacer(1,20)
        )



    # SHAP Bar Plot


    if os.path.exists(shap_bar):


        content.append(

            Paragraph(
                "SHAP Feature Importance",
                styles["Heading2"]
            )

        )


        content.append(

            Image(
                shap_bar,
                width=450,
                height=300
            )

        )


        content.append(
            Spacer(1,20)
        )



    # SHAP Importance Table


    shap_file = (
        "results/shap_importance.csv"
    )


    if os.path.exists(shap_file):


        shap_df = pd.read_csv(
            shap_file
        )


        add_table(
            content,
            shap_df.head(20),
            "Top SHAP Important Genes",
            styles
        )



    # ==================================================
    # FINAL BIOMARKER RANKING
    # ==================================================


    biomarker_file = (
        "results/final_biomarker_ranking.csv"
    )


    if os.path.exists(biomarker_file):


        biomarker_results = pd.read_csv(
            biomarker_file
        )


        add_table(

            content,

            biomarker_results.head(20),

            "12. Final Biomarker Ranking",

            styles

        )



    # ==================================================
    # BIOLOGICAL INTERPRETATION
    # ==================================================


    content.append(

        Paragraph(
            "13. Biological Interpretation",
            styles["Heading1"]
        )

    )



    # Gene annotations


    annotation_file = (
        "results/gene_annotations.csv"
    )


    if os.path.exists(annotation_file):


        annotation_df = pd.read_csv(
            annotation_file
        )


        add_table(

            content,

            annotation_df,

            "Gene Functional Annotation",

            styles

        )



    # ==================================================
    # PATHWAY ENRICHMENT
    # ==================================================


    pathway_file = (
        "results/pathway_enrichment.csv"
    )


    if os.path.exists(pathway_file):


        pathway_df = pd.read_csv(
            pathway_file
        )


        add_table(

            content,

            pathway_df,

            "GO / KEGG Pathway Enrichment",

            styles

        )



    # ==================================================
    # CONCLUSION
    # ==================================================


    content.append(

        Paragraph(
            "14. Conclusion",
            styles["Heading1"]
        )

    )


    content.append(

        Paragraph(

            """
            This automated AI biomarker discovery report summarizes
            a complete computational workflow including gene expression
            preprocessing, exploratory analysis, differential expression,
            feature selection, machine learning classification,
            explainable AI interpretation, biomarker ranking, and
            biological pathway analysis.

            The identified biomarkers represent candidate genes that
            require further experimental validation.
            """,

            styles["BodyText"]

        )

    )



    content.append(
        Spacer(1,20)
    )



    # ==================================================
    # BUILD PDF
    # ==================================================


    doc.build(
        content
    )


    return filename
