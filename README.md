# Solar Data Discovery — Week 0 Challenge

A lightweight, reproducible repository for KAIM 10 Academy Week 0: Solar Data Discovery — from setup to an optional Streamlit dashboard.

## Repo structure
- `src/` — Python package for data prep, features, and utilities
- `notebooks/` — EDA and exploration notebooks (empty for now)
- `app/` — Streamlit app (to be added)
- `tests/` — Minimal tests (to be added)
- `data/` — Ignored by git. Place your local datasets here (e.g., per-country CSVs)

## Quick setup
Using a local virtual environment (no activation required in commands):

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt  # (Optional: we’ll add later) or install packages individually
```

Current core packages installed in the workspace env:
- numpy, pandas, matplotlib, seaborn, scikit-learn
- jupyter, pvlib, streamlit, plotly
- python-dotenv, requests

## Data
- The `data/` folder is ignored by git to keep the repo lean.
- Put your datasets under `data/` (e.g., `data/country_A_sales.csv`, etc.).
- We will document provenance and download/placement steps as we proceed.

## How to run (quick)
- Jupyter (EDA):
  ```bash
  ./.venv/bin/jupyter lab
  ```
- Streamlit (dashboard, when added):
  ```bash
  ./.venv/bin/streamlit run app/main.py
  ```

## Next steps
- [ ] Add data ingestion script(s) under `src/` and document data provenance
- [ ] Create initial EDA notebook in `notebooks/`
- [ ] Implement preprocessing/feature engineering in `src/`
- [ ] Baseline model and evaluation
- [ ] Build Streamlit dashboard under `app/`
