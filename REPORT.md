# Solar Data Discovery – Week 0 Final Report

Short, clear, and practical. This follows our style and can be converted to PDF.

## 1. Business Objective
- MoonLight Energy Solutions needs a quick analysis to guide solar investment strategy.
- Goal: identify high-potential regions aligned with long-term sustainability.

## 2. Data Overview
- Three countries: Benin, Sierra Leone, Togo.
- Key variables: Timestamp, GHI, DNI, DHI, modules (ModA/ModB), temperatures (Tamb/TModA/TModB), humidity (RH), wind (WS/WD), BP, Cleaning, Precipitation.
- Data loaded locally; CSVs are not committed.

## 3. Method in Brief
- Ingestion: `src/ingest.py` tags country from filename.
- Cleaning: `src/preprocess.py` + `src/clean_countries.py` (median imputation; z-score outlier filter on GHI/DNI/DHI/ModA/ModB/WS/WSgust).
- EDA: per-country notebooks in `notebooks/` with summary stats, distributions, correlations, and time series.
- Modeling (baseline): Linear Regression and RandomForest. Metrics saved to `metrics/baseline.json`.
- Dashboard: Streamlit (`app.py`) for quick exploration.

## 4. Key Findings
- Highest average GHI: Benin (≈235.93 W/m²), then Togo (≈223.38), then Sierra Leone (≈180.42).
- Highest average DNI: Benin (≈166.66 W/m²), then Togo (≈147.58), then Sierra Leone (≈100.70).
- Highest average DHI: Togo (≈112.63 W/m²), then Benin (≈111.54), then Sierra Leone (≈106.60).
- Medians near zero are expected due to many nighttime observations; means are better for ranking solar potential here.
- Variability (std of GHI) is larger in Benin (≈328.13) and Togo (≈316.96) than Sierra Leone (≈273.84), consistent with stronger daytime peaks.
- Cleaning effect: visuals suggest ModA/ModB improve after cleaning; quantify in a follow-up (see country EDA notebooks).

## 5. Cross-Country Comparison
- Boxplots: GHI, DNI, DHI by country.
- Summary table: mean/median/std per metric and country.
- Optional tests: ANOVA and Kruskal on GHI.

Results snapshot:
- ANOVA on GHI: F ≈ 4564.77, p ≈ 0.0 (differences across countries are significant).
- Kruskal–Wallis on GHI: H ≈ 7473.82, p ≈ 0.0.
- Ranking by average GHI: Benin > Togo > Sierra Leone.
- Ranking by average DNI: Benin > Togo > Sierra Leone.
- Ranking by average DHI: Togo > Benin > Sierra Leone.

## 6. Baseline Modeling Results
- Best model: RandomForestRegressor
- Metrics (test set): see `metrics/baseline.json`
  - MAE ≈ 3.68
  - RMSE ≈ 7.84
- Note: Simple, fast baseline; not optimized.

## 7. Recommendations
- Focus regions for higher GHI and stable patterns (based on boxplots/rankings).
- Investigate operational gains related to Cleaning (ModA/ModB improvements).
- Next steps: feature engineering, weather-seasonal analysis, PV production modeling.

## 8. Screenshots (to insert)
- Dashboard UI: `dashboard_screenshots/` (add after running `streamlit run app.py`).
- Selected EDA plots from notebooks (time series, boxplots, correlation heatmap).

## 9. Reproducibility
- Environment: Python 3.11+, `requirements.txt`.
- Data: place the three CSVs under `data/` (ignored by git).
- Scripts:
  - Baseline: `python src/model_baseline.py`
  - Cleaned CSVs: `python src/clean_countries.py`
  - Country stats + tests: `python src/summarize_countries.py` (writes `metrics/country_summary.json`)
  - Streamlit: `streamlit run app.py`

## 10. Acknowledgements
- References: Day1–Day3 tutorials (used as guidance only), KAIM instructions and sample blueprint.

Convert this file to PDF for final submission after adding screenshots.
