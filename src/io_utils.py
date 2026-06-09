#------------------------------------------------------------------------------
# General IO and notebook helper functions
#------------------------------------------------------------------------------
import json
from pathlib import Path

import numpy as np
import pandas as pd

#------------------------------------------------------------------------------
# Print helpers
#------------------------------------------------------------------------------
def print_banner(title):
    print("\n" + "-" * 78); print(title); print("-" * 78)

#------------------------------------------------------------------------------
# Folder helpers
#------------------------------------------------------------------------------
def make_dirs(paths):
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)

#------------------------------------------------------------------------------
# JSON helpers
#------------------------------------------------------------------------------
def load_json(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing JSON file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

def save_json_overwrite(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path

#------------------------------------------------------------------------------
# CSV helpers
#------------------------------------------------------------------------------
def load_csv(path, **kwargs):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing CSV file: {path}")
    return pd.read_csv(path, **kwargs)

def read_csv_required(path, **kwargs):
    return load_csv(path, **kwargs)

def save_csv(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print("Saved ->", path)
    return path

#------------------------------------------------------------------------------
# Parquet helpers
#------------------------------------------------------------------------------
def load_parquet(path, **kwargs):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Missing parquet file: {path}")
    return pd.read_parquet(path, **kwargs)

def save_parquet(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    print("Saved ->", path)
    return path

#------------------------------------------------------------------------------
# Validation helpers
#------------------------------------------------------------------------------
def require_cols(df, cols, df_name="dataframe"):
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")
    return True

def audit_required_files(path_map):
    rows = []
    for name, path in path_map.items():
        path = Path(path)
        rows.append({"file_name": name, "path": str(path), "exists": path.exists(),
                     "size_bytes": path.stat().st_size if path.exists() else 0})
    return pd.DataFrame(rows)

#------------------------------------------------------------------------------
# Cleaning helpers
#------------------------------------------------------------------------------
def clean_label_series(series):
    return series.fillna("(not set)").astype(str).str.strip().replace({"": "(not set)", "nan": "(not set)", "None": "(not set)"})

def clean_date_col(df, col="week_start_date"):
    df = df.copy()
    if col in df.columns:
        df[col] = pd.to_datetime(df[col])
    return df

#------------------------------------------------------------------------------
# Simple calculation helpers
#------------------------------------------------------------------------------
def safe_divide(numerator, denominator):
    numerator = pd.to_numeric(pd.Series(numerator), errors="coerce")
    denominator = pd.to_numeric(pd.Series(denominator), errors="coerce")
    return np.where(denominator > 0, numerator / denominator, np.nan)

def weighted_mean(values, weights):
    v = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    mask = v.notna() & w.notna()
    if mask.sum() == 0 or w.loc[mask].sum() == 0:
        return np.nan
    return float(np.average(v.loc[mask], weights=w.loc[mask]))

#------------------------------------------------------------------------------
# Display helpers
#------------------------------------------------------------------------------
def pct_text(x, d=1):
    if pd.isna(x):
        return "n/a"
    return f"{x * 100:.{d}f}%"

def num_text(x, d=1):
    if pd.isna(x):
        return "n/a"
    return f"{x:,.{d}f}"
