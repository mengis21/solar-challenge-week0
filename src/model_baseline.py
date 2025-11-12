import json
import os
import sys
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.impute import SimpleImputer


# allow 'from ingest import load_all' when run as a script
if "src" not in sys.path:
    sys.path.append("src")

from ingest import load_all  # type: ignore
import preprocess  # type: ignore


def prepare_data(target: str = "GHI", max_rows: int = 100_000) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, Dict]:
    df = load_all("data")
    df = preprocess.quick_preprocess(df)

    if target not in df.columns:
        raise ValueError(f"Target column not found: {target}")

    df = df.dropna(subset=[target]).reset_index(drop=True)

    # numeric features only, exclude target
    num_cols = df.select_dtypes("number").columns.tolist()
    feature_cols = [c for c in num_cols if c != target]
    X = df[feature_cols]
    y = df[target]

    # downsample to keep training fast
    if len(df) > max_rows:
        idx = np.random.RandomState(42).choice(len(df), size=max_rows, replace=False)
        X = X.iloc[idx].reset_index(drop=True)
        y = y.iloc[idx].reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # drop columns that are entirely NaN in train (cannot impute median)
    all_nan_cols = [c for c in X_train.columns if X_train[c].isna().all()]
    if all_nan_cols:
        X_train = X_train.drop(columns=all_nan_cols)
        X_test = X_test.drop(columns=[c for c in all_nan_cols if c in X_test.columns])
        feature_cols = [c for c in feature_cols if c not in all_nan_cols]

    # record missing counts before imputation
    missing_before_train = int(X_train.isna().sum().sum())
    missing_before_test = int(X_test.isna().sum().sum())

    # simple median imputation for any remaining NaNs
    imputer = SimpleImputer(strategy="median")
    X_train = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
    X_test = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)

    meta = {
        "rows_total": int(len(df)),
        "rows_used": int(len(X)),
        "n_features": int(len(feature_cols)),
        "target": target,
        "feature_cols_sample": feature_cols[:10],
        "missing_before_train": missing_before_train,
        "missing_before_test": missing_before_test,
        "imputer_strategy": "median",
    }
    return X_train, X_test, y_train, y_test, meta


def evaluate_models(X_train, X_test, y_train, y_test) -> Dict:
    results = {}
    kfold = KFold(n_splits=3, shuffle=True, random_state=42)
    # Sample down for cross-validation
    max_cv_rows = 5000
    if len(X_train) > max_cv_rows:
        sample_idx = np.random.RandomState(42).choice(len(X_train), size=max_cv_rows, replace=False)
        X_cv = X_train.iloc[sample_idx]
        y_cv = y_train.iloc[sample_idx]
    else:
        X_cv = X_train
        y_cv = y_train

    # Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    pred_lr = lr.predict(X_test)
    mae_lr = float(mean_absolute_error(y_test, pred_lr))
    # Compute RMSE manually for broad sklearn compatibility
    rmse_lr = float(np.sqrt(mean_squared_error(y_test, pred_lr)))
    # cross-validation scores (negative metrics -> invert sign)
    cv_mae_lr = -cross_val_score(lr, X_cv, y_cv, cv=kfold, scoring="neg_mean_absolute_error", n_jobs=-1)
    # Older sklearn versions may not support "neg_root_mean_squared_error"
    cv_mse_lr = -cross_val_score(lr, X_cv, y_cv, cv=kfold, scoring="neg_mean_squared_error", n_jobs=-1)
    cv_rmse_lr = np.sqrt(cv_mse_lr)
    results["LinearRegression"] = {
        "MAE": mae_lr,
        "RMSE": rmse_lr,
        "CV_MAE_mean": float(cv_mae_lr.mean()),
    "CV_RMSE_mean": float(cv_rmse_lr.mean()),
    }

    # Random Forest
    rf = RandomForestRegressor(n_estimators=50, max_depth=15, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    pred_rf = rf.predict(X_test)
    mae_rf = float(mean_absolute_error(y_test, pred_rf))
    rmse_rf = float(np.sqrt(mean_squared_error(y_test, pred_rf)))
    cv_mae_rf = -cross_val_score(rf, X_cv, y_cv, cv=kfold, scoring="neg_mean_absolute_error", n_jobs=-1)
    cv_mse_rf = -cross_val_score(rf, X_cv, y_cv, cv=kfold, scoring="neg_mean_squared_error", n_jobs=-1)
    cv_rmse_rf = np.sqrt(cv_mse_rf)
    results["RandomForestRegressor"] = {
        "MAE": mae_rf,
        "RMSE": rmse_rf,
        "CV_MAE_mean": float(cv_mae_rf.mean()),
        "CV_RMSE_mean": float(cv_rmse_rf.mean()),
    }

    # pick best by RMSE
    best_model = min(results.items(), key=lambda kv: kv[1]["RMSE"])[0]
    results["best_model"] = best_model
    results["cv_sample_size"] = int(len(X_cv))
    return results


def save_metrics(metrics: Dict, meta: Dict, out_dir: str = "metrics", name: str = "baseline.json") -> str:
    os.makedirs(out_dir, exist_ok=True)
    payload = {"metrics": metrics, "meta": meta}
    out_path = os.path.join(out_dir, name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return out_path


def main() -> None:
    X_train, X_test, y_train, y_test, meta = prepare_data(target="GHI", max_rows=100_000)
    results = evaluate_models(X_train, X_test, y_train, y_test)
    out_path = save_metrics(results, meta)
    print(f"Saved metrics -> {out_path}")
    print(json.dumps({"meta": meta, "metrics": results}, indent=2))


if __name__ == "__main__":
    main()
