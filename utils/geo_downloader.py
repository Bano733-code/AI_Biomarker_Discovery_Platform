from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    import GEOparse
except ImportError as exc:
    raise ImportError(
        "GEOparse is required. Install it with: pip install GEOparse"
    ) from exc


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)

if not logger.handlers:
    logger.addHandler(logging.NullHandler())


# ============================================================
# CUSTOM EXCEPTIONS
# ============================================================

class GeoDownloaderError(Exception):
    """Base exception for GEO downloader."""


class GeoDownloadError(GeoDownloaderError):
    """GEO accession download or parsing failed."""


class ExpressionExtractionError(GeoDownloaderError):
    """Expression matrix extraction failed."""


class MetadataExtractionError(GeoDownloaderError):
    """Metadata extraction failed."""


# ============================================================
# GROUP KEYWORDS
# ============================================================

CONTROL_KEYWORDS = [
    "control",
    "ctrl",
    "normal",
    "healthy",
    "wildtype",
    "wild type",
    "wild-type",
    "wt",
    "untreated",
    "unaffected",
    "baseline",
    "sham",
    "vehicle",
    "non-tumor",
    "nontumor",
    "reference",
    "naive",
    "mock",
]

DISEASE_KEYWORDS = [
    "disease",
    "diseased",
    "tumor",
    "tumour",
    "cancer",
    "carcinoma",
    "patient",
    "affected",
    "treated",
    "treatment",
    "mutant",
    "case",
    "knockout",
    "ko",
    "malignant",
    "lesion",
    "infection",
    "infected",
]

ALL_GROUP_KEYWORDS = CONTROL_KEYWORDS + DISEASE_KEYWORDS


# ============================================================
# METADATA COLUMNS
# ============================================================

CANDIDATE_METADATA_COLUMNS = [
    "Characteristics",
    "Source",
    "Title",
    "Description",
]


# ============================================================
# GENE SYMBOL ANNOTATION HINTS
# ============================================================

GENE_SYMBOL_HINTS = [
    "gene symbol",
    "gene_symbol",
    "symbol",
    "gene name",
    "gene_assignment",
]


# ============================================================
# 1. VALIDATE GEO ACCESSION
# ============================================================

def validate_geo_accession(accession: str) -> str:
    """
    Validate and normalize a GEO Series accession.

    The platform expects GSE accessions such as:

        GSE113994
        GSE176078
        GSE12345

    Returns
    -------
    str
        Normalized accession.

    Raises
    ------
    GeoDownloadError
        If accession is invalid.
    """

    if accession is None:
        raise GeoDownloadError(
            "GEO accession cannot be empty."
        )

    accession = str(accession).strip().upper()

    if not accession:
        raise GeoDownloadError(
            "GEO accession cannot be empty."
        )

    # Only GSE datasets are accepted by this platform.
    if not re.fullmatch(r"GSE\d+", accession):
        raise GeoDownloadError(
            f"Invalid GEO accession '{accession}'. "
            "Please enter a GEO Series accession such as GSE176078."
        )

    return accession


# ============================================================
# 2. DOWNLOAD GEO DATASET
# ============================================================

def download_geo_dataset(
    accession: str,
    cache_dir: str = "data/geo_cache",
) -> Any:
    """
    Download a GEO Series dataset using GEOparse.

    Cached datasets are reused automatically.
    """

    accession = validate_geo_accession(accession)

    cache_path = Path(cache_dir)

    try:
        cache_path.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as exc:

        raise GeoDownloadError(
            f"Could not create GEO cache directory: {exc}"
        ) from exc

    logger.info(
        "Downloading GEO dataset: %s",
        accession,
    )

    try:

        gse = GEOparse.get_GEO(
            geo=accession,
            destdir=str(cache_path),
            silent=True,
            how="full",
        )

    except Exception as exc:

        raise GeoDownloadError(
            f"Failed to download GEO dataset '{accession}': {exc}"
        ) from exc

    if gse is None:

        raise GeoDownloadError(
            f"GEOparse returned no data for '{accession}'."
        )

    gsms = getattr(
        gse,
        "gsms",
        {},
    ) or {}

    if len(gsms) == 0:

        raise GeoDownloadError(
            f"GEO dataset '{accession}' contains no samples."
        )

    logger.info(
        "%s downloaded successfully: %d samples.",
        accession,
        len(gsms),
    )

    return gse


# ============================================================
# 3. BUILD PROBE → GENE SYMBOL MAP
# ============================================================

def _build_probe_to_gene_map(
    gse: Any,
) -> Dict[str, str]:

    probe_to_gene: Dict[str, str] = {}

    gpls = getattr(
        gse,
        "gpls",
        {},
    ) or {}

    for _, gpl in gpls.items():

        table = getattr(
            gpl,
            "table",
            None,
        )

        if table is None:
            continue

        if table.empty:
            continue

        if "ID" not in table.columns:
            continue

        symbol_column = None

        for column in table.columns:

            column_lower = str(column).lower()

            if any(
                hint in column_lower
                for hint in GENE_SYMBOL_HINTS
            ):
                symbol_column = column
                break

        if symbol_column is None:
            continue

        subset = table[
            ["ID", symbol_column]
        ].dropna()

        for probe_id, gene_symbol in zip(
            subset["ID"],
            subset[symbol_column],
        ):

            gene_symbol = str(
                gene_symbol
            ).strip()

            # Affymetrix-style annotation
            if "///" in gene_symbol:
                gene_symbol = gene_symbol.split(
                    "///"
                )[0].strip()

            if not gene_symbol:
                continue

            if gene_symbol.lower() in {
                "nan",
                "none",
                "---",
            }:
                continue

            probe_to_gene[
                str(probe_id)
            ] = gene_symbol

    logger.info(
        "Probe-to-gene mappings found: %d",
        len(probe_to_gene),
    )

    return probe_to_gene


# ============================================================
# 4. FALLBACK EXPRESSION EXTRACTION
# ============================================================

def _detect_expression_table(
    gse: Any,
) -> pd.DataFrame:

    frames = []

    gsms = getattr(
        gse,
        "gsms",
        {},
    ) or {}

    for gsm_name, gsm in gsms.items():

        table = getattr(
            gsm,
            "table",
            None,
        )

        if table is None or table.empty:
            continue

        value_column = None

        # Standard GEO expression column
        for candidate in [
            "VALUE",
            "value",
            "Value",
        ]:

            if candidate in table.columns:

                value_column = candidate
                break

        # Fallback: find numeric column
        if value_column is None:

            numeric_columns = [
                column
                for column in table.columns
                if column not in [
                    "ID",
                    "ID_REF",
                ]
                and pd.api.types.is_numeric_dtype(
                    table[column]
                )
            ]

            if numeric_columns:
                value_column = numeric_columns[0]

        if value_column is None:
            continue

        if "ID_REF" in table.columns:
            id_column = "ID_REF"
        elif "ID" in table.columns:
            id_column = "ID"
        else:
            id_column = table.columns[0]

        series = table.set_index(
            id_column
        )[value_column]

        series.name = gsm_name

        frames.append(series)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        axis=1,
    )


# ============================================================
# 5. EXTRACT EXPRESSION MATRIX
# ============================================================

def extract_expression_matrix(
    gse: Any,
) -> pd.DataFrame:
    """
    Extract expression matrix from GEO.

    Output format:

        Gene | GSM1 | GSM2 | GSM3 | ...

    Probe IDs are mapped to gene symbols whenever
    GPL annotation is available.
    """

    logger.info(
        "Extracting expression matrix..."
    )

    # --------------------------------------------------------
    # Try standard GEOparse VALUE matrix
    # --------------------------------------------------------

    try:

        raw = gse.pivot_samples(
            "VALUE"
        )

    except Exception as exc:

        logger.warning(
            "pivot_samples failed: %s",
            exc,
        )

        raw = pd.DataFrame()

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if raw is None or raw.empty:

        logger.info(
            "Using fallback expression extraction."
        )

        raw = _detect_expression_table(
            gse
        )

    # --------------------------------------------------------
    # Check
    # --------------------------------------------------------

    if raw is None or raw.empty:

        raise ExpressionExtractionError(
            "No expression matrix could be extracted from this GEO dataset. "
            "This GSE may provide only raw/supplementary files rather than "
            "a GEO series matrix with VALUE measurements."
        )

    # --------------------------------------------------------
    # Clean feature IDs
    # --------------------------------------------------------

    raw.index = raw.index.astype(str)

    raw = raw[
        raw.index.str.strip() != ""
    ]

    # --------------------------------------------------------
    # Probe → gene mapping
    # --------------------------------------------------------

    probe_to_gene = (
        _build_probe_to_gene_map(gse)
    )

    if probe_to_gene:

        gene_index = raw.index.map(
            lambda probe:
                probe_to_gene.get(
                    probe,
                    probe,
                )
        )

        mapped_count = sum(
            1
            for probe in raw.index
            if probe in probe_to_gene
        )

        logger.info(
            "Mapped %d/%d features to gene symbols.",
            mapped_count,
            len(raw.index),
        )

    else:

        gene_index = raw.index

        logger.warning(
            "No GPL gene-symbol annotation found. "
            "Using original feature IDs."
        )

    # --------------------------------------------------------
    # Create expression dataframe
    # --------------------------------------------------------

    expression_df = raw.copy()

    expression_df.insert(
        0,
        "Gene",
        gene_index,
    )

    # --------------------------------------------------------
    # Remove invalid genes
    # --------------------------------------------------------

    expression_df = expression_df[
        expression_df["Gene"].notna()
    ]

    expression_df = expression_df[
        expression_df["Gene"].astype(str).str.strip() != ""
    ]

    # --------------------------------------------------------
    # Convert expression columns to numeric
    # --------------------------------------------------------

    sample_columns = [
        column
        for column in expression_df.columns
        if column != "Gene"
    ]

    for column in sample_columns:

        expression_df[column] = pd.to_numeric(
            expression_df[column],
            errors="coerce",
        )

    # --------------------------------------------------------
    # Remove completely empty genes
    # --------------------------------------------------------

    expression_df = expression_df.dropna(
        subset=sample_columns,
        how="all",
    )

    # --------------------------------------------------------
    # Collapse duplicate genes
    # --------------------------------------------------------

    if expression_df["Gene"].duplicated().any():

        logger.info(
            "Duplicate genes detected. "
            "Collapsing duplicate probes using mean expression."
        )

        expression_df = (
            expression_df
            .groupby(
                "Gene",
                as_index=False,
            )
            .mean(
                numeric_only=True
            )
        )

    expression_df = expression_df.reset_index(
        drop=True
    )

    logger.info(
        "Expression matrix ready: %d genes x %d samples.",
        expression_df.shape[0],
        expression_df.shape[1] - 1,
    )

    return expression_df


# ============================================================
# 6. FLATTEN GEO METADATA
# ============================================================

def _flatten(value: Any) -> str:

    if value is None:
        return ""

    if isinstance(
        value,
        (list, tuple),
    ):

        return "; ".join(
            str(v).strip()
            for v in value
            if str(v).strip()
        )

    return str(value).strip()


# ============================================================
# 7. EXTRACT SAMPLE METADATA
# ============================================================

def extract_sample_metadata(
    gse: Any,
) -> pd.DataFrame:

    logger.info(
        "Extracting sample metadata..."
    )

    gsms = getattr(
        gse,
        "gsms",
        {},
    ) or {}

    if not gsms:

        raise MetadataExtractionError(
            "No GSM samples were found in this GEO dataset."
        )

    rows = []

    for sample_id, gsm in gsms.items():

        metadata = getattr(
            gsm,
            "metadata",
            {},
        ) or {}

        flattened_metadata = {
            key: _flatten(value)
            for key, value in metadata.items()
        }

        title = flattened_metadata.get(
            "title",
            "",
        )

        source = flattened_metadata.get(
            "source_name_ch1",
            "",
        )

        description = flattened_metadata.get(
            "description",
            "",
        )

        characteristics = _flatten(
            metadata.get(
                "characteristics_ch1",
                [],
            )
        )

        rows.append(
            {
                "Sample": sample_id,
                "Title": title,
                "Source": source,
                "Characteristics": characteristics,
                "Description": description,
                "Metadata": flattened_metadata,
            }
        )

    metadata_df = pd.DataFrame(
        rows
    )

    logger.info(
        "Metadata extracted for %d samples.",
        len(metadata_df),
    )

    return metadata_df


# ============================================================
# 8. REMOVE METADATA FIELD NAMES
# ============================================================

def _values_only(
    text: str,
) -> str:

    parts = [
        part.strip()
        for part in text.split(";")
        if part.strip()
    ]

    if not parts:
        return text

    values = []

    found_structure = False

    for part in parts:

        if ":" in part:

            _, value = part.split(
                ":",
                1,
            )

            values.append(
                value.strip()
            )

            found_structure = True

        else:

            values.append(part)

    if found_structure:
        return " ".join(values)

    return text


# ============================================================
# 9. GROUP COLUMN DETECTION
# ============================================================

def detect_group_column(
    metadata_df: pd.DataFrame,
) -> Optional[str]:

    logger.info(
        "Detecting experimental group column..."
    )

    best_column = None
    best_score = 0.0

    candidates = [
        column
        for column in CANDIDATE_METADATA_COLUMNS
        if column in metadata_df.columns
    ]

    for column in candidates:

        values = (
            metadata_df[column]
            .dropna()
            .astype(str)
        )

        if values.empty:
            continue

        keyword_hits = 0

        for value in values:

            clean_value = (
                _values_only(value)
                .lower()
            )

            if any(
                keyword in clean_value
                for keyword in ALL_GROUP_KEYWORDS
            ):

                keyword_hits += 1

        if keyword_hits == 0:
            continue

        coverage = (
            keyword_hits /
            len(values)
        )

        has_control = any(
            any(
                keyword in
                _values_only(value).lower()
                for keyword in CONTROL_KEYWORDS
            )
            for value in values
        )

        has_disease = any(
            any(
                keyword in
                _values_only(value).lower()
                for keyword in DISEASE_KEYWORDS
            )
            for value in values
        )

        score = coverage

        if has_control and has_disease:
            score += 0.5

        if score > best_score:

            best_score = score
            best_column = column

    if best_column:

        logger.info(
            "Detected group column: %s",
            best_column,
        )

    else:

        logger.warning(
            "Could not automatically detect a group column."
        )

    return best_column


# ============================================================
# 10. NORMALIZE GROUP LABEL
# ============================================================

def _normalize_label(
    raw_value: str,
) -> Optional[str]:

    value = (
        _values_only(raw_value)
        .lower()
    )

    is_control = any(
        keyword in value
        for keyword in CONTROL_KEYWORDS
    )

    is_disease = any(
        keyword in value
        for keyword in DISEASE_KEYWORDS
    )

    if is_control and not is_disease:
        return "Control"

    if is_disease and not is_control:
        return "Disease"

    return None


# ============================================================
# 11. CREATE GROUP LABELS
# ============================================================

def create_group_labels(
    metadata_df: pd.DataFrame,
    group_column: Optional[str] = None,
) -> pd.DataFrame:

    if "Sample" not in metadata_df.columns:

        return pd.DataFrame(
            columns=[
                "Sample",
                "Group",
            ]
        )

    if group_column is None:

        group_column = detect_group_column(
            metadata_df
        )

    if (
        group_column is None
        or group_column not in metadata_df.columns
    ):

        logger.warning(
            "No group column found. "
            "Samples will be labeled Unknown."
        )

        return pd.DataFrame(
            {
                "Sample": metadata_df["Sample"],
                "Group": "Unknown",
            }
        )

    labels = []

    for raw_value in metadata_df[
        group_column
    ].fillna(""):

        raw_value = str(
            raw_value
        ).strip()

        normalized = _normalize_label(
            raw_value
        )

        if normalized:

            labels.append(
                normalized
            )

        elif raw_value:

            labels.append(
                raw_value
            )

        else:

            labels.append(
                "Unknown"
            )

    result = pd.DataFrame(
        {
            "Sample": metadata_df["Sample"],
            "Group": labels,
        }
    )

    logger.info(
        "Groups detected: %s",
        result["Group"]
        .value_counts()
        .to_dict(),
    )

    return result


# ============================================================
# 12. DATASET VALIDATION
# ============================================================

def validate_dataset(
    expression_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
) -> Dict[str, Any]:

    report = {
        "is_valid": True,
        "n_genes": 0,
        "n_samples_expression": 0,
        "n_samples_metadata": 0,
        "missing_metadata_for_samples": [],
        "missing_expression_for_samples": [],
        "duplicate_samples": [],
        "duplicate_genes": [],
        "groups": {},
    }

    # --------------------------------------------------------
    # Expression check
    # --------------------------------------------------------

    if (
        expression_df is None
        or expression_df.empty
        or "Gene" not in expression_df.columns
    ):

        report["is_valid"] = False

        report["error"] = (
            "Expression matrix is empty "
            "or missing the 'Gene' column."
        )

        return report

    # --------------------------------------------------------
    # Sample names
    # --------------------------------------------------------

    expression_samples = [
        column
        for column in expression_df.columns
        if column != "Gene"
    ]

    metadata_samples = []

    if "Sample" in metadata_df.columns:

        metadata_samples = (
            metadata_df["Sample"]
            .astype(str)
            .tolist()
        )

    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    report["n_genes"] = int(
        expression_df.shape[0]
    )

    report["n_samples_expression"] = len(
        expression_samples
    )

    report["n_samples_metadata"] = len(
        metadata_samples
    )

    # --------------------------------------------------------
    # Sample matching
    # --------------------------------------------------------

    expression_set = set(
        map(str, expression_samples)
    )

    metadata_set = set(
        map(str, metadata_samples)
    )

    report[
        "missing_metadata_for_samples"
    ] = sorted(
        expression_set - metadata_set
    )

    report[
        "missing_expression_for_samples"
    ] = sorted(
        metadata_set - expression_set
    )

    # --------------------------------------------------------
    # Duplicate samples
    # --------------------------------------------------------

    report["duplicate_samples"] = sorted(
        {
            sample
            for sample in metadata_samples
            if metadata_samples.count(sample) > 1
        }
    )

    # --------------------------------------------------------
    # Duplicate genes
    # --------------------------------------------------------

    duplicate_genes = (
        expression_df["Gene"]
        .astype(str)
        .duplicated()
    )

    report["duplicate_genes"] = (
        expression_df.loc[
            duplicate_genes,
            "Gene"
        ]
        .astype(str)
        .unique()
        .tolist()
    )

    # --------------------------------------------------------
    # Groups
    # --------------------------------------------------------

    if "Group" in metadata_df.columns:

        report["groups"] = (
            metadata_df["Group"]
            .value_counts()
            .to_dict()
        )

    # --------------------------------------------------------
    # Determine validity
    # --------------------------------------------------------

    if (
        report["missing_metadata_for_samples"]
        or report["missing_expression_for_samples"]
        or report["duplicate_samples"]
        or report["duplicate_genes"]
    ):

        report["is_valid"] = False

    return report


# ============================================================
# 13. MAIN GEO LOADER
# ============================================================

def load_geo_dataset(
    accession: str,
    group_column: Optional[str] = None,
    cache_dir: str = "data/geo_cache",
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    Dict[str, Any],
]:

    """
    Complete GEO loading pipeline.

    GSE accession
        ↓
    Download
        ↓
    Expression extraction
        ↓
    Probe → gene symbol
        ↓
    Metadata extraction
        ↓
    Group detection
        ↓
    Validation

    Returns
    -------
    expression_df
        Gene | GSM1 | GSM2 | ...

    metadata_df
        Sample | Group

    validation_report
        Dataset quality report.
    """

    # --------------------------------------------------------
    # 1. Validate accession
    # --------------------------------------------------------

    accession = validate_geo_accession(
        accession
    )

    # --------------------------------------------------------
    # 2. Download GEO
    # --------------------------------------------------------

    gse = download_geo_dataset(
        accession,
        cache_dir=cache_dir,
    )

    # --------------------------------------------------------
    # 3. Expression
    # --------------------------------------------------------

    expression_df = (
        extract_expression_matrix(
            gse
        )
    )

    # --------------------------------------------------------
    # 4. Metadata
    # --------------------------------------------------------

    raw_metadata_df = (
        extract_sample_metadata(
            gse
        )
    )

    # --------------------------------------------------------
    # 5. Group detection
    # --------------------------------------------------------

    metadata_df = create_group_labels(
        raw_metadata_df,
        group_column=group_column,
    )

    # --------------------------------------------------------
    # 6. Validation
    # --------------------------------------------------------

    validation_report = validate_dataset(
        expression_df,
        metadata_df,
    )

    # --------------------------------------------------------
    # 7. Add accession information
    # --------------------------------------------------------

    validation_report[
        "accession"
    ] = accession

    logger.info(
        "GEO pipeline complete: %s",
        accession,
    )

    return (
        expression_df,
        metadata_df,
        validation_report,
    )
