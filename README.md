# Solar Data Discovery — Week 0 Challenge

A lean, reproducible repository for KAIM Week 0: Solar Data Discovery — setup to dashboard.

## Repo structure
- `src/` — data ingestion, preprocessing, cleaning, summarization, baseline model
- `notebooks/` — per-country EDA and cross-country comparison
- `metrics/` — saved metrics and summaries (e.g., baseline.json, country_summary.json)
- `data/` — ignored by git. Place your local per-country CSVs and cleaned CSVs here
- `app.py` — Streamlit dashboard entry point
- `REPORT.md` — final report (convert to PDF)

## Quick setup
```
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
```

## Data
- Put the three country CSVs under `data/` (ignored by git).
- Cleaned files will be written as `data/benin_clean.csv`, `data/sierraleone_clean.csv`, `data/togo_clean.csv`.

## How to run
- Generate cleaned CSVs (optional, already done once):
```
./.venv/bin/python src/clean_countries.py
```
- Country stats and tests (for report):
```
./.venv/bin/python src/summarize_countries.py
```
- Baseline metrics:
```
./.venv/bin/python src/model_baseline.py
```
- Notebooks (EDA/comparison):
```
./.venv/bin/jupyter lab
```
- Streamlit dashboard:
```
./.venv/bin/streamlit run app.py
```

## Results (short)
- GHI mean ranking: Benin > Togo > Sierra Leone
- GHI tests: ANOVA p ≈ 0.0; Kruskal–Wallis p ≈ 0.0 (significant differences)
- Baseline best: RandomForest, test MAE ≈ 3.68, RMSE ≈ 7.84

## Notes
- Reference PDFs and tutorial folders are ignored by git and not part of the submission.
- Add dashboard screenshots to `dashboard_screenshots/` before finalizing.
