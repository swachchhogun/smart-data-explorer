"""
data_utils.py
─────────────
Data ingestion, cleaning, and type-override helpers.
"""

import io
import pandas as pd
import numpy as np


# ── CSV reading ──────────────────────────────────────────────────────────────

def safe_read_csv(file) -> tuple[pd.DataFrame | None, str | None]:
    """
    Try multiple encodings and separators to read a CSV file.
    Returns (dataframe, None) on success or (None, error_message) on failure.
    """
    for enc in ["utf-8", "latin-1", "utf-16", "cp1252"]:
        for sep in [",", ";", "\t"]:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=enc, sep=sep)
                if df.shape[1] > 1 or sep == ",":
                    return df, None
            except Exception:
                continue
    return None, "Could not read this file. Make sure it's a valid CSV."


# ── Auto-cleaning ────────────────────────────────────────────────────────────

def smart_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Apply a suite of automatic cleaning steps to a DataFrame.
    Returns (cleaned_df, report) where report is a list of human-readable actions taken.
    """
    report  = []
    cleaned = df.copy()

    # Strip whitespace from column names
    cleaned.columns = [c.strip() for c in cleaned.columns]

    if cleaned.empty:
        return cleaned, ["File is empty."]

    # Try to parse object columns that look like datetimes
    for col in cleaned.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(cleaned[col], infer_datetime_format=True, errors="coerce")
            if parsed.notna().mean() > 0.7:
                cleaned[col] = parsed
                report.append(f"Parsed '{col}' as datetime")
        except Exception:
            pass

    # Strip leading/trailing whitespace from string values
    for col in cleaned.select_dtypes(include="object").columns:
        try:
            cleaned[col] = cleaned[col].str.strip()
        except Exception:
            pass

    # Fill numeric nulls with column median
    for col in cleaned.select_dtypes(include="number").columns:
        n = int(cleaned[col].isnull().sum())
        if n > 0:
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
            report.append(f"Filled {n} nulls in '{col}' with median")

    # Fill categorical nulls with column mode
    for col in cleaned.select_dtypes(include="object").columns:
        n = int(cleaned[col].isnull().sum())
        if n > 0 and not cleaned[col].mode().empty:
            cleaned[col] = cleaned[col].fillna(cleaned[col].mode()[0])
            report.append(f"Filled {n} nulls in '{col}' with mode")

    # Drop fully-empty rows and columns
    before = len(cleaned)
    cleaned = cleaned.dropna(how="all").dropna(axis=1, how="all")
    if before - len(cleaned) > 0:
        report.append(f"Removed {before - len(cleaned)} empty rows")

    # Drop duplicate rows
    n_dupes = int(cleaned.duplicated().sum())
    if n_dupes > 0:
        cleaned = cleaned.drop_duplicates()
        report.append(f"Removed {n_dupes} duplicate rows")

    return cleaned, report


# ── Type overrides ───────────────────────────────────────────────────────────

def apply_type_overrides(df: pd.DataFrame, overrides: dict) -> pd.DataFrame:
    """
    Apply user-specified column type overrides to a DataFrame.
    Silently skips columns that don't exist or fail to convert.
    """
    out = df.copy()
    for col, t in overrides.items():
        if col not in out.columns:
            continue
        try:
            if t == "Text / String":
                out[col] = out[col].astype(str)
            elif t == "Integer":
                out[col] = pd.to_numeric(out[col], errors="coerce").astype("Int64")
            elif t == "Float / Decimal":
                out[col] = pd.to_numeric(out[col], errors="coerce")
            elif t == "Date / Time":
                out[col] = pd.to_datetime(out[col], errors="coerce")
            elif t == "Boolean":
                out[col] = out[col].map(
                    lambda x: True if str(x).lower() in ("1", "true", "yes", "y") else False
                )
        except Exception:
            pass
    return out


# ── Export helpers ───────────────────────────────────────────────────────────

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a DataFrame to an Excel (.xlsx) file in memory and return bytes."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
        if hasattr(writer, "sheets"):
            ws = writer.sheets["Data"]
            for col_cells in ws.columns:
                max_len = max(len(str(c.value or "")) for c in col_cells)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 2, 40)
    buf.seek(0)
    return buf.read()


# ── Column health scoring ────────────────────────────────────────────────────

def col_health(s: pd.Series) -> dict:
    """
    Compute a quality score (0–100) for a DataFrame column.
    Penalises high null rates and high-cardinality object columns.
    """
    null_pct   = s.isnull().mean() * 100
    unique_pct = s.nunique() / max(len(s), 1) * 100
    score = max(
        0,
        100 - null_pct - (20 if unique_pct > 95 and pd.api.types.is_object_dtype(s) else 0)
    )
    return {"null_pct": round(null_pct, 1), "unique": s.nunique(), "score": round(score)}
