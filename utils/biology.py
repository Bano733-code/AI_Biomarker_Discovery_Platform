import requests
import pandas as pd


# ============================================================
# MyGene.info API
# ============================================================

MYGENE_QUERY_API = "https://mygene.info/v3/query"


# ============================================================
# GET SINGLE GENE INFORMATION
# ============================================================

def get_gene_information(gene):
    """
    Retrieve human gene information from MyGene.info.

    Supports:
        - Gene symbols (BRCA1, MYC, TP53)
        - Entrez IDs
        - Ensembl IDs
        - Other identifiers recognized by MyGene.info

    Parameters
    ----------
    gene : str
        Gene identifier.

    Returns
    -------
    dict
        Gene annotation information.
    """

    gene = str(gene).strip()

    # --------------------------------------------------------
    # Empty identifier
    # --------------------------------------------------------

    if not gene:
        return {
            "Gene": "",
            "Name": "Not available",
            "Symbol": "",
            "Summary": "No gene identifier provided",
        }

    # --------------------------------------------------------
    # Query MyGene.info
    # --------------------------------------------------------

    try:

        response = requests.get(
            MYGENE_QUERY_API,
            params={
                "q": gene,
                "species": "human",
                "fields": "symbol,name,summary,entrezgene,ensembl",
                "size": 5,
            },
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        hits = data.get("hits", [])

        # ----------------------------------------------------
        # No result
        # ----------------------------------------------------

        if not hits:

            return {
                "Gene": gene,
                "Name": "Not available",
                "Symbol": gene,
                "Summary": "Gene not found in MyGene.info",
            }

        # ----------------------------------------------------
        # Find best matching result
        # ----------------------------------------------------

        best_hit = None

        gene_upper = gene.upper()

        for hit in hits:

            symbol = str(
                hit.get("symbol", "")
            ).upper()

            if symbol == gene_upper:

                best_hit = hit
                break

        # If exact symbol match wasn't found,
        # use the first result.

        if best_hit is None:
            best_hit = hits[0]

        # ----------------------------------------------------
        # Extract information
        # ----------------------------------------------------

        symbol = best_hit.get(
            "symbol",
            gene,
        )

        name = best_hit.get(
            "name",
            "Not available",
        )

        summary = best_hit.get(
            "summary",
            "No description available",
        )

        # ----------------------------------------------------
        # Return annotation
        # ----------------------------------------------------

        return {
            "Gene": gene,
            "Name": name,
            "Symbol": symbol,
            "Summary": summary,
        }

    # --------------------------------------------------------
    # HTTP / connection error
    # --------------------------------------------------------

    except requests.exceptions.RequestException as e:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": f"MyGene.info request failed: {str(e)}",
        }

    # --------------------------------------------------------
    # JSON / unexpected error
    # --------------------------------------------------------

    except Exception as e:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": f"Could not retrieve information: {str(e)}",
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

    # --------------------------------------------------------
    # No genes
    # --------------------------------------------------------

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
        Human gene symbols.

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

    # --------------------------------------------------------
    # No genes
    # --------------------------------------------------------

    if not clean_genes:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )

    # --------------------------------------------------------
    # g:Profiler payload
    # --------------------------------------------------------

    payload = {
        "organism": "hsapiens",
        "query": clean_genes,
        "sources": [
            "GO:BP",
            "GO:MF",
            "GO:CC",
            "KEGG",
            "REAC",
        ],
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

        # ----------------------------------------------------
        # Parse results
        # ----------------------------------------------------

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

                    "Intersection Size": item.get(
                        "intersection_size",
                        None,
                    ),

                    "Term Size": item.get(
                        "term_size",
                        None,
                    ),

                    "Query Size": item.get(
                        "query_size",
                        None,
                    ),
                }
            )

        # ----------------------------------------------------
        # No enrichment results
        # ----------------------------------------------------

        if not results:

            return pd.DataFrame(
                columns=[
                    "Term",
                    "Source",
                    "P-value",
                    "Intersection Size",
                    "Term Size",
                    "Query Size",
                ]
            )

        return pd.DataFrame(results)

    # --------------------------------------------------------
    # Request error
    # --------------------------------------------------------

    except requests.exceptions.RequestException as e:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
                "Intersection Size",
                "Term Size",
                "Query Size",
            ]
        )

    # --------------------------------------------------------
    # Unexpected error
    # --------------------------------------------------------

    except Exception:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
                "Intersection Size",
                "Term Size",
                "Query Size",
            ]
        )
