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
st.write("Upload up to three CSVs to compare side-by-side, or use local data if no files are uploaded.")

# Sidebar uploaders similar to the provided sample
st.sidebar.header("Upload Your Data (optional)")
uploaded_files = st.sidebar.file_uploader(
    "Upload up to 3 country CSV files",
    type="csv",
    accept_multiple_files=True,
)
if uploaded_files and len(uploaded_files) > 3:
    st.sidebar.warning("You uploaded more than 3 files. Only the first 3 will be used.")
    uploaded_files = uploaded_files[:3]


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


def render_multi_compare(dfs: list[pd.DataFrame], labels: list[str]) -> None:
    st.header("Multi-dataset Comparison")

    base_metrics = ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"]
    intersect = set(base_metrics)
    for d in dfs:
        intersect &= set([c for c in base_metrics if c in d.columns])
    metrics = sorted(list(intersect))
    if not metrics:
        st.warning("No overlapping metrics across uploaded datasets.")
        return
    metric = st.selectbox("Select a metric to compare:", metrics)

    # Combine with identifier
    frames = []
    for d, lab in zip(dfs, labels):
        x = d.copy()
        x["dataset"] = lab
        frames.append(x)
    both = pd.concat(frames, ignore_index=True)

    # KPIs
    kpi_cols = st.columns(len(dfs))
    for i, lab in enumerate(labels):
        val = both.loc[both["dataset"] == lab, metric].mean()
        with kpi_cols[i]:
            st.metric(label=f"{lab} Mean {metric}", value=f"{val:.2f}")

    # Monthly comparison (requires Timestamp)
    both_ts = try_parse_timestamp(both)
    if "Timestamp" in both_ts.columns:
        both_ts["Month"] = both_ts["Timestamp"].dt.to_period("M").astype(str)
        fig = px.bar(
            both_ts, x="Month", y=metric, color="dataset", barmode="group",
            title=f"Monthly {metric} Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Distribution comparison
    fig_hist = px.histogram(both, x=metric, color="dataset", nbins=40, opacity=0.6, title=f"{metric} Distribution")
    st.plotly_chart(fig_hist, use_container_width=True)

    # Time series sample (per dataset sample)
    both_ts2 = try_parse_timestamp(both)
    if "Timestamp" in both_ts2.columns:
        sample = both_ts2.sort_values("Timestamp").groupby("dataset").head(2000)
        fig_line = px.line(sample, x="Timestamp", y=metric, color="dataset", title="Time Series (sample)")
        st.plotly_chart(fig_line, use_container_width=True)

    with st.expander("Show Combined Data"):
        st.dataframe(both)


# Branch: Uploaded vs Local
df_local = None
if uploaded_files:
    dfs = []
    labels = []
    for i, uf in enumerate(uploaded_files, start=1):
        try:
            d = pd.read_csv(uf, low_memory=False)
            d = preprocess.quick_preprocess(d)
            # Prefer explicit 'country' if a single value; otherwise label by filename
            label = None
            if "country" in d.columns:
                unique_c = d["country"].dropna().unique()
                if len(unique_c) == 1:
                    label = str(unique_c[0])
            if not label:
                fname = getattr(uf, 'name', f'uploaded_{i}.csv')
                label = os.path.splitext(os.path.basename(fname))[0]
            dfs.append(d)
            labels.append(label)
        except Exception as e:
            st.error(f"Error processing file #{i}: {e}")
            st.stop()

    if len(dfs) == 1:
        render_single_dashboard(dfs[0], labels[0])
    else:
        render_multi_compare(dfs, labels)
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
