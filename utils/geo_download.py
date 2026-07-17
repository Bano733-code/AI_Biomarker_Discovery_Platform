import argparse
import os
import sys
import re
from pathlib import Path

import pandas as pd

try:
    import GEOparse
except ImportError:
    sys.exit(
        "ERROR: GEOparse is not installed.\n"
        "Install it with: pip install GEOparse --break-system-packages"
    )

# --------------------------------------------------------------------------
# Keyword banks used for automatic control/disease group detection
# --------------------------------------------------------------------------
CONTROL_KEYWORDS = [
    "control", "ctrl", "ctr", "normal", "healthy", "wild type", "wild-type",
    "wt", "untreated", "unaffected", "baseline", "sham", "vehicle",
    "non-tumor", "nontumor", "non-cancer", "reference", "naive", "mock",
]

CASE_KEYWORDS = [
    "disease", "diseased", "tumor", "tumour", "cancer", "carcinoma",
    "patient", "affected", "treated", "treatment", "mutant", "case",
    "ko", "knockout", "malignant", "lesion", "infected", "positive",
]

# Metadata field name hints that are likely to encode group/condition info
FIELD_NAME_HINTS = [
    "disease", "condition", "group", "status", "state", "phenotype",
    "diagnosis", "treatment", "genotype", "tissue type",
]


# --------------------------------------------------------------------------
# Step 1: Download
# --------------------------------------------------------------------------
def download_geo(accession: str, destdir: str):
    """Download a GEO accession (GSE) and parse it with GEOparse."""
    print(f"[1/4] Downloading {accession} ...")
    os.makedirs(destdir, exist_ok=True)
    gse = GEOparse.get_GEO(geo=accession, destdir=destdir, silent=True)
    print(f"      Downloaded. {len(gse.gsms)} samples, {len(gse.gpls)} platform(s).")
    return gse


# --------------------------------------------------------------------------
# Step 2: Expression matrix
# --------------------------------------------------------------------------
def extract_expression_matrix(gse) -> pd.DataFrame:
    """
    Build a probes/genes x samples expression matrix from the GSMs'
    VALUE column. Works for standard array-based GSE series-matrix data.
    """
    print("[2/4] Extracting expression matrix ...")
    try:
        expr = gse.pivot_samples("VALUE")
    except Exception as e:
        print(f"      WARNING: could not pivot on 'VALUE' column ({e}).")
        expr = pd.DataFrame()

    if expr is None or expr.empty:
        print("      No standard expression table found (this may be an "
              "RNA-seq / supplementary-file-only series). Returning empty matrix.")
    else:
        print(f"      Matrix shape: {expr.shape[0]} features x {expr.shape[1]} samples.")
    return expr


# --------------------------------------------------------------------------
# Step 3: Sample metadata
# --------------------------------------------------------------------------
def extract_metadata(gse) -> pd.DataFrame:
    """
    Build a samples x fields metadata table from each GSM's .metadata dict.
    Handles the common 'characteristics_ch1' repeated-key pattern by
    splitting on the first ':' to turn 'tissue: liver' into a named column.
    """
    print("[3/4] Extracting sample metadata ...")
    rows = {}
    for gsm_name, gsm in gse.gsms.items():
        row = {}
        for key, values in gsm.metadata.items():
            if not values:
                continue
            if key == "characteristics_ch1":
                # Each entry usually looks like "field: value"
                for i, item in enumerate(values):
                    if ":" in item:
                        field, val = item.split(":", 1)
                        col_name = f"characteristics_ch1.{i}.{field.strip()}"
                        row[col_name] = val.strip()
                    else:
                        row[f"characteristics_ch1.{i}"] = item.strip()
            else:
                row[key] = "; ".join(values) if len(values) > 1 else values[0]
        rows[gsm_name] = row

    meta = pd.DataFrame.from_dict(rows, orient="index")
    meta.index.name = "sample_id"
    print(f"      Metadata shape: {meta.shape[0]} samples x {meta.shape[1]} fields.")
    return meta


# --------------------------------------------------------------------------
# Step 4a: Automatic control/disease group detection
# --------------------------------------------------------------------------
def _score_column(series: pd.Series):
    """
    Score a metadata column on how well it separates into a control-like
    group and a case-like group based on keyword matches.
    Returns (score, mapping_dict) where mapping_dict maps raw value -> label.
    """
    values = series.dropna().astype(str)
    if values.empty:
        return 0, {}

    mapping = {}
    matched = 0
    for raw_val in values.unique():
        lower = raw_val.lower()
        is_control = any(kw in lower for kw in CONTROL_KEYWORDS)
        is_case = any(kw in lower for kw in CASE_KEYWORDS)
        if is_control and not is_case:
            mapping[raw_val] = "control"
            matched += 1
        elif is_case and not is_control:
            mapping[raw_val] = "case"
            matched += 1
        # ambiguous (both or neither) -> leave unmapped

    n_unique = values.nunique()
    n_labeled_groups = len(set(mapping.values()))
    if n_labeled_groups < 2:
        return 0, {}

    # Score: fraction of distinct values we could confidently map,
    # bonus if the column exactly splits into two clean groups.
    coverage = matched / n_unique
    score = coverage
    if n_unique == 2:
        score += 0.5
    return score, mapping


def auto_detect_group(meta: pd.DataFrame):
    """
    Scan every metadata column, score it for control/case separability,
    and return (best_column_name, group_series, mapping) or (None, None, None)
    if nothing usable is found.
    """
    print("[4/4] Auto-detecting control/disease groups ...")
    best_col, best_score, best_mapping = None, 0, {}

    # Prioritize columns whose name hints at group/condition info, but
    # still score every column as a fallback.
    columns_sorted = sorted(
        meta.columns,
        key=lambda c: any(hint in c.lower() for hint in FIELD_NAME_HINTS),
        reverse=True,
    )

    for col in columns_sorted:
        score, mapping = _score_column(meta[col])
        if score > best_score:
            best_score, best_col, best_mapping = score, col, mapping

    if best_col is None:
        print("      Could not confidently auto-detect groups from metadata.")
        return None, None, None

    group_series = meta[best_col].map(best_mapping)
    n_control = (group_series == "control").sum()
    n_case = (group_series == "case").sum()
    print(f"      Best column: '{best_col}' (score={best_score:.2f})")
    print(f"      -> control: {n_control} samples, case/disease: {n_case} samples, "
          f"unclassified: {group_series.isna().sum()}")
    return best_col, group_series, best_mapping


# --------------------------------------------------------------------------
# Step 4b: Manual group selection (for non-standard metadata)
# --------------------------------------------------------------------------
def manual_group_selection(meta: pd.DataFrame, group_column=None,
                            control_keywords=None, case_keywords=None,
                            interactive=True):
    """
    Let the user choose which metadata column defines the groups, and how
    its values map to 'control' vs 'case'. Supports both a non-interactive
    mode (column/keywords passed as CLI args) and an interactive prompt.
    """
    columns = list(meta.columns)

    # --- Choose the column ---
    if group_column is None:
        if not interactive:
            print("No --group-column given and not running interactively; skipping.")
            return None, None
        print("\nAvailable metadata columns:")
        for i, col in enumerate(columns):
            sample_vals = meta[col].dropna().unique()[:3]
            print(f"  [{i}] {col}  (e.g. {list(sample_vals)})")
        choice = input("\nEnter the number of the column that defines your groups "
                        "(or blank to skip): ").strip()
        if choice == "":
            return None, None
        try:
            group_column = columns[int(choice)]
        except (ValueError, IndexError):
            print("Invalid selection; skipping group assignment.")
            return None, None
    elif group_column not in columns:
        print(f"Column '{group_column}' not found in metadata. Available columns:")
        for c in columns:
            print(f"  - {c}")
        return None, None

    unique_vals = sorted(meta[group_column].dropna().astype(str).unique())

    # --- Map values to control/case ---
    mapping = {}
    if control_keywords or case_keywords:
        control_keywords = [k.lower() for k in (control_keywords or [])]
        case_keywords = [k.lower() for k in (case_keywords or [])]
        for val in unique_vals:
            lower = val.lower()
            if any(kw in lower for kw in control_keywords):
                mapping[val] = "control"
            elif any(kw in lower for kw in case_keywords):
                mapping[val] = "case"
    elif interactive:
        print(f"\nUnique values in '{group_column}':")
        for i, val in enumerate(unique_vals):
            print(f"  [{i}] {val}")
        print("\nAssign each value to a group label (e.g. 'control' or 'case'),")
        print("or press Enter to leave it unclassified.")
        for val in unique_vals:
            label = input(f"  '{val}' -> ").strip()
            if label:
                mapping[val] = label
    else:
        print("No keyword mapping given and not interactive; leaving values unmapped.")

    group_series = meta[group_column].map(mapping)
    print(f"\nGroup column: '{group_column}'")
    print(group_series.value_counts(dropna=False).to_string())
    return group_column, group_series


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Download a GEO accession and extract expression matrix, "
                    "metadata, and control/disease group labels.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("accession", help="GEO accession, e.g. GSE12345")
    parser.add_argument("-o", "--output-dir", default="./geo_output",
                         help="Directory to save downloaded files and CSV outputs "
                              "(default: ./geo_output)")
    parser.add_argument("--no-groups", action="store_true",
                         help="Skip group detection entirely (only expression + metadata).")
    parser.add_argument("--manual", action="store_true",
                         help="Skip auto-detection and go straight to manual group selection.")
    parser.add_argument("--group-column", default=None,
                         help="Manually specify the metadata column to use for grouping "
                              "(enables non-interactive manual mode).")
    parser.add_argument("--control-keywords", nargs="*", default=None,
                         help="Keywords identifying the control group's values "
                              "(used with --group-column).")
    parser.add_argument("--case-keywords", nargs="*", default=None,
                         help="Keywords identifying the case/disease group's values "
                              "(used with --group-column).")
    parser.add_argument("--non-interactive", action="store_true",
                         help="Never prompt for input; skip steps that would require it "
                              "unless resolved via CLI flags.")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    raw_dir = out_dir / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Download
    gse = download_geo(args.accession, str(raw_dir))

    # 2. Expression matrix
    expr = extract_expression_matrix(gse)
    expr_path = out_dir / f"{args.accession}_expression_matrix.csv"
    expr.to_csv(expr_path)
    print(f"      Saved -> {expr_path}")

    # 3. Metadata
    meta = extract_metadata(gse)
    meta_path = out_dir / f"{args.accession}_sample_metadata.csv"
    meta.to_csv(meta_path)
    print(f"      Saved -> {meta_path}")

    # 4. Groups
    if args.no_groups:
        print("[4/4] Skipping group detection (--no-groups).")
    else:
        group_col, group_series, mapping = (None, None, None)

        if not args.manual and args.group_column is None:
            group_col, group_series, mapping = auto_detect_group(meta)

        if group_series is None:
            # Fall back to manual selection: either explicit --group-column
            # (non-interactive) or an interactive prompt.
            interactive = not args.non_interactive
            group_col, group_series = manual_group_selection(
                meta,
                group_column=args.group_column,
                control_keywords=args.control_keywords,
                case_keywords=args.case_keywords,
                interactive=interactive,
            )

        if group_series is not None:
            groups_df = meta.copy()
            groups_df["group"] = group_series
            groups_path = out_dir / f"{args.accession}_sample_groups.csv"
            groups_df[["group"]].to_csv(groups_path)
            print(f"      Saved -> {groups_path}")
        else:
            print("      No group labels were assigned.")

    print("\nDone.")


if __name__ == "__main__":
    main()
