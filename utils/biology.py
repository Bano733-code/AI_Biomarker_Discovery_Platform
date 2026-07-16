import requests
import pandas as pd



MYGENE_API = (
    "https://mygene.info/v3/gene/"
)



def get_gene_information(
        gene
):

    """
    Retrieve gene information
    from MyGene.info
    """


    try:

        response = requests.get(
            f"{MYGENE_API}{gene}",
            timeout=10
        )


        data = response.json()


        result = {

            "Gene": gene,

            "Name":
                data.get(
                    "name",
                    "Not available"
                ),

            "Symbol":
                data.get(
                    "symbol",
                    gene
                ),

            "Summary":
                data.get(
                    "summary",
                    "No description available"
                )

        }


        return result


    except Exception:


        return {

            "Gene": gene,

            "Name":
                "Error",

            "Symbol":
                gene,

            "Summary":
                "Could not retrieve information"

        }




def annotate_genes(
        genes
):

    """
    Annotate multiple genes.
    """


    results = []


    for gene in genes:

        results.append(
            get_gene_information(
                gene
            )
        )


    return pd.DataFrame(
        results
    )





def pathway_enrichment(
        genes
):

    """
    Perform pathway enrichment
    using g:Profiler.
    """


    url = (
        "https://biit.cs.ut.ee/gprofiler/api/gost/profile/"
    )


    payload = {

        "organism": "hsapiens",

        "query": genes

    }


    try:

        response = requests.post(
            url,
            json=payload,
            timeout=20
        )


        data = response.json()


        results = []


        for item in data.get(
            "result",
            []
        )[:20]:


            results.append(

                {

                "Term":
                    item.get(
                        "name"
                    ),

                "Source":
                    item.get(
                        "source"
                    ),

                "P-value":
                    item.get(
                        "p_value"
                    )

                }

            )


        return pd.DataFrame(
            results
        )


    except Exception:


        return pd.DataFrame()
