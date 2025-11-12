# Solar Data Discovery — Week 0 Challenge

Arepository for KAIM Week 0: Solar Data Discovery

## ABOUT M3
```
____________________________________________________________________________________
|                  10 Academy Week 0 — Solar Data Discovery Challenge               |
|-----------------------------------------------------------------------------------|
| Name: Kidus Mengistu Gebremedhin            Status: Final Assignment Submission   |
| Cohort: Week 0 			         		  Due Date: Nov 12, 2025				    |
|																					|
| Project: Cross-country solar farm exploratory analysis (Benin, Sierra Leone, Togo)|
------------------------------------------------------------------------------------
```

## Repo structure
- `src/` — data ingestion, preprocessing, cleaning, summarization, baseline model
- `notebooks/` — per-country EDA and cross-country comparison
- `metrics/` — saved metrics and summaries (e.g., baseline.json, country_summary.json)
- `data/` — ignored by git. Holds per-country CSVs and cleaned CSVs
- `dashboard_screenshots`    # Screenshot of the Deployed dashboard
- `app.py` — Streamlit dashboard entry point
- `.github/workflows/`    # CI workflows

## Quick setup
```
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt
```

## Data
- Put the three country CSVs under `data/` (ignored by git).
- Cleaned files will be written as `data/benin_clean.csv`, `data/sierraleone_clean.csv`, `data/togo_clean.csv`.

## How to run (Assuming all requirments are installed)
- Generate cleaned CSVs:
```
./.venv/bin/python src/clean_countries.py
```
- Country stats and tests:
```
./.venv/bin/python src/summarize_countries.py
```
- Baseline metrics:
```
./.venv/bin/python src/model_baseline.py

```
- Streamlit dashboard:
```
./.venv/bin/streamlit run app.py
```

## Results (short)
- GHI mean ranking: Benin > Togo > Sierra Leone
- GHI tests: ANOVA p ≈ 0.0; Kruskal–Wallis p ≈ 0.0 (significant differences)
- Baseline best: RandomForest, test MAE ≈ 3.68, RMSE ≈ 7.84

## References
1. Gueymard, C. A. (2019). A review of validation methodologies and statistical performance indicators for solar radiation models. Solar Energy, 191, 300–333. https://doi.org/10.1016/j.solener.2019.09.006
2. Virtanen, P., et al. (2020). SciPy 1.0. Nature Methods, 17, 261–272.
3. Waskom, M. (2021). seaborn. JOSS, 6(60), 3021.
4. Python Windrose Library. URL:https://github.com/python-windrose/windrose
5. Day1–Day3 tutorials (used as blueprint), KAIM instructions and sample blueprint.


### AI Assistance Disclosure
I used ChatGPT (OpenAI, accessed 9 Nov 2025) to assist with wording, code scaffolding, and documentation structure. All analysis and final decisions are my own.
