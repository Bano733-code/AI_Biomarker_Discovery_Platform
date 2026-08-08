
import requests
import pandas as pd


# ============================================================
# MyGene.info API
# ============================================================

MYGENE_API = "https://mygene.info/v3/gene"

# ============================================================
# g:Profiler API
# ============================================================

GPROFILER_API = (
    "https://biit.cs.ut.ee/gprofiler/api/gost/profile/"
)


# ============================================================
# GET SINGLE GENE INFORMATION
# ============================================================

def get_gene_information(gene):
    """
    Retrieve gene information from MyGene.info.

    Parameters
    ----------
    gene : str
        Gene symbol, Entrez ID, Ensembl ID, or another
        supported MyGene identifier.

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
            "Summary": "No gene identifier provided.",
            "Status": "Invalid",
        }

    try:

        # ----------------------------------------------------
        # Request gene information
        # ----------------------------------------------------

        response = requests.get(
            f"{MYGENE_API}/{gene}",
            params={
                "species": "human"
            },
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "AI-Biomarker-Discovery-Platform/1.0"
                ),
            },
            timeout=20,
        )

        # ----------------------------------------------------
        # Check HTTP response
        # ----------------------------------------------------

        response.raise_for_status()

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        data = response.json()

        # ----------------------------------------------------
        # Gene not found
        # ----------------------------------------------------

        if data.get("notfound", False):

            return {
                "Gene": gene,
                "Name": "Not available",
                "Symbol": gene,
                "Summary": (
                    "Gene was not found in MyGene.info."
                ),
                "Status": "Not found",
            }

        # ----------------------------------------------------
        # Extract annotation
        # ----------------------------------------------------

        name = data.get(
            "name",
            "Not available",
        )

        symbol = data.get(
            "symbol",
            gene,
        )

        summary = data.get(
            "summary",
            "No description available.",
        )

        # ----------------------------------------------------
        # Clean None values
        # ----------------------------------------------------

        if name is None:
            name = "Not available"

        if symbol is None:
            symbol = gene

        if summary is None:
            summary = "No description available."

        return {
            "Gene": gene,
            "Name": name,
            "Symbol": symbol,
            "Summary": summary,
            "Status": "Success",
        }

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except requests.exceptions.ConnectionError:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": (
                "Could not connect to MyGene.info. "
                "Please check the internet connection."
            ),
            "Status": "Connection error",
        }

    # ========================================================
    # TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": (
                "MyGene.info request timed out."
            ),
            "Status": "Timeout",
        }

    # ========================================================
    # HTTP ERROR
    # ========================================================

    except requests.exceptions.HTTPError as e:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": (
                f"MyGene.info returned an HTTP error: {e}"
            ),
            "Status": "HTTP error",
        }

    # ========================================================
    # JSON ERROR
    # ========================================================

    except ValueError:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": (
                "MyGene.info returned an invalid response."
            ),
            "Status": "Invalid response",
        }

    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception as e:

        return {
            "Gene": gene,
            "Name": "Error",
            "Symbol": gene,
            "Summary": (
                f"Could not retrieve information: {e}"
            ),
            "Status": "Error",
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
                "Status",
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
    }

    try:

        response = requests.post(
            GPROFILER_API,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": (
                    "AI-Biomarker-Discovery-Platform/1.0"
                ),
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get(
            "result",
            []
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

        # ----------------------------------------------------
        # No enrichment results
        # ----------------------------------------------------

        if not results:

            return pd.DataFrame(
                columns=[
                    "Term",
                    "Source",
                    "P-value",
                ]
            )

        result_df = pd.DataFrame(
            results
        )

        # ----------------------------------------------------
        # Sort by P-value
        # ----------------------------------------------------

        result_df["P-value"] = pd.to_numeric(
            result_df["P-value"],
            errors="coerce",
        )

        result_df = result_df.sort_values(
            by="P-value",
            ascending=True,
        )

        return result_df.reset_index(
            drop=True
        )

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except requests.exceptions.ConnectionError:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )

    # ========================================================
    # TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )

    # ========================================================
    # HTTP ERROR
    # ========================================================

    except requests.exceptions.HTTPError:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )

    # ========================================================
    # GENERAL ERROR
    # ========================================================

    except Exception:

        return pd.DataFrame(
            columns=[
                "Term",
                "Source",
                "P-value",
            ]
        )
