from __future__ import annotations

import json
import os
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import f_oneway, kruskal


def load_cleaned(data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    files = {
        "benin": os.path.join(data_dir, "benin_clean.csv"),
        "sierraleone": os.path.join(data_dir, "sierraleone_clean.csv"),
        "togo": os.path.join(data_dir, "togo_clean.csv"),
    }
    out = {}
    for c, p in files.items():
        if os.path.exists(p):
            df = pd.read_csv(p, parse_dates=["Timestamp"], low_memory=False)
            df["country"] = c
            out[c] = df
    return out


def compute_summary(dfs: Dict[str, pd.DataFrame]) -> Dict:
    summary = {}
    for country, df in dfs.items():
        res = {}
        for col in ["GHI", "DNI", "DHI"]:
            if col in df:
                res[f"{col.lower()}_mean"] = float(df[col].mean())
                res[f"{col.lower()}_median"] = float(df[col].median())
                res[f"{col.lower()}_std"] = float(df[col].std(ddof=0))
        # cleaning gains
        if "Cleaning" in df.columns:
            for mod in ["ModA", "ModB"]:
                if mod in df:
                    g = df.groupby("Cleaning")[mod].mean()
                    res[f"{mod.lower()}_clean_gain"] = float(g.get(1, 0) - g.get(0, 0))
        summary[country] = res

    ranking = sorted(
        [(c, v.get("ghi_mean", 0.0)) for c, v in summary.items()],
        key=lambda x: x[1],
        reverse=True,
    )

    # ANOVA / Kruskal on GHI if available
    anova = {}
    ghi_groups: List[np.ndarray] = []
    for c, df in dfs.items():
        if "GHI" in df:
            arr = df["GHI"].dropna().values
            if len(arr) > 0:
                ghi_groups.append(arr)
    if len(ghi_groups) >= 2:
        try:
            f_stat, p_f = f_oneway(*ghi_groups)
            h_stat, p_h = kruskal(*ghi_groups)
            anova = {
                "anova_f": float(f_stat),
                "anova_p": float(p_f),
                "kruskal_h": float(h_stat),
                "kruskal_p": float(p_h),
            }
        except Exception as e:
            anova = {"error": str(e)}

    return {"summary": summary, "ranking_mean_GHI": ranking, "tests": anova}


def main() -> None:
    dfs = load_cleaned("data")
    result = compute_summary(dfs)
    os.makedirs("metrics", exist_ok=True)
    with open("metrics/country_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
