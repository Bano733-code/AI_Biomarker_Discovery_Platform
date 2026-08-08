from __future__ import annotations

import logging
import re
from typing import Iterable, List, Optional

import pandas as pd
import requests


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# API CONFIGURATION
# ============================================================

MYGENE_API = "https://mygene.info/v3/gene/"

MYGENE_BATCH_API = "https://mygene.info/v3/query"

GPROFILER_API = (
    "https://biit.cs.ut.ee/gprofiler/api/gost/profile/"
)

DEFAULT_TIMEOUT = 15

GPROFILER_TIMEOUT = 30


# ============================================================
# HTTP SESSION
# ============================================================

SESSION = requests.Session()

SESSION.headers.update(
    {
        "User-Agent": (
            "AI-Biomarker-Discovery-Platform/1.0 "
            "(research bioinformatics application)"
        )
    }
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _clean_identifier(value) -> str:
    """
    Convert a gene/probe identifier into a clean string.
    """

    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


def _unique_identifiers(
    genes: Iterable
) -> List[str]:
    """
    Clean and deduplicate gene identifiers while preserving order.
    """

    seen = set()

    cleaned = []

    for gene in genes:

        gene = _clean_identifier(gene)

        if not gene:
            continue

        if gene.lower() in {
            "nan",
            "none",
            "null",
            "unknown",
        }:
            continue

        if gene not in seen:

            seen.add(gene)

            cleaned.append(gene)

    return cleaned


# ============================================================
# IDENTIFIER DETECTION
# ============================================================

def detect_identifier_type(
    gene
) -> str:
    """
    Detect the approximate type of biological identifier.

    Returns one of:

        gene_symbol
        ensembl
        entrez
        affymetrix_probe
        unknown
    """

    gene = _clean_identifier(gene)

    if not gene:
        return "unknown"

    # Ensembl human gene
    if re.match(
        r"^ENSG\d+",
        gene,
        flags=re.IGNORECASE
    ):
        return "ensembl"

    # Entrez Gene ID
    if gene.isdigit():
        return "entrez"

    # Common Affymetrix probe patterns
    if re.match(
        r"^\d+_[a-z]+$",
        gene,
        flags=re.IGNORECASE
    ):
        return "affymetrix_probe"

    # Affymetrix probes can also contain suffixes
    if re.match(
        r"^\d+_at$",
        gene,
        flags=re.IGNORECASE
    ):
        return "affymetrix_probe"

    if re.match(
        r"^\d+_x_at$",
        gene,
        flags=re.IGNORECASE
    ):
        return "affymetrix_probe"

    # Otherwise treat it as a possible gene symbol.
    return "gene_symbol"


# ============================================================
# SINGLE GENE ANNOTATION
# ============================================================

def get_gene_information(
    gene
):
    """
    Retrieve biological information for a single gene/probe.

    Parameters
    ----------
    gene : str
        Gene symbol, Ensembl ID, Entrez ID, or probe ID.

    Returns
    -------
    dict
        Standardized annotation dictionary.
    """

    original_gene = _clean_identifier(gene)

    if not original_gene:

        return {
            "Gene": "",
            "Name": "Not available",
            "Symbol": "",
            "Summary": "No gene identifier provided",
            "Ensembl": "",
            "Entrez": "",
            "Identifier_Type": "unknown",
            "Status": "Invalid"
        }


    identifier_type = detect_identifier_type(
        original_gene
    )


    try:

        # ----------------------------------------------------
        # MyGene query
        # ----------------------------------------------------

        params = {
            "q": original_gene,
            "species": "human",
            "size": 1,
            "fields": (
                "symbol,name,summary,"
                "ensembl,entrezgene,"
                "type_of_gene"
            )
        }


        response = SESSION.get(
            MYGENE_BATCH_API,
            params=params,
            timeout=DEFAULT_TIMEOUT
        )


        response.raise_for_status()


        data = response.json()


        hits = data.get(
            "hits",
            []
        )


        if not hits:

            return {
                "Gene": original_gene,
                "Name": "Not available",
                "Symbol": (
                    original_gene
                    if identifier_type == "gene_symbol"
                    else "Not available"
                ),
                "Summary": (
                    "No annotation found"
                ),
                "Ensembl": "",
                "Entrez": "",
                "Identifier_Type": identifier_type,
                "Status": "Not Found"
            }


        hit = hits[0]


        # ----------------------------------------------------
        # Ensembl extraction
        # ----------------------------------------------------

        ensembl = hit.get(
            "ensembl",
            ""
        )


        if isinstance(
            ensembl,
            dict
        ):

            ensembl = ensembl.get(
                "gene",
                ""
            )


        # ----------------------------------------------------
        # Entrez extraction
        # ----------------------------------------------------

        entrez = hit.get(
            "entrezgene",
            ""
        )


        if isinstance(
            entrez,
            list
        ):

            entrez = (
                entrez[0]
                if entrez
                else ""
            )


        # ----------------------------------------------------
        # Final annotation
        # ----------------------------------------------------

        symbol = hit.get(
            "symbol",
            original_gene
        )


        name = hit.get(
            "name",
            "Not available"
        )


        summary = hit.get(
            "summary",
            "No description available"
        )


        return {

            "Gene": original_gene,

            "Name": name,

            "Symbol": symbol,

            "Summary": summary,

            "Ensembl": ensembl,

            "Entrez": entrez,

            "Identifier_Type": identifier_type,

            "Status": "Annotated"

        }


    except requests.exceptions.Timeout:

        logger.warning(
            "MyGene timeout for %s",
            original_gene
        )


        return {

            "Gene": original_gene,

            "Name": "Timeout",

            "Symbol": (
                original_gene
                if identifier_type == "gene_symbol"
                else "Not available"
            ),

            "Summary": (
                "Gene annotation request timed out"
            ),

            "Ensembl": "",

            "Entrez": "",

            "Identifier_Type": identifier_type,

            "Status": "Timeout"

        }


    except requests.exceptions.RequestException as exc:

        logger.warning(
            "MyGene request failed for %s: %s",
            original_gene,
            exc
        )


        return {

            "Gene": original_gene,

            "Name": "Unavailable",

            "Symbol": (
                original_gene
                if identifier_type == "gene_symbol"
                else "Not available"
            ),

            "Summary": (
                "Gene annotation service unavailable"
            ),

            "Ensembl": "",

            "Entrez": "",

            "Identifier_Type": identifier_type,

            "Status": "API Error"

        }


    except Exception as exc:

        logger.exception(
            "Unexpected annotation error for %s",
            original_gene
        )


        return {

            "Gene": original_gene,

            "Name": "Error",

            "Symbol": original_gene,

            "Summary": (
                "Could not retrieve gene information"
            ),

            "Ensembl": "",

            "Entrez": "",

            "Identifier_Type": identifier_type,

            "Status": "Error"

        }


# ============================================================
# BATCH GENE ANNOTATION
# ============================================================

def annotate_genes(
    genes
):
    """
    Annotate multiple genes/probes.

    The function keeps the original API:

        annotate_genes(genes)

    and returns a DataFrame.

    Parameters
    ----------
    genes : iterable
        Gene/probe identifiers.

    Returns
    -------
    pandas.DataFrame
        Gene annotation table.
    """

    identifiers = _unique_identifiers(
        genes
    )


    if not identifiers:

        return pd.DataFrame(
            columns=[
                "Gene",
                "Name",
                "Symbol",
                "Summary",
                "Ensembl",
                "Entrez",
                "Identifier_Type",
                "Status"
            ]
        )


    results = []


    # --------------------------------------------------------
    # Use MyGene batch endpoint where possible
    # --------------------------------------------------------

    try:

        response = SESSION.post(
            MYGENE_BATCH_API,
            data={
                "q": ",".join(
                    identifiers
                ),
                "species": "human",
                "size": len(
                    identifiers
                ),
                "fields": (
                    "symbol,name,summary,"
                    "ensembl,entrezgene,"
                    "type_of_gene"
                )
            },
            timeout=DEFAULT_TIMEOUT
        )


        response.raise_for_status()


        data = response.json()


        # MyGene can return a list for batch queries.
        if isinstance(
            data,
            list
        ):

            hits = data

        else:

            hits = data.get(
                "hits",
                []
            )


        # ----------------------------------------------------
        # Build lookup
        # ----------------------------------------------------

        lookup = {}


        for hit in hits:

            if not isinstance(
                hit,
                dict
            ):
                continue


            query = str(
                hit.get(
                    "query",
                    ""
                )
            ).strip()


            if query:

                lookup[
                    query
                ] = hit


        # ----------------------------------------------------
        # Reconstruct results in original order
        # ----------------------------------------------------

        for gene in identifiers:

            hit = lookup.get(
                gene
            )


            if hit is None:

                # Fall back to single-gene API
                results.append(
                    get_gene_information(
                        gene
                    )
                )

                continue


            identifier_type = detect_identifier_type(
                gene
            )


            ensembl = hit.get(
                "ensembl",
                ""
            )


            if isinstance(
                ensembl,
                dict
            ):

                ensembl = ensembl.get(
                    "gene",
                    ""
                )


            entrez = hit.get(
                "entrezgene",
                ""
            )


            if isinstance(
                entrez,
                list
            ):

                entrez = (
                    entrez[0]
                    if entrez
                    else ""
                )


            results.append({

                "Gene": gene,

                "Name": hit.get(
                    "name",
                    "Not available"
                ),

                "Symbol": hit.get(
                    "symbol",
                    gene
                ),

                "Summary": hit.get(
                    "summary",
                    "No description available"
                ),

                "Ensembl": ensembl,

                "Entrez": entrez,

                "Identifier_Type": identifier_type,

                "Status": "Annotated"

            })


    except Exception as exc:

        logger.warning(
            "Batch MyGene annotation failed: %s",
            exc
        )


        # ----------------------------------------------------
        # Safe fallback: annotate individually
        # ----------------------------------------------------

        results = [

            get_gene_information(
                gene
            )

            for gene in identifiers

        ]


    return pd.DataFrame(
        results
    )


# ============================================================
# EXTRACT GENE SYMBOLS
# ============================================================

def get_gene_symbols(
    annotation_df: pd.DataFrame
) -> List[str]:
    """
    Extract valid gene symbols from an annotation DataFrame.

    Useful before pathway enrichment.
    """

    if annotation_df is None:
        return []


    if annotation_df.empty:
        return []


    if "Symbol" not in annotation_df.columns:
        return []


    symbols = (

        annotation_df["Symbol"]

        .dropna()

        .astype(str)

        .str.strip()

    )


    invalid = {
        "",
        "nan",
        "none",
        "not available",
        "unknown"
    }


    symbols = [

        symbol

        for symbol in symbols

        if symbol.lower()
        not in invalid

    ]


    return list(
        dict.fromkeys(
            symbols
        )
    )


# ============================================================
# PATHWAY ENRICHMENT
# ============================================================

def pathway_enrichment(
    genes,
    sources: Optional[List[str]] = None,
    max_results: int = 20
):
    """
    Perform functional/pathway enrichment using g:Profiler.

    Parameters
    ----------
    genes : iterable
        Gene symbols or identifiers.

    sources : list, optional
        Sources to retain.

        Examples:
            ["GO:BP"]
            ["KEGG"]
            ["REAC"]
            ["GO:BP", "KEGG", "REAC"]

        If None, all available sources are retained.

    max_results : int
        Maximum number of results returned.

    Returns
    -------
    pandas.DataFrame

    Columns:
        Source
        Term
        P-value
        Adjusted P-value
        Description
        Term Size
        Intersection Size
    """

    genes = _unique_identifiers(
        genes
    )


    if not genes:

        return pd.DataFrame(
            columns=[
                "Source",
                "Term",
                "P-value",
                "Adjusted P-value",
                "Description",
                "Term Size",
                "Intersection Size"
            ]
        )


    # --------------------------------------------------------
    # g:Profiler request
    # --------------------------------------------------------

    payload = {

        "organism": "hsapiens",

        "query": genes,

        "sources": sources,

        "user_threshold": 0.05,

        "significance_threshold_method": "g_SCS",

        "no_evidences": False

    }


    # Remove None because some versions of g:Profiler
    # dislike null source lists.
    if sources is None:

        payload.pop(
            "sources",
            None
        )


    try:

        response = SESSION.post(

            GPROFILER_API,

            json=payload,

            timeout=GPROFILER_TIMEOUT

        )


        response.raise_for_status()


        data = response.json()


        raw_results = data.get(
            "result",
            []
        )


        results = []


        for item in raw_results:

            results.append({

                "Source": item.get(
                    "source",
                    ""
                ),

                "Term": item.get(
                    "name",
                    ""
                ),

                "P-value": item.get(
                    "p_value",
                    None
                ),

                "Adjusted P-value": item.get(
                    "p_value",
                    None
                ),

                "Description": item.get(
                    "description",
                    item.get(
                        "name",
                        ""
                    )
                ),

                "Term Size": item.get(
                    "term_size",
                    None
                ),

                "Intersection Size": item.get(
                    "intersection_size",
                    None
                )

            })


        if not results:

            return pd.DataFrame(
                columns=[
                    "Source",
                    "Term",
                    "P-value",
                    "Adjusted P-value",
                    "Description",
                    "Term Size",
                    "Intersection Size"
                ]
            )


        result_df = pd.DataFrame(
            results
        )


        # ----------------------------------------------------
        # Sort by significance
        # ----------------------------------------------------

        if "P-value" in result_df.columns:

            result_df["P-value"] = pd.to_numeric(
                result_df["P-value"],
                errors="coerce"
            )


            result_df = result_df.sort_values(
                by="P-value",
                ascending=True
            )


        # ----------------------------------------------------
        # Limit results
        # ----------------------------------------------------

        result_df = result_df.head(
            max_results
        ).reset_index(
            drop=True
        )


        return result_df


    except requests.exceptions.Timeout:

        logger.warning(
            "g:Profiler request timed out."
        )

        return pd.DataFrame()


    except requests.exceptions.RequestException as exc:

        logger.warning(
            "g:Profiler request failed: %s",
            exc
        )

        return pd.DataFrame()


    except Exception as exc:

        logger.exception(
            "Unexpected pathway enrichment error: %s",
            exc
        )

        return pd.DataFrame()


# ============================================================
# CONVENIENCE ENRICHMENT FUNCTIONS
# ============================================================

def go_enrichment(
    genes,
    max_results: int = 20
):
    """
    Gene Ontology Biological Process enrichment.
    """

    return pathway_enrichment(

        genes,

        sources=[
            "GO:BP"
        ],

        max_results=max_results

    )


def kegg_enrichment(
    genes,
    max_results: int = 20
):
    """
    KEGG pathway enrichment.
    """

    return pathway_enrichment(

        genes,

        sources=[
            "KEGG"
        ],

        max_results=max_results

    )


def reactome_enrichment(
    genes,
    max_results: int = 20
):
    """
    Reactome pathway enrichment.
    """

    return pathway_enrichment(

        genes,

        sources=[
            "REAC"
        ],

        max_results=max_results

    )


# ============================================================
# BIOLOGICAL INTERPRETATION SUMMARY
# ============================================================

def build_biological_interpretation(
    annotation_df: pd.DataFrame,
    pathway_df: Optional[pd.DataFrame] = None
) -> str:
    """
    Create a concise evidence-based biological interpretation.

    This does NOT claim that a gene is a clinically validated
    biomarker. It summarizes the computational findings.

    Returns
    -------
    str
        Human-readable interpretation.
    """

    if annotation_df is None or annotation_df.empty:

        return (
            "No gene annotations were available for biological "
            "interpretation."
        )


    annotated = annotation_df.copy()


    valid = annotated[
        annotated["Symbol"].notna()
    ]


    if valid.empty:

        return (
            "No confidently annotated genes were available."
        )


    symbols = (

        valid["Symbol"]

        .astype(str)

        .str.strip()

    )


    symbols = [

        s

        for s in symbols

        if s
        and s.lower()
        not in {
            "nan",
            "not available",
            "unknown"
        }

    ]


    if not symbols:

        return (
            "No valid gene symbols were identified."
        )


    interpretation = (

        f"The analysis identified {len(symbols)} "
        f"annotated candidate biomarker"
        f"{'s' if len(symbols) != 1 else ''}. "

    )


    interpretation += (

        "These genes were prioritized based on their "
        "importance to the machine-learning model and "
        "should be interpreted as computational candidates "
        "rather than clinically validated biomarkers. "
    )


    if pathway_df is not None and not pathway_df.empty:

        significant = pathway_df.copy()


        if "P-value" in significant.columns:

            significant["P-value"] = pd.to_numeric(
                significant["P-value"],
                errors="coerce"
            )


            significant = significant[
                significant["P-value"] <= 0.05
            ]


        if not significant.empty:

            terms = (

                significant["Term"]

                .dropna()

                .astype(str)

                .head(5)

                .tolist()

            )


            if terms:

                interpretation += (

                    "Enrichment analysis indicated biological "
                    "involvement in pathways/processes including "
                    + ", ".join(terms)
                    + ". "
                )


    interpretation += (

        "Further validation using independent datasets, "
        "statistical testing, and experimental evidence is "
        "required before these candidates can be considered "
        "validated disease biomarkers."
    )


    return interpretation


# ============================================================
# FULL BIOLOGICAL ANALYSIS
# ============================================================

def analyze_biomarkers(
    genes,
    max_pathways: int = 20
):
    """
    Run the complete biological interpretation pipeline.

    Pipeline:

        Candidate genes
             ↓
        Gene annotation
             ↓
        Gene symbols
             ↓
        Pathway enrichment
             ↓
        Interpretation

    Returns
    -------
    dict
        {
            "annotations": DataFrame,
            "pathways": DataFrame,
            "interpretation": str
        }
    """

    annotations = annotate_genes(
        genes
    )


    symbols = get_gene_symbols(
        annotations
    )


    pathways = pathway_enrichment(

        symbols,

        max_results=max_pathways

    )


    interpretation = build_biological_interpretation(

        annotations,

        pathways

    )


    return {

        "annotations": annotations,

        "pathways": pathways,

        "interpretation": interpretation

    }
```
