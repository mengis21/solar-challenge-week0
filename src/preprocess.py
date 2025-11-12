from __future__ import annotations

from typing import Optional, Iterable

import pandas as pd


DT_CANDIDATES: tuple[str, ...] = (
    "time",
    "date",
    "datetime",
    "timestamp",
)


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    # strip spaces in column names and drop duplicates.
    out = df.copy()
    out.columns = [c.strip() for c in out.columns]
    if not out.empty:
        out = out.drop_duplicates().reset_index(drop=True)
    return out


def find_datetime_column(df: pd.DataFrame) -> Optional[str]:
    """Guess a datetime column by name.

    Looks for common names like 'time', 'date', 'datetime', 'timestamp'.
    Returns the first match (case-insensitive) or None.
    """
    lowered = {c.lower(): c for c in df.columns}
    for key in DT_CANDIDATES:
        if key in lowered:
            return lowered[key]
    # Try partial matches like 'time_col'
    for c in df.columns:
        cl = c.lower()
        if any(k in cl for k in DT_CANDIDATES):
            return c
    return None


def parse_datetime(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Parse a column to datetime, in-place style but returns DataFrame for chaining."""
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce", infer_datetime_format=True)
    return out


def add_time_features(df: pd.DataFrame, dt_col: str) -> pd.DataFrame:
    """Add simple time features if a datetime column is present.

    Creates: year, month, day, hour, dayofweek.
    """
    out = df.copy()
    if dt_col not in out.columns:
        return out
    if not pd.api.types.is_datetime64_any_dtype(out[dt_col]):
        out = parse_datetime(out, dt_col)
    # If still not datetime (all NaT), skip feature creation
    if not pd.api.types.is_datetime64_any_dtype(out[dt_col]):
        return out
    out["year"] = out[dt_col].dt.year
    out["month"] = out[dt_col].dt.month
    out["day"] = out[dt_col].dt.day
    out["hour"] = out[dt_col].dt.hour
    out["dayofweek"] = out[dt_col].dt.dayofweek
    return out


def simple_fill_numeric(
    df: pd.DataFrame,
    *,
    columns: Optional[Iterable[str]] = None,
    strategy: str = "median",
) -> pd.DataFrame:
    """Fill NaNs in numeric columns with a simple strategy.

    strategy in {"median", "mean", "zero"}.
    """
    out = df.copy()
    num_cols = out.select_dtypes("number").columns.tolist()
    target_cols = list(columns) if columns is not None else num_cols
    for col in target_cols:
        if col not in out.columns:
            continue
        if strategy == "median":
            val = out[col].median()
        elif strategy == "mean":
            val = out[col].mean()
        elif strategy == "zero":
            val = 0
        else:
            raise ValueError("Unknown strategy: {strategy}")
        out[col] = out[col].fillna(val)
    return out


def quick_preprocess(
    df: pd.DataFrame,
    *,
    datetime_col: Optional[str] = None,
    fill_strategy: str = "median",
) -> pd.DataFrame:
    """One-pass simple preprocessing for quick experiments.

    - basic_clean
    - find/parse datetime
    - add time features
    - simple_fill_numeric
    """
    out = basic_clean(df)
    dt_col = datetime_col or find_datetime_column(out)
    if dt_col:
        out = add_time_features(out, dt_col)
    out = simple_fill_numeric(out, strategy=fill_strategy)
    return out


if __name__ == "__main__":
    # Quick check: try to load data using ingest if available, then preprocess.
    try:
        import sys
        if "src" not in sys.path:
            sys.path.append("src")
        from ingest import load_all  # type: ignore

        data = load_all("data")
        processed = quick_preprocess(data)
        print(f"Input rows={len(data)} -> Processed rows={len(processed)}")
        print("Columns:", list(processed.columns))
    except Exception as e:
        print(f"Preprocess quick check skipped: {e}")
