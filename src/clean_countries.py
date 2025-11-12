"""
Simple cleaning utilities and a runner to export per-country cleaned CSVs.
This script reads local CSVs via ingest.load_all, splits by country, applies
basic cleaning (z-score outlier filter on selected cols and median impute),
and writes data/<country>_clean.csv (data/ is gitignored).
"""
from __future__ import annotations

import os
import sys
from typing import List

import numpy as np
import pandas as pd

if "src" not in sys.path:
    sys.path.append("src")

from ingest import load_all  # type: ignore
import preprocess  # type: ignore


ZCOLS = [
    "GHI", "DNI", "DHI", "ModA", "ModB", "WS", "WSgust",
]


def zscore_filter(df: pd.DataFrame, cols: List[str], z: float = 3.0) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            mu = out[c].mean()
            sd = out[c].std(ddof=0)
            if pd.notnull(sd) and sd > 0:
                out = out[(out[c] - mu).abs() <= z * sd]
    return out.reset_index(drop=True)


def clean_country(df: pd.DataFrame) -> pd.DataFrame:
    # basic preprocess (datetime + features + numeric fill)
    df = preprocess.quick_preprocess(df, fill_strategy="median")
    # outlier filter on target/sensors/wind columns
    df = zscore_filter(df, ZCOLS, z=3.0)
    # ensure target present and drop rows with missing target
    if "GHI" in df.columns:
        df = df.dropna(subset=["GHI"]).reset_index(drop=True)
    return df


def save_country_csvs(data_dir: str = "data") -> None:
    df_all = load_all(data_dir)
    if "country" not in df_all.columns:
        raise RuntimeError("Expected 'country' column from ingest.load_all")
    countries = sorted(df_all["country"].dropna().unique().tolist())
    os.makedirs(data_dir, exist_ok=True)

    for c in countries:
        sub = df_all[df_all["country"] == c].reset_index(drop=True)
        cleaned = clean_country(sub)
        out_path = os.path.join(data_dir, f"{c}_clean.csv")
        cleaned.to_csv(out_path, index=False)
        print(f"saved -> {out_path} rows={len(cleaned)} cols={len(cleaned.columns)}")


if __name__ == "__main__":
    save_country_csvs("data")
