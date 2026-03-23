# =============================================================
# ANOMCHECKER — preprocessing.py
# Handles all data loading, validation, cleaning, and sampling.
# =============================================================

import io
import base64
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def decode_uploaded_file(contents: str, filename: str) -> pd.DataFrame:
    """
    Decode a base64-encoded Dash upload and return a raw DataFrame.
    Raises ValueError for non-CSV files or unreadable content.
    """
    if not filename.lower().endswith(".csv"):
        raise ValueError("Only CSV files are supported.")

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        raise ValueError(f"Could not read CSV: {str(e)}")

    return df


def get_file_stats(contents: str, filename: str) -> dict:
    """
    Return basic stats about the uploaded file without full preprocessing.
    Used to populate the file info panel and guide the user's row range input.
    """
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    size_mb = len(decoded) / (1024 * 1024)

    df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    total_rows = len(df)
    total_cols = len(df.columns)

    label_col = _find_label_column(df)
    if label_col:
        numeric_features = df.drop(columns=[label_col]).select_dtypes(
            include=[np.number]
        ).shape[1]
    else:
        numeric_features = df.select_dtypes(include=[np.number]).shape[1]

    return {
        "filename":        filename,
        "size_mb":         round(size_mb, 2),
        "total_rows":      total_rows,
        "total_cols":      total_cols,
        "numeric_features":numeric_features,
        "has_label":       label_col is not None,
        "label_col":       label_col,
    }


def _find_label_column(df: pd.DataFrame) -> str | None:
    """
    Detect the label column regardless of leading/trailing whitespace.
    Supports CICIDS2017 (' Label') and UNSW-NB15 ('label') formats.
    """
    for col in df.columns:
        if col.strip().lower() == "label":
            return col
    return None


def slice_dataframe(df: pd.DataFrame, start_row: int, end_row: int) -> pd.DataFrame:
    """
    Slice the dataframe by 1-indexed row range [start_row, end_row].
    Enforces a hard maximum of 10,000 rows on the slice.
    """
    start_idx = max(0, start_row - 1)
    end_idx   = min(len(df), end_row)

    if (end_idx - start_idx) > 10000:
        end_idx = start_idx + 10000

    sliced = df.iloc[start_idx:end_idx].copy()

    if len(sliced) == 0:
        raise ValueError(
            f"Row range {start_row}-{end_row} produced an empty slice. "
            "Please check your input values."
        )

    return sliced


def _remove_correlated_features(X: np.ndarray, threshold: float = 0.95) -> np.ndarray:
    """
    Remove highly correlated features (correlation > threshold).
    Correlated features add noise without adding information to clustering.
    Keeps one feature from each correlated pair.
    """
    df_temp     = pd.DataFrame(X)
    corr_matrix = df_temp.corr().abs()
    upper       = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    df_temp = df_temp.drop(columns=to_drop)
    removed = X.shape[1] - df_temp.shape[1]
    if removed > 0:
        print(f"[ANOMCHECKER] Removed {removed} correlated features "
              f"({X.shape[1]} → {df_temp.shape[1]})")
    return df_temp.values


def preprocess(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """
    Full preprocessing pipeline on a sliced DataFrame.

    Steps:
      1. Detect and extract binary labels (CICIDS2017 or UNSW-NB15)
      2. Drop irrelevant non-numeric columns
      3. Replace inf/NaN values
      4. Drop zero-variance columns
      5. Remove highly correlated features (reduces noise)
      6. StandardScaler normalization

    Returns:
        X_scaled  - normalized feature matrix (numpy array)
        y         - binary ground truth labels (0=normal, 1=attack)
        df_clean  - the cleaned DataFrame (for anomaly export)
    """
    label_col = _find_label_column(df)
    if label_col is None:
        raise ValueError(
            "No 'Label' column found. "
            "File must be in CICIDS2017 or UNSW-NB15 format."
        )

    # ── Label extraction — handles both dataset formats ───────
    # CICIDS2017 : "BENIGN" = normal, anything else = attack
    # UNSW-NB15  : "0"      = normal, "1"           = attack
    raw_labels = df[label_col].astype(str).str.strip()
    unique_vals = raw_labels.str.upper().unique()
    is_numeric_labels = all(v in ["0", "1"] for v in unique_vals if v != "")

    if is_numeric_labels:
        y = (raw_labels != "0").astype(int)
        print("[ANOMCHECKER] Detected UNSW-NB15 label format (0/1)")
    else:
        y = (raw_labels.str.upper() != "BENIGN").astype(int)
        print("[ANOMCHECKER] Detected CICIDS2017 label format (BENIGN/attack)")

    print(f"[ANOMCHECKER] Labels — Normal: {(y==0).sum():,} | Attack: {(y==1).sum():,}")

    # ── Feature extraction ────────────────────────────────────
    # Drop irrelevant identifier and categorical columns
    COLS_TO_DROP = ["attack_cat", "id", "proto", "service", "state"]
    drop_these   = [c for c in COLS_TO_DROP if c in df.columns]
    X = df.drop(columns=[label_col] + drop_these).select_dtypes(include=[np.number])

    # Clean: replace inf, fill NaN with 0
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)

    # Drop constant columns — zero variance breaks StandardScaler
    X = X.loc[:, X.std() > 0]

    print(f"[ANOMCHECKER] Features after cleaning: {X.shape[1]}")

    if X.shape[1] == 0:
        raise ValueError(
            "No valid numeric features found after preprocessing. "
            "Check that your CSV has numeric columns."
        )

    # ── Remove correlated features ────────────────────────────
    X_values = _remove_correlated_features(X.values, threshold=0.95)

    print(f"[ANOMCHECKER] Final feature count: {X_values.shape[1]}")

    # ── Normalize ─────────────────────────────────────────────
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X_values)

    return X_scaled, y.values, df.reset_index(drop=True)