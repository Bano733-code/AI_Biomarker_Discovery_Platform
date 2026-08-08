import requests
import pandas as pd


# ============================================================
# MyGene.info API
# ============================================================

MYGENE_API = "https://mygene.info/v3/gene/"


# ============================================================
# GET SINGLE GENE INFORMATION
# ============================================================

def get_gene_information(gene):
    """
    Retrieve gene information from MyGene.info.

    Parameters
    ----------
    gene : str
        Gene symbol, Entrez ID, Ensembl ID, or other
        supported MyGene identifier.

    Returns
    -------
    dict
        Gene annotation information.
    """

    gene = str(gene).strip()

    if not gene:
        return {
            "Gene": "",
            "Name": "Not available",
            "Symbol": "",
            "Summary": "No gene identifier provided",
        }

    try:

        response = requests.get(
            f"{MYGENE_API}{gene}",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        # ----------------------------------------------------
        # MyGene may return "notfound"
        # ----------------------------------------------------

        if data.get("notfound", False):

            return {
                "Gene": gene,
                "Name": "Not available",
                "Symbol": gene,
                "Summary": "Gene not found in MyGene.info",
            }

        return {
            "Gene": gene,

            "Name": data.get(
                "name",
                "Not available",
            ),

            "Symbol": data.get(
                "symbol",
                gene,
            ),

            "Summary": data.get(
                "summary",
                "No description available",
            ),
        }

    except requests.exceptions.RequestException:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": "Could not connect to MyGene.info",
        }

    except Exception:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": "Could not retrieve information",
        }


# ============================================================
# ANNOTATE MULTIPLE GENES
# ============================================================

def annotate_genes(genes):
    """
    Annotate multiple genes using MyGene.info.

    Parameters
    ----------
    genes : iterable
        Gene identifiers.

    Returns
    -------
    pandas.DataFrame
        Gene annotation table.
    """

    results = []

    # --------------------------------------------------------
    # Remove duplicates while preserving order
    # --------------------------------------------------------

    seen = set()

    for gene in genes:

        gene = str(gene).strip()

        if not gene:
            continue

        if gene in seen:
            continue

        seen.add(gene)

        results.append(
            get_gene_information(gene)
        )

    if not results:

        return pd.DataFrame(
            columns=[
                "Gene",
                "Name",
                "Symbol",
                "Summary",
            ]
        )

    return pd.DataFrame(results)


# ============================================================
# PATHWAY ENRICHMENT
# ============================================================

def pathway_enrichment(genes):
    """
    Perform pathway enrichment using g:Profiler.

    Parameters
    ----------
    genes : iterable
        List of human gene symbols.

    Returns
    -------
    pandas.DataFrame
        Enriched biological pathways.
    """

    url = (
        "https://biit.cs.ut.ee/gprofiler/api/gost/profile/"
    )

    # --------------------------------------------------------
    # Clean genes
    # --------------------------------------------------------

    clean_genes = []

    for gene in genes:

        gene = str(gene).strip()

        if gene:
            clean_genes.append(gene)

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    clean_genes = list(
        dict.fromkeys(clean_genes)
    )

    if not clean_genes:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )

    payload = {
        "organism": "hsapiens",
        "query": clean_genes,
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get(
            "result",
            [],
        )[:20]:

            results.append(
                {
                    "Term": item.get(
                        "name",
                        "Unknown",
                    ),

                    "Source": item.get(
                        "source",
                        "Unknown",
                    ),

                    "P-value": item.get(
                        "p_value",
                        None,
                    ),
                }
            )

        if not results:

            return pd.DataFrame(
                columns=[
                    "Term",
                    "Source",
                    "P-value",
                ]
            )

        return pd.DataFrame(results)

    except requests.exceptions.RequestException:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )

    except Exception:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )
