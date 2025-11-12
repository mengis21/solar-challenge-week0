import sys
import os
import pandas as pd
import streamlit as st

if "src" not in sys.path:
    sys.path.append("src")

from ingest import load_all  # type: ignore
import preprocess  # type: ignore

st.set_page_config(page_title="Solar Cross-Country Explorer", layout="wide")
st.title("Solar Data Explorer")
st.caption("Quick interactive view of irradiance and weather metrics across countries.")

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
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
        df = pd.concat(frames, ignore_index=True)
    else:
        df = load_all(data_dir)
        df = preprocess.quick_preprocess(df)
    return df

df = load_data()

countries = sorted(df["country"].dropna().unique().tolist())
selected = st.multiselect("Select countries", countries, default=countries[:2])

metric = st.selectbox("Metric", ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"], index=0)

sub = df[df["country"].isin(selected)].copy()

st.subheader("Summary Table")
summary = (
    sub.groupby("country")[metric]
    .agg(["count", "mean", "median", "std"])
    .round(2)
)
st.dataframe(summary)

st.subheader("Distribution")
import plotly.express as px  # noqa: E402
fig_hist = px.histogram(sub, x=metric, color="country", nbins=40, opacity=0.6)
st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Time Series (sample)")
sample = sub.sort_values("Timestamp").groupby("country").head(3000)
fig_line = px.line(sample, x="Timestamp", y=metric, color="country")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader(f"Country Ranking by Mean {metric}")
rank = summary["mean"].sort_values(ascending=False)
st.bar_chart(rank)

st.caption("Data loaded locally; CSVs are ignored in git. This is a minimal demo.")
