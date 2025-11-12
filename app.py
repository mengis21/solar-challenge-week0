import sys
import os
import pandas as pd
import streamlit as st
import plotly.express as px

if "src" not in sys.path:
    sys.path.append("src")

from ingest import load_all  # type: ignore
import preprocess  # type: ignore

st.set_page_config(page_title="Solar Cross-Country Explorer", layout="wide")
st.title("Solar Data Explorer")
st.write("Upload CSVs to compare datasets side-by-side, or use local data if no files are uploaded.")

# Sidebar uploaders similar to the provided sample
st.sidebar.header("Upload Your Data (optional)")
col1, col2 = st.sidebar.columns(2)
with col1:
    uploaded_a = st.file_uploader("Dataset A CSV", type="csv", key="file_a")
with col2:
    uploaded_b = st.file_uploader("Dataset B CSV", type="csv", key="file_b")


def try_parse_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "Timestamp" in out.columns and not pd.api.types.is_datetime64_any_dtype(out["Timestamp"]):
        out["Timestamp"] = pd.to_datetime(out["Timestamp"], errors="coerce")
    return out


@st.cache_data(show_spinner=False)
def load_local_data() -> pd.DataFrame:
    # Prefer cleaned CSVs if available; otherwise, load raw and preprocess
    data_dir = "data"
    cleaned_files = [
        os.path.join(data_dir, f)
        for f in ("benin_clean.csv", "sierraleone_clean.csv", "togo_clean.csv")
    ]
    if all(os.path.exists(p) for p in cleaned_files):
        frames = []
        for p in cleaned_files:
            c = os.path.basename(p).split("_")[0]
            d = pd.read_csv(p, parse_dates=["Timestamp"], low_memory=False)
            d["country"] = c
            frames.append(d)
        return pd.concat(frames, ignore_index=True)
    df = load_all(data_dir)
    return preprocess.quick_preprocess(df)


def render_single_dashboard(df: pd.DataFrame, label: str) -> None:
    st.subheader(f"Summary – {label}")
    # choose an available metric
    numeric_cols = [c for c in ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"] if c in df.columns]
    if not numeric_cols:
        st.warning("No expected metrics found. Ensure columns like GHI/DNI/DHI/Tamb/RH/WS exist.")
        st.dataframe(df.head())
        return
    metric = st.selectbox(f"Metric ({label})", numeric_cols, key=f"metric_{label}")

    # summary table
    st.write(df[[metric]].describe().T.round(2))

    # histogram
    st.plotly_chart(px.histogram(df, x=metric, nbins=40, title=f"{label} – {metric} distribution"), use_container_width=True)

    # time series sample
    dfts = try_parse_timestamp(df)
    if "Timestamp" in dfts.columns:
        sample = dfts.sort_values("Timestamp").head(3000)
        st.plotly_chart(px.line(sample, x="Timestamp", y=metric, title=f"{label} – {metric} over time (sample)"), use_container_width=True)

    with st.expander(f"Show data – {label}"):
        st.dataframe(df)


def render_compare_dashboard(df_a: pd.DataFrame, df_b: pd.DataFrame, label_a: str = "A", label_b: str = "B") -> None:
    st.header("Side-by-Side Comparison")

    # Decide common metric set
    base_metrics = ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"]
    metrics_a = [c for c in base_metrics if c in df_a.columns]
    metrics_b = [c for c in base_metrics if c in df_b.columns]
    metrics = [m for m in base_metrics if m in metrics_a and m in metrics_b]
    if not metrics:
        st.warning("No overlapping metrics between the two datasets.")
        return
    metric = st.selectbox("Select a metric to compare:", metrics)

    # KPIs
    kpi_col1, kpi_col2 = st.columns(2)
    with kpi_col1:
        st.metric(label=f"Dataset {label_a} Mean {metric}", value=f"{df_a[metric].mean():.2f}")
    with kpi_col2:
        st.metric(label=f"Dataset {label_b} Mean {metric}", value=f"{df_b[metric].mean():.2f}")

    # Combine with identifier
    dfa = df_a.copy(); dfa["dataset"] = f"Dataset {label_a}"
    dfb = df_b.copy(); dfb["dataset"] = f"Dataset {label_b}"
    both = pd.concat([dfa, dfb], ignore_index=True)

    # Monthly comparison (requires Timestamp)
    both_ts = try_parse_timestamp(both)
    if "Timestamp" in both_ts.columns:
        both_ts["Month"] = both_ts["Timestamp"].dt.to_period("M").astype(str)
        fig = px.bar(both_ts, x="Month", y=metric, color="dataset", barmode="group", title=f"Monthly {metric} Comparison")
        st.plotly_chart(fig, use_container_width=True)

    # Distribution comparison
    fig_hist = px.histogram(both, x=metric, color="dataset", nbins=40, opacity=0.6, title=f"{metric} Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)

    # Data preview
    with st.expander("Show Combined Data"):
        st.dataframe(both)


# Branch: Uploaded vs Local
df_local = None
if uploaded_a is not None or uploaded_b is not None:
    try:
        if uploaded_a is not None:
            df_a = pd.read_csv(uploaded_a, low_memory=False)
            df_a = preprocess.quick_preprocess(df_a)
        else:
            df_a = None
        if uploaded_b is not None:
            df_b = pd.read_csv(uploaded_b, low_memory=False)
            df_b = preprocess.quick_preprocess(df_b)
        else:
            df_b = None
    except Exception as e:
        st.error(f"Error processing uploaded files: {e}")
        st.stop()

    if df_a is not None and df_b is not None:
        render_compare_dashboard(df_a, df_b, "A", "B")
    elif df_a is not None:
        render_single_dashboard(df_a, "A")
    elif df_b is not None:
        render_single_dashboard(df_b, "B")
    else:
        st.info("Please upload at least one CSV file to begin.")
else:
    # Fallback to local data flow (original behavior)
    df_local = load_local_data()
    countries = sorted(df_local.get("country", pd.Series(dtype=str)).dropna().unique().tolist())
    selected = st.multiselect("Select countries", countries, default=countries[:2] if len(countries) >= 2 else countries)
    metric = st.selectbox("Metric", [m for m in ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"] if m in df_local.columns], index=0)
    sub = df_local[df_local["country"].isin(selected)].copy() if selected else df_local.copy()

    st.subheader("Summary Table")
    summary = (
        sub.groupby("country")[metric]
        .agg(["count", "mean", "median", "std"])
        .round(2)
    )
    st.dataframe(summary)

    fig_hist = px.histogram(sub, x=metric, color="country", nbins=40, opacity=0.6, title=f"{metric} distribution by country")
    st.plotly_chart(fig_hist, use_container_width=True)

    sample = sub.sort_values("Timestamp").groupby("country").head(3000) if "Timestamp" in sub.columns else sub.head(3000)
    fig_line = px.line(sample, x="Timestamp" if "Timestamp" in sub.columns else sample.index, y=metric, color="country" if "country" in sample.columns else None, title="Time Series (sample)")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader(f"Country Ranking by Mean {metric}")
    rank = summary["mean"].sort_values(ascending=False)
    st.bar_chart(rank)

    st.caption("Data loaded locally; CSVs are ignored in git. Upload your own files to compare.")
