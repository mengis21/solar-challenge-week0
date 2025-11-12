# Solar Data Discovery – Week 0 Final Report (Draft)

Short, clear, and practical. This draft follows our style and can be converted to PDF.

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

## 4. Key Findings (to be refined after notebook runs)
- [Placeholder] Country with highest median GHI: ...
- [Placeholder] Variability notes: ...
- [Placeholder] Cleaning impact on ModA/ModB: ...

## 5. Cross-Country Comparison
- Boxplots: GHI, DNI, DHI by country.
- Summary table: mean/median/std per metric and country.
- Optional tests: ANOVA and Kruskal on GHI.

Results snapshot:
- [Placeholder] ANOVA p-value: ... (significant if p < 0.05)
- [Placeholder] Ranking by average GHI: ...

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
  - Streamlit: `streamlit run app.py`

## 10. Acknowledgements
- References: Day1–Day3 tutorials (used as guidance only), KAIM instructions and sample blueprint.

*** End of Draft ***
*** Replace placeholders after running notebooks and capturing visuals. ***
*** Convert this file to PDF as final submission. ***
