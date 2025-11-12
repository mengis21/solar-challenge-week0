import os
from typing import List

import pandas as pd


def _get_country_from_filename(filename: str) -> str:
    """Return a lowercase country name guessed from the CSV filename.

    Example:
    - benin-malanville.csv -> benin
    - sierraleone-bumbuna.csv -> sierraleone
    - togo-dapaong_qc.csv -> togo
    """
    base = os.path.basename(filename).lower()
    # Try split by '-' first, then '_', else strip extension
    if '-' in base:
        return base.split('-')[0]
    if '_' in base:
        return base.split('_')[0]
    return os.path.splitext(base)[0]


def load_single(path: str) -> pd.DataFrame:
    """Load a single CSV and add simple metadata columns.

    Adds:
    - country: from filename
    - source_file: just the filename
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)
    df["country"] = _get_country_from_filename(path)
    df["source_file"] = os.path.basename(path)
    return df


def list_csvs(data_dir: str = "data") -> List[str]:
    """List CSV file paths under a directory (non-recursive)."""
    if not os.path.isdir(data_dir):
        raise NotADirectoryError(f"Directory not found: {data_dir}")
    files = []
    for name in os.listdir(data_dir):
        if name.lower().endswith(".csv"):
            files.append(os.path.join(data_dir, name))
    return sorted(files)


def load_all(data_dir: str = "data") -> pd.DataFrame:
    """Load all CSVs under data_dir and concatenate them.

    Skips files that fail to load and prints a short message.
    Returns an empty DataFrame if none loaded.
    """
    paths = list_csvs(data_dir)
    frames = []
    for p in paths:
        try:
            frames.append(load_single(p))
        except Exception as e:
            # Keep it simple, just show the skip
            print(f"Skipping {p}: {e}")
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()


if __name__ == "__main__":
    # Small manual check: load all and print shape
    combined = load_all("data")
    print(f"Loaded rows: {len(combined)}; columns: {list(combined.columns)}")
