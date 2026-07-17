from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    import GEOparse
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "GEOparse is required by utils.geo_downloader. "
        "Install it with: pip install GEOparse"
    ) from exc


# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Library modules should not force a global logging config; attach a
    # NullHandler so the host application controls output. The application
    # can still see these logs by configuring the root/parent logger.
    logger.addHandler(logging.NullHandler())


# --------------------------------------------------------------------------
# Custom exceptions
# --------------------------------------------------------------------------
class GeoDownloaderError(Exception):
    """Base exception for all utils.geo_downloader failures."""


class GeoDownloadError(GeoDownloaderError):
    """Raised when a GEO accession cannot be downloaded or parsed."""


class ExpressionExtractionError(GeoDownloaderError):
    """Raised when no usable expression matrix can be extracted."""


class MetadataExtractionError(GeoDownloaderError):
    """Raised when sample metadata cannot be extracted."""


# --------------------------------------------------------------------------
# Keyword banks for group detection / normalization
# --------------------------------------------------------------------------
_CONTROL_KEYWORDS = [
    "control", "ctrl", "normal", "healthy", "wildtype", "wild type",
    "wild-type", "wt", "untreated", "unaffected", "baseline", "sham",
    "vehicle", "non-tumor", "nontumor", "reference", "naive", "mock",
]

_DISEASE_KEYWORDS = [
    "disease", "diseased", "tumor", "tumour", "cancer", "carcinoma",
    "patient", "affected", "treated", "treatment", "mutant", "case",
    "knockout", "ko", "malignant", "lesion", "infection", "infected",
]

# All keywords combined, used purely for scanning/detecting which column
# is likely to encode experimental group information.
_ALL_GROUP_KEYWORDS = _CONTROL_KEYWORDS + _DISEASE_KEYWORDS

# Candidate columns (in priority order) that extract_sample_metadata()
# produces and that may plausibly encode group information.
_CANDIDATE_METADATA_COLUMNS = ["Characteristics", "Source", "Title", "Description"]

# Common gene-symbol column names found in GEO platform (GPL) annotation
# tables, checked case-insensitively as substrings.
_GENE_SYMBOL_HINTS = ["gene symbol", "gene_symbol", "symbol", "gene name", "gene_assignment"]


# --------------------------------------------------------------------------
# 1. Download
# --------------------------------------------------------------------------
def download_geo_dataset(accession: str, cache_dir: str = "data/geo_cache") -> Any:
    """
    Download (or load from cache) a GEO accession using GEOparse.

    Parameters
    ----------
    accession : str
        A GEO accession, e.g. "GSE12345".
    cache_dir : str
        Directory used to cache downloaded GEO files. Created if missing.

    Returns
    -------
    GEOparse GEO object (e.g. a GSE instance).

    Raises
    ------
    GeoDownloadError
        If the accession is invalid, the download fails, or the file
        cannot be parsed.
    """
    if not accession or not isinstance(accession, str):
        raise GeoDownloadError(f"Invalid GEO accession: {accession!r}")

    accession = accession.strip().upper()
    if not accession.startswith(("GSE", "GDS", "GPL", "GSM")):
        raise GeoDownloadError(
            f"Unsupported accession format: '{accession}'. "
            "Expected an accession starting with GSE, GDS, GPL, or GSM."
        )

    cache_path = Path(cache_dir)
    try:
        cache_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise GeoDownloadError(
            f"Could not create cache directory '{cache_dir}': {exc}"
        ) from exc

    already_cached = any(cache_path.glob(f"{accession}*"))
    if already_cached:
        logger.info("Loading cache: found existing files for %s in %s", accession, cache_dir)
    else:
        logger.info("Downloading: %s -> %s", accession, cache_dir)

    try:
        gse = GEOparse.get_GEO(geo=accession, destdir=str(cache_path), silent=True,how="full")
    except Exception as exc:
        raise GeoDownloadError(
            f"Failed to download/parse GEO accession '{accession}': {exc}"
        ) from exc

    if gse is None:
        raise GeoDownloadError(f"GEOparse returned no data for accession '{accession}'.")

    n_samples = len(getattr(gse, "gsms", {}) or {})
    if n_samples == 0:
        raise GeoDownloadError(
            f"Accession '{accession}' was downloaded but contains no samples "
            "(possibly a corrupt or empty GEO file)."
        )

    logger.info("Downloaded %s: %d sample(s).", accession, n_samples)
    return gse


# --------------------------------------------------------------------------
# 2. Expression matrix
# --------------------------------------------------------------------------
def _build_probe_to_gene_map(gse: Any) -> Dict[str, str]:
    """
    Attempt to map probe/feature IDs to gene symbols using the platform
    (GPL) annotation table attached to the GEO object. Returns an empty
    dict if no usable annotation is found (never raises).
    """
    probe_to_gene: Dict[str, str] = {}
    gpls = getattr(gse, "gpls", None) or {}

    for _, gpl in gpls.items():
        table = getattr(gpl, "table", None)
        if table is None or table.empty or "ID" not in table.columns:
            continue

        symbol_col = None
        for col in table.columns:
            col_lower = str(col).lower()
            if any(hint in col_lower for hint in _GENE_SYMBOL_HINTS):
                symbol_col = col
                break

        if symbol_col is None:
            continue

        sub = table[["ID", symbol_col]].dropna()
        for probe_id, gene_symbol in zip(sub["ID"], sub[symbol_col]):
            gene_symbol = str(gene_symbol).strip()
            # Some annotation columns pack multiple symbols separated by
            # '///' (Affymetrix style) — keep only the first.
            gene_symbol = gene_symbol.split("///")[0].strip()
            if gene_symbol and gene_symbol.lower() not in ("nan", "none", ""):
                probe_to_gene[str(probe_id)] = gene_symbol

    return probe_to_gene


def _detect_expression_table(gse: Any) -> pd.DataFrame:
    """
    Fallback path used when gse.pivot_samples("VALUE") is unavailable or
    empty. Manually scans each sample's table for a numeric "VALUE"-like
    column and assembles a probes x samples matrix.
    """
    frames = []
    for gsm_name, gsm in getattr(gse, "gsms", {}).items():
        table = getattr(gsm, "table", None)
        if table is None or table.empty:
            continue

        value_col = None
        for candidate in ("VALUE", "value", "Value"):
            if candidate in table.columns:
                value_col = candidate
                break
        if value_col is None:
            # Try the first numeric non-ID column as a last resort.
            numeric_cols = [
                c for c in table.columns
                if c not in ("ID_REF", "ID") and pd.api.types.is_numeric_dtype(table[c])
            ]
            if numeric_cols:
                value_col = numeric_cols[0]

        id_col = "ID_REF" if "ID_REF" in table.columns else table.columns[0]
        if value_col is None:
            continue

        series = table.set_index(id_col)[value_col]
        series.name = gsm_name
        frames.append(series)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, axis=1)


def extract_expression_matrix(gse: Any) -> pd.DataFrame:
    """
    Extract a gene-expression matrix from a GEOparse GEO object.

    Returns
    -------
    pd.DataFrame
        Columns: ["Gene", <Sample1>, <Sample2>, ...]. Probe IDs are mapped
        to gene symbols when platform annotation is available; otherwise
        the original probe/feature ID is used as the gene identifier.
        Rows with no usable gene identifier are dropped, and duplicate
        genes are collapsed by averaging their expression values.

    Raises
    ------
    ExpressionExtractionError
        If no expression data could be extracted at all.
    """
    logger.info("Extracting expression matrix...")

    raw: pd.DataFrame
    try:
        raw = gse.pivot_samples("VALUE")
    except Exception as exc:
        logger.warning("pivot_samples('VALUE') failed (%s); trying fallback detection.", exc)
        raw = pd.DataFrame()

    if raw is None or raw.empty:
        logger.info("Standard VALUE pivot unavailable/empty; scanning sample tables directly.")
        raw = _detect_expression_table(gse)

    if raw is None or raw.empty:
        raise ExpressionExtractionError(
            "No expression matrix could be extracted from this GEO object. "
            "This series may only provide raw/supplementary files "
            "(e.g. RNA-seq counts) rather than a series-matrix VALUE table."
        )

    raw.index = raw.index.astype(str)
    raw = raw[~raw.index.isna()]
    raw = raw[raw.index.str.strip() != ""]

    probe_to_gene = _build_probe_to_gene_map(gse)
    if probe_to_gene:
        gene_index = raw.index.map(lambda pid: probe_to_gene.get(pid, pid))
        n_mapped = sum(1 for pid in raw.index if pid in probe_to_gene)
        logger.info(
            "Mapped %d/%d probes to gene symbols using platform annotation.",
            n_mapped, len(raw.index),
        )
    else:
        gene_index = raw.index
        logger.info("No platform gene-symbol annotation found; using original feature IDs.")

    expr_df = raw.copy()
    expr_df.insert(0, "Gene", gene_index)

    # Drop rows with no usable gene identifier.
    before = len(expr_df)
    expr_df = expr_df[expr_df["Gene"].notna()]
    expr_df = expr_df[expr_df["Gene"].astype(str).str.strip() != ""]
    dropped = before - len(expr_df)
    if dropped:
        logger.info("Dropped %d row(s) with no gene identifier.", dropped)

    # Collapse duplicate genes by averaging expression across probes.
    n_unique = expr_df["Gene"].nunique()
    if n_unique < len(expr_df):
        logger.info(
            "Collapsing %d duplicate gene rows into %d unique genes (mean aggregation).",
            len(expr_df) - n_unique, n_unique,
        )
        expr_df = expr_df.groupby("Gene", as_index=False).mean(numeric_only=True)

    expr_df = expr_df.reset_index(drop=True)
    logger.info(
        "Expression matrix ready: %d genes x %d samples.",
        expr_df.shape[0], expr_df.shape[1] - 1,
    )
    return expr_df


# --------------------------------------------------------------------------
# 3. Sample metadata
# --------------------------------------------------------------------------
def _flatten(value: Any) -> str:
    """Flatten a GEOparse metadata value (often a list of strings) into a single string."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "; ".join(str(v).strip() for v in value if str(v).strip())
    return str(value).strip()


def extract_sample_metadata(gse: Any) -> pd.DataFrame:
    """
    Extract per-sample metadata from a GEOparse GEO object.

    Returns
    -------
    pd.DataFrame
        Columns: ["Sample", "Title", "Source", "Characteristics",
                  "Description", "Metadata"].
        "Metadata" holds the full flattened metadata dict for each sample
        (useful as an escape hatch for fields not otherwise surfaced).

    Raises
    ------
    MetadataExtractionError
        If no samples with metadata could be found.
    """
    logger.info("Extracting sample metadata...")

    gsms = getattr(gse, "gsms", {}) or {}
    if not gsms:
        raise MetadataExtractionError("GEO object has no samples (gsms) to extract metadata from.")

    rows: List[Dict[str, Any]] = []
    for sample_id, gsm in gsms.items():
        meta = getattr(gsm, "metadata", {}) or {}

        flattened_all = {key: _flatten(val) for key, val in meta.items()}

        title = flattened_all.get("title", "")
        source = flattened_all.get("source_name_ch1", "")
        description = flattened_all.get("description", "")

        characteristics_list = meta.get("characteristics_ch1", []) or []
        characteristics = "; ".join(str(c).strip() for c in characteristics_list if str(c).strip())

        rows.append({
            "Sample": sample_id,
            "Title": title,
            "Source": source,
            "Characteristics": characteristics,
            "Description": description,
            "Metadata": flattened_all,
        })

    metadata_df = pd.DataFrame(rows)
    logger.info("Extracted metadata for %d sample(s).", len(metadata_df))
    return metadata_df


# --------------------------------------------------------------------------
# 4. Group column detection
# --------------------------------------------------------------------------
def _values_only(text: str) -> str:
    """
    GEO characteristics strings look like "disease state: tumor; tissue: liver".
    Field *names* (e.g. "disease state") can themselves contain group
    keywords and cause false positives if matched against the raw string.
    This extracts just the value portions ("tumor", "liver") for matching.
    Falls back to the original text if no "key: value" structure is found.
    """
    parts = [p.strip() for p in text.split(";") if p.strip()]
    if not parts:
        return text

    values = []
    found_structure = False
    for part in parts:
        if ":" in part:
            _, value = part.split(":", 1)
            values.append(value.strip())
            found_structure = True
        else:
            values.append(part)

    return " ".join(values) if found_structure else text


def _keyword_hit_count(text: str) -> int:
    text_lower = _values_only(text).lower()
    return sum(1 for kw in _ALL_GROUP_KEYWORDS if kw in text_lower)


def detect_group_column(metadata_df: pd.DataFrame) -> Optional[str]:
    """
    Scan metadata_df's descriptive columns to find the one most likely to
    encode experimental group / condition information (control vs. disease,
    treated vs. untreated, etc.).

    Returns
    -------
    str or None
        The name of the best-matching column, or None if nothing
        confidently matched.
    """
    logger.info("Detecting group column...")

    best_col: Optional[str] = None
    best_score = 0.0

    candidates = [c for c in _CANDIDATE_METADATA_COLUMNS if c in metadata_df.columns]

    for col in candidates:
        values = metadata_df[col].dropna().astype(str)
        if values.empty:
            continue

        n_hits = sum(1 for v in values if _keyword_hit_count(v) > 0)
        if n_hits == 0:
            continue

        # Distinguish control-like vs disease-like matches to reward columns
        # that actually separate samples into (at least) two groups.
        has_control = any(
            any(kw in _values_only(v).lower() for kw in _CONTROL_KEYWORDS) for v in values
        )
        has_disease = any(
            any(kw in _values_only(v).lower() for kw in _DISEASE_KEYWORDS) for v in values
        )
        coverage = n_hits / len(values)
        score = coverage + (0.5 if (has_control and has_disease) else 0.0)

        if score > best_score:
            best_score = score
            best_col = col

    if best_col:
        logger.info("Detected group column: '%s' (score=%.2f).", best_col, best_score)
    else:
        logger.info("Could not confidently detect a group column.")

    return best_col


# --------------------------------------------------------------------------
# 5. Group label normalization
# --------------------------------------------------------------------------
def _normalize_label(raw_value: str) -> Optional[str]:
    """Map a raw metadata string to a normalized 'Control' / 'Disease' label."""
    lower = _values_only(raw_value).lower()
    is_control = any(kw in lower for kw in _CONTROL_KEYWORDS)
    is_disease = any(kw in lower for kw in _DISEASE_KEYWORDS)

    if is_control and not is_disease:
        return "Control"
    if is_disease and not is_control:
        return "Disease"
    return None  # ambiguous or no keyword match


def create_group_labels(
    metadata_df: pd.DataFrame,
    group_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Produce a clean two-column DataFrame of experimental group labels.

    Parameters
    ----------
    metadata_df : pd.DataFrame
        Output of extract_sample_metadata().
    group_column : str, optional
        Metadata column to use for grouping. If omitted, detect_group_column()
        is used to find one automatically.

    Returns
    -------
    pd.DataFrame
        Columns: ["Sample", "Group"]. Values are normalized to "Control" /
        "Disease" where a confident keyword match is found; otherwise the
        original raw value is kept as-is. This function never raises —
        if grouping cannot be determined at all, "Group" is filled with
        "Unknown".
    """
    if "Sample" not in metadata_df.columns:
        logger.warning("metadata_df has no 'Sample' column; cannot create group labels.")
        return pd.DataFrame(columns=["Sample", "Group"])

    if group_column is None:
        group_column = detect_group_column(metadata_df)

    if group_column is None or group_column not in metadata_df.columns:
        logger.warning(
            "No usable group column (requested=%r); all samples will be labeled 'Unknown'.",
            group_column,
        )
        return pd.DataFrame({
            "Sample": metadata_df["Sample"],
            "Group": "Unknown",
        })

    labels = []
    for raw_value in metadata_df[group_column].fillna(""):
        raw_value = str(raw_value)
        normalized = _normalize_label(raw_value)
        if normalized is not None:
            labels.append(normalized)
        elif raw_value.strip():
            labels.append(raw_value.strip())  # keep original value, never crash
        else:
            labels.append("Unknown")

    result = pd.DataFrame({"Sample": metadata_df["Sample"], "Group": labels})
    logger.info(
        "Group labels created from column '%s': %s",
        group_column, result["Group"].value_counts(dropna=False).to_dict(),
    )
    return result


# --------------------------------------------------------------------------
# 6. Validation
# --------------------------------------------------------------------------
def validate_dataset(
    expression_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Cross-check expression_df and metadata_df for consistency.

    Returns
    -------
    dict
        {
          "is_valid": bool,
          "n_genes": int,
          "n_samples_expression": int,
          "n_samples_metadata": int,
          "missing_metadata_for_samples": [...],  # in expression, not in metadata
          "missing_expression_for_samples": [...],  # in metadata, not in expression
          "duplicate_samples": [...],
          "duplicate_genes": [...],
        }
    """
    logger.info("Validating dataset...")

    report: Dict[str, Any] = {
        "is_valid": True,
        "n_genes": 0,
        "n_samples_expression": 0,
        "n_samples_metadata": 0,
        "missing_metadata_for_samples": [],
        "missing_expression_for_samples": [],
        "duplicate_samples": [],
        "duplicate_genes": [],
    }

    if expression_df is None or expression_df.empty or "Gene" not in expression_df.columns:
        report["is_valid"] = False
        report["error"] = "expression_df is empty or missing a 'Gene' column."
        logger.error(report["error"])
        return report

    expression_samples = [c for c in expression_df.columns if c != "Gene"]
    metadata_samples = list(metadata_df["Sample"]) if "Sample" in metadata_df.columns else []

    report["n_genes"] = int(expression_df["Gene"].shape[0])
    report["n_samples_expression"] = len(expression_samples)
    report["n_samples_metadata"] = len(metadata_samples)

    expr_set = set(expression_samples)
    meta_set = set(metadata_samples)

    missing_metadata = sorted(expr_set - meta_set)
    missing_expression = sorted(meta_set - expr_set)

    duplicate_samples = sorted({
        s for s in metadata_samples if metadata_samples.count(s) > 1
    })
    duplicate_genes = sorted({
        g for g in expression_df["Gene"] if list(expression_df["Gene"]).count(g) > 1
    })

    report["missing_metadata_for_samples"] = missing_metadata
    report["missing_expression_for_samples"] = missing_expression
    report["duplicate_samples"] = duplicate_samples
    report["duplicate_genes"] = duplicate_genes

    if missing_metadata or duplicate_samples or duplicate_genes:
        report["is_valid"] = False

    if report["is_valid"]:
        logger.info("Validation passed: %d genes, %d samples.",
                    report["n_genes"], report["n_samples_expression"])
    else:
        logger.warning("Validation found issues: %s", {
            k: v for k, v in report.items()
            if k in ("missing_metadata_for_samples", "missing_expression_for_samples",
                      "duplicate_samples", "duplicate_genes")
        })

    return report


# --------------------------------------------------------------------------
# 7. Main API
# --------------------------------------------------------------------------
def load_geo_dataset(
    accession: str,
    group_column: Optional[str] = None,
    cache_dir: str = "data/geo_cache",
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Main entry point: download a GEO accession and return everything the
    application needs to run biomarker discovery.

    Parameters
    ----------
    accession : str
        GEO accession, e.g. "GSE12345".
    group_column : str, optional
        Metadata column to use for experimental grouping. If omitted,
        grouping is detected automatically.
    cache_dir : str
        Directory for caching downloaded GEO files.

    Returns
    -------
    (expression_df, metadata_df, validation_report)
        expression_df : Gene | Sample1 | Sample2 | ...
        metadata_df   : Sample | Group
        validation_report : dict, see validate_dataset().

    Raises
    ------
    GeoDownloadError, ExpressionExtractionError, MetadataExtractionError
        Propagated from the underlying steps with descriptive messages.
    """
    gse = download_geo_dataset(accession, cache_dir=cache_dir)
    expression_df = extract_expression_matrix(gse)
    raw_metadata_df = extract_sample_metadata(gse)
    metadata_df = create_group_labels(raw_metadata_df, group_column=group_column)
    validation_report = validate_dataset(expression_df, metadata_df)

    logger.info(
        "load_geo_dataset('%s') complete: %d genes, %d samples, valid=%s.",
        accession, validation_report.get("n_genes", 0),
        validation_report.get("n_samples_expression", 0),
        validation_report.get("is_valid"),
    )
    return expression_df, metadata_df, validation_report
