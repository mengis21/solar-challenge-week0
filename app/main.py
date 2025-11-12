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
    df = load_all("data")
    df = preprocess.quick_preprocess(df)
    return df

df = load_data()

countries = sorted(df["country"].dropna().unique().tolist())
selected = st.multiselect("Select countries", countries, default=countries[:2])

metric = st.selectbox("Metric", ["GHI", "DNI", "DHI", "Tamb", "RH", "WS"])

sub = df[df["country"].isin(selected)].copy()

st.subheader("Summary Table")
summary = (
    sub.groupby("country")[metric]
    .agg(["count", "mean", "median", "std"])
    .round(2)
)
st.dataframe(summary)

st.subheader("Distribution")
import plotly.express as px  # lazy import inside Streamlit
fig_hist = px.histogram(sub, x=metric, color="country", nbins=40, opacity=0.6)
st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Time Series (sample)")
sample = sub.sort_values("Timestamp").groupby("country").head(3000)
fig_line = px.line(sample, x="Timestamp", y=metric, color="country")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Country Ranking by Mean {}".format(metric))
rank = summary["mean"].sort_values(ascending=False)
st.bar_chart(rank)

st.caption("Data loaded locally; CSVs are ignored in git. This is a minimal demo.")
