from __future__ import annotations

import json
import os
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import f_oneway, kruskal


def load_cleaned(data_dir: str = "data") -> pd.DataFrame:
    countries = ["benin", "sierraleone", "togo"]
    frames: List[pd.DataFrame] = []
    for c in countries:
        p = os.path.join(data_dir, f"{c}_clean.csv")
        if os.path.exists(p):
            d = pd.read_csv(p, parse_dates=["Timestamp"], low_memory=False)
            d["country"] = c
            frames.append(d)
    if not frames:
        raise FileNotFoundError("No cleaned CSVs found in data/. Run src/clean_countries.py first.")
    return pd.concat(frames, ignore_index=True)


def summarize(df: pd.DataFrame) -> Dict:
    result: Dict = {"summary": {}, "ranking": {}, "tests": {}}

    for metric in ["GHI", "DNI", "DHI"]:
        if metric in df.columns:
            g = df.groupby("country")[metric].agg(["mean", "median", "std"]).to_dict()
            # reshape to {country: {mean:.., median:.., std:..}}
            out = {}
            for stat, mapping in g.items():
                for country, value in mapping.items():
                    out.setdefault(country, {})[stat] = float(value) if pd.notnull(value) else None
            result["summary"][metric] = out
            # ranking by mean
            means = {c: v["mean"] for c, v in out.items() if v["mean"] is not None}
            result["ranking"][metric] = sorted(means.items(), key=lambda x: x[1], reverse=True)

    # tests for GHI
    if "GHI" in df.columns:
        groups = [df[df["country"] == c]["GHI"].dropna().values for c in df["country"].unique()]
        if all(len(g) > 0 for g in groups):
            f_stat, p_f = f_oneway(*groups)
            h_stat, p_h = kruskal(*groups)
            result["tests"]["GHI"] = {
                "anova_f": float(f_stat),
                "anova_p": float(p_f),
                "kruskal_h": float(h_stat),
                "kruskal_p": float(p_h),
            }
    return result


def main() -> None:
    df = load_cleaned("data")
    res = summarize(df)
    os.makedirs("metrics", exist_ok=True)
    out_path = os.path.join("metrics", "country_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))
    print(f"saved -> {out_path}")


if __name__ == "__main__":
    main()
