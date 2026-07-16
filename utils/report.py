from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet



def generate_report(
        filename,
        dataset_info,
        metrics,
        biomarkers,
        shap_results=None
):

    """
    Generate AI Biomarker Discovery PDF Report.

    Includes:

    - Dataset information
    - ML performance
    - Biomarker ranking
    - SHAP explainability
    """



    doc = SimpleDocTemplate(
        filename
    )


    styles = getSampleStyleSheet()


    content = []



    # =================================================
    # TITLE
    # =================================================

    content.append(

        Paragraph(
            "AI Biomarker Discovery Platform Report",
            styles["Title"]
        )

    )


    content.append(
        Spacer(1,20)
    )



    # =================================================
    # DATASET SUMMARY
    # =================================================

    content.append(

        Paragraph(
            "1. Dataset Summary",
            styles["Heading2"]
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



    # =================================================
    # MACHINE LEARNING RESULTS
    # =================================================

    content.append(

        Paragraph(
            "2. Machine Learning Performance",
            styles["Heading2"]
        )

    )


    if metrics:


        for key,value in metrics.items():


            if key != "Confusion Matrix":


                content.append(

                    Paragraph(
                        f"{key}: {value}",
                        styles["BodyText"]
                    )

                )


    else:

        content.append(

            Paragraph(
                "Machine learning results not available.",
                styles["BodyText"]
            )

        )



    content.append(
        Spacer(1,20)
    )



    # =================================================
    # BIOMARKER RESULTS
    # =================================================

    content.append(

        Paragraph(
            "3. Top Biomarkers",
            styles["Heading2"]
        )

    )



    table_data = [

        [
            "Gene",
            "Score"
        ]

    ]



    for _,row in biomarkers.head(10).iterrows():


        score = None


        # support different ranking columns

        if "Final Score" in biomarkers.columns:

            score = row["Final Score"]


        elif "SHAP Importance" in biomarkers.columns:

            score = row["SHAP Importance"]


        elif "Importance" in biomarkers.columns:

            score = row["Importance"]



        table_data.append(

            [

                str(row["Gene"]),

                str(
                    round(
                        float(score),
                        3
                    )
                )

            ]

        )



    table = Table(
        table_data
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



    # =================================================
    # SHAP RESULTS
    # =================================================

    content.append(

        Paragraph(
            "4. Explainable AI (SHAP) Results",
            styles["Heading2"]
        )

    )



    if shap_results is not None:


        shap_table = [

            [

                "Gene",

                "SHAP Importance"

            ]

        ]


        for _,row in shap_results.head(10).iterrows():


            shap_table.append(

                [

                    str(row["Gene"]),

                    str(
                        round(
                            row["SHAP Importance"],
                            4
                        )
                    )

                ]

            )


        table = Table(
            shap_table
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


    else:


        content.append(

            Paragraph(
                "SHAP analysis not available.",
                styles["BodyText"]
            )

        )



    content.append(
        Spacer(1,20)
    )



    # =================================================
    # CONCLUSION
    # =================================================

    content.append(

        Paragraph(
            "5. Conclusion",
            styles["Heading2"]
        )

    )


    content.append(

        Paragraph(

            """
            This report summarizes an AI-driven biomarker discovery workflow
            including preprocessing, machine learning classification,
            feature selection, and explainable AI analysis.
            """,

            styles["BodyText"]

        )

    )



    # BUILD PDF

    doc.build(
        content
    )


    return filename
