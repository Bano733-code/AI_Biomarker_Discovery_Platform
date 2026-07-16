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
        annotations,
        pathways
):

    """
    Generate PDF research report.
    """


    doc = SimpleDocTemplate(
        filename
    )


    styles = getSampleStyleSheet()


    content = []


    # Title

    content.append(
        Paragraph(
            "AI Biomarker Discovery Report",
            styles["Title"]
        )
    )


    content.append(
        Spacer(1,20)
    )



    # Dataset Summary

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



    # ML Performance

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



    content.append(
        Spacer(1,20)
    )



    # Biomarkers

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


        table_data.append(

            [

                str(row["Gene"]),

                str(
                    round(
                        row["Biomarker_Score"],
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



    # Gene Annotation

    content.append(

        Paragraph(
            "4. Biological Interpretation",
            styles["Heading2"]
        )

    )


    for _,row in annotations.iterrows():

        text = (
            f"{row['Gene']} - "
            f"{row['Name']} : "
            f"{row['Summary']}"
        )


        content.append(

            Paragraph(
                text,
                styles["BodyText"]
            )

        )



    content.append(
        Spacer(1,20)
    )



    # Pathways

    content.append(

        Paragraph(
            "5. Pathway Enrichment",
            styles["Heading2"]
        )

    )


    for _,row in pathways.head(10).iterrows():

        content.append(

            Paragraph(
                f"{row['Source']} - {row['Term']} "
                f"(p={row['P-value']})",
                styles["BodyText"]
            )

        )



    doc.build(
        content
    )


    return filename
