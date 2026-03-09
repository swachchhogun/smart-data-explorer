import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import requests

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DataLens",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"   # collapsed by default → mobile friendly
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES  (fully responsive)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,90,50,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(80,180,255,0.05) 0%, transparent 60%),
        #0a0a0f !important;
}
[data-testid="stSidebar"] {
    background: #0d0d16 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #e8e4dc !important; }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Responsive padding ── */
.block-container {
    padding: 1.5rem 1.25rem 4rem !important;
    max-width: 1400px !important;
}
@media (min-width: 768px) {
    .block-container { padding: 2rem 2.5rem 4rem !important; }
}

/* ── Hero ── */
.hero {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 2rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 4px; text-transform: uppercase;
    color: #ff5a32; margin-bottom: 0.6rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(38px, 10vw, 80px);
    font-weight: 800; line-height: 0.92; letter-spacing: -2px;
    color: #f0ece4; margin: 0 0 0.75rem;
}
.hero-title span { color: #ff5a32; }
.hero-sub {
    font-family: 'DM Sans', sans-serif; font-size: 14px;
    color: rgba(232,228,220,0.4); font-weight: 300;
    max-width: 480px; line-height: 1.7;
}

/* ── Upload zone (shown when no file) ── */
.upload-zone {
    border: 1px dashed rgba(255,255,255,0.12);
    background: #0f0f18;
    padding: 3rem 1.5rem;
    text-align: center;
    margin: 1.5rem 0;
    border-radius: 2px;
}
.upload-title {
    font-family: 'Syne', sans-serif; font-size: clamp(20px, 5vw, 28px);
    font-weight: 700; color: #f0ece4; margin-bottom: 0.5rem; letter-spacing: -0.5px;
}
.upload-sub {
    font-family: 'DM Mono', monospace; font-size: 10px;
    letter-spacing: 2px; color: rgba(232,228,220,0.25); text-transform: uppercase;
}

/* ── Metrics grid — 2 cols mobile, 5 cols desktop ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2rem;
    overflow: hidden;
}
@media (min-width: 600px) {
    .metrics-row { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 900px) {
    .metrics-row { grid-template-columns: repeat(5, 1fr); }
}
.metric-card {
    background: #0f0f18;
    padding: 1.2rem 1.25rem;
    position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #ff5a32, transparent); opacity: 0; transition: opacity 0.3s;
}
.metric-card:hover::before { opacity: 1; }
.metric-label {
    font-family: 'DM Mono', monospace; font-size: 9px;
    letter-spacing: 2px; text-transform: uppercase;
    color: rgba(232,228,220,0.3); margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'Syne', sans-serif; font-size: clamp(24px, 5vw, 34px);
    font-weight: 800; color: #f0ece4; line-height: 1; letter-spacing: -1px;
}
.metric-value span {
    font-size: 10px; font-weight: 400; letter-spacing: 0;
    color: rgba(232,228,220,0.3); font-family: 'DM Mono', monospace; margin-left: 2px;
}
.metric-sub {
    font-family: 'DM Mono', monospace; font-size: 9px;
    color: #ff5a32; margin-top: 3px; letter-spacing: 0.5px;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Mono', monospace; font-size: 9px;
    letter-spacing: 4px; text-transform: uppercase; color: #ff5a32;
    margin-bottom: 1rem; display: flex; align-items: center; gap: 10px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.07); }

/* ── Inputs ── */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #0f0f18 !important; border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e8e4dc !important; font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #ff5a32 !important; box-shadow: 0 0 0 1px #ff5a32 !important;
}
.stSelectbox label, .stMultiSelect label, .stTextInput label {
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    color: rgba(232,228,220,0.4) !important;
}
.stTextInput input {
    background: #0f0f18 !important; border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e8e4dc !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;          /* bigger for mobile tap */
}
.stTextInput input:focus { border-color: #ff5a32 !important; box-shadow: 0 0 0 1px #ff5a32 !important; }

/* ── Buttons ── */
.stButton > button {
    background: transparent !important; border: 1px solid rgba(255,255,255,0.15) !important;
    color: #e8e4dc !important; font-family: 'DM Mono', monospace !important;
    font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important;
    padding: 0.7rem 1.4rem !important; transition: all 0.2s !important;
    width: 100% !important;              /* full width on mobile */
}
.stButton > button:hover { background: #ff5a32 !important; border-color: #ff5a32 !important; color: white !important; }
.stDownloadButton > button {
    background: rgba(255,90,50,0.1) !important; border: 1px solid rgba(255,90,50,0.3) !important;
    color: #ff5a32 !important; font-family: 'DM Mono', monospace !important;
    font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important;
    padding: 0.7rem 1.4rem !important; transition: all 0.2s !important;
    width: 100% !important;
}
.stDownloadButton > button:hover { background: #ff5a32 !important; color: white !important; }

/* ── File uploader — make it big and obvious on mobile ── */
[data-testid="stFileUploader"] {
    background: #0f0f18 !important;
    border: 1px dashed rgba(255,90,50,0.3) !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] * { color: #e8e4dc !important; }
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    padding: 1.5rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] div {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important; letter-spacing: 1px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 0 !important; overflow-x: auto !important;   /* scrollable on mobile */
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: rgba(232,228,220,0.35) !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    border: none !important; padding: 0.75rem 1rem !important;
    white-space: nowrap !important;
}
.stTabs [aria-selected="true"] { color: #ff5a32 !important; border-bottom: 2px solid #ff5a32 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

/* ── Data frame ── */
.stDataFrame { border: 1px solid rgba(255,255,255,0.06) !important; }

/* ── Insight cards ── */
.insight-card {
    background: #0f0f18; border: 1px solid rgba(255,255,255,0.06);
    border-left: 2px solid #ff5a32; padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem; font-family: 'DM Sans', sans-serif;
    font-size: 14px; color: rgba(232,228,220,0.7); line-height: 1.7;
}
.insight-card strong { color: #f0ece4; font-weight: 500; }
.insight-icon {
    font-family: 'DM Mono', monospace; font-size: 9px;
    color: #ff5a32; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 0.4rem;
}

/* ── AI card ── */
.ai-card {
    background: linear-gradient(135deg, #0f0f18 0%, #12101f 100%);
    border: 1px solid rgba(255,90,50,0.2); padding: 1.5rem;
    margin-top: 1rem; position: relative;
}
.ai-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, #ff5a32, transparent 60%);
}
.ai-card-label {
    font-family: 'DM Mono', monospace; font-size: 9px;
    letter-spacing: 3px; text-transform: uppercase; color: #ff5a32; margin-bottom: 1rem;
}
.ai-card-text {
    font-family: 'DM Sans', sans-serif; font-size: 14px;
    color: rgba(232,228,220,0.8); line-height: 1.8; white-space: pre-wrap;
}

/* ── Clean badge ── */
.clean-badge {
    display: inline-block; background: rgba(168,224,99,0.1);
    border: 1px solid rgba(168,224,99,0.25); color: #a8e063;
    font-family: 'DM Mono', monospace; font-size: 9px;
    letter-spacing: 1px; text-transform: uppercase; padding: 3px 8px; margin: 3px;
}

/* ── Stats table — horizontally scrollable on mobile ── */
.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.stats-table { width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace; font-size: 11px; min-width: 600px; }
.stats-table th {
    background: rgba(255,90,50,0.08); color: #ff5a32; letter-spacing: 2px;
    text-transform: uppercase; padding: 10px 12px; text-align: left;
    border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 9px; white-space: nowrap;
}
.stats-table td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); color: rgba(232,228,220,0.7); white-space: nowrap; }
.stats-table tr:hover td { background: rgba(255,255,255,0.02); color: #e8e4dc; }
.stats-table .col-name { color: #f0ece4; font-weight: 500; }

hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }
.stAlert { background: rgba(255,90,50,0.07) !important; border: 1px solid rgba(255,90,50,0.18) !important; color: #e8e4dc !important; }

/* ── Sidebar brand ── */
.sidebar-brand {
    font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800;
    color: #f0ece4; letter-spacing: -0.5px; padding: 1.5rem 0 0.2rem;
}
.sidebar-brand span { color: #ff5a32; }
.sidebar-tagline {
    font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 3px;
    color: rgba(232,228,220,0.2); text-transform: uppercase; margin-bottom: 1.5rem;
}

/* ── Toggle ── */
.stToggle label { font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 1px !important; text-transform: uppercase !important; color: rgba(232,228,220,0.5) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
COLORS = ["#ff5a32", "#50b4ff", "#a8e063", "#f7c948", "#c678dd", "#56b6c2", "#e06c75", "#d19a66"]

def style_fig(fig, mobile=False):
    margin = dict(l=8, r=8, t=44, b=8) if mobile else dict(l=20, r=20, t=50, b=20)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d16",
        font=dict(family="DM Sans", color="#e8e4dc", size=11),
        title_font=dict(family="Syne", size=15, color="#f0ece4"),
        colorway=COLORS,
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.07)",
            tickfont=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)"),
            title_font=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)"),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.07)",
            tickfont=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)"),
            title_font=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.45)"),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        margin=margin,
        hoverlabel=dict(bgcolor="#0f0f18", font_family="DM Mono", font_size=11, bordercolor="rgba(255,90,50,0.3)"),
    )
    return fig

# ─────────────────────────────────────────────
#  HELPERS — responsive columns
# ─────────────────────────────────────────────
def r_cols(n, weights=None):
    """On mobile Streamlit columns still render side by side — we keep
    them but always use full-width charts so they adapt naturally."""
    if weights:
        return st.columns(weights)
    return st.columns(n)

# ─────────────────────────────────────────────
#  DATA CLEANING
# ─────────────────────────────────────────────
def smart_clean(df: pd.DataFrame):
    report = []
    cleaned = df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]

    for col in cleaned.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(cleaned[col], infer_datetime_format=True, errors="coerce")
            if parsed.notna().mean() > 0.7:
                cleaned[col] = parsed
                report.append(f"Parsed '{col}' as datetime")
        except Exception:
            pass

    for col in cleaned.select_dtypes(include="object").columns:
        cleaned[col] = cleaned[col].str.strip()

    for col in cleaned.select_dtypes(include="number").columns:
        n = cleaned[col].isnull().sum()
        if n > 0:
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
            report.append(f"Filled {n} nulls in '{col}' with median")

    for col in cleaned.select_dtypes(include="object").columns:
        n = cleaned[col].isnull().sum()
        if n > 0 and not cleaned[col].mode().empty:
            cleaned[col] = cleaned[col].fillna(cleaned[col].mode()[0])
            report.append(f"Filled {n} nulls in '{col}' with mode")

    before = len(cleaned)
    cleaned = cleaned.dropna(how="all").dropna(axis=1, how="all")
    if before - len(cleaned) > 0:
        report.append(f"Removed {before - len(cleaned)} empty rows")

    n_dupes = cleaned.duplicated().sum()
    if n_dupes > 0:
        cleaned = cleaned.drop_duplicates()
        report.append(f"Removed {n_dupes} duplicate rows")

    return cleaned, report

# ─────────────────────────────────────────────
#  AI INSIGHTS
# ─────────────────────────────────────────────
def get_ai_insights(df: pd.DataFrame, question: str = "") -> str:
    numeric_df = df.select_dtypes(include="number")
    cat_df = df.select_dtypes(include="object")
    summary = {
        "shape": list(df.shape),
        "columns": list(df.columns),
        "numeric_stats": numeric_df.describe().round(2).to_dict() if len(numeric_df.columns) > 0 else {},
        "categorical_top": {col: df[col].value_counts().head(3).to_dict() for col in cat_df.columns[:4]},
        "missing": df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
    }
    prompt = f"""You are a data analyst. Analyze this dataset summary and provide clear, actionable insights.

Dataset Summary:
{json.dumps(summary, indent=2, default=str)}

{"User question: " + question if question else "Provide 4-5 key insights about patterns, outliers, distributions, and interesting findings. Be specific with numbers."}

Be concise, specific, and use plain language suitable for both technical and non-technical users. Format with clear numbered points."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        return response.json()["content"][0]["text"]
    except Exception as e:
        return f"AI insights unavailable: {str(e)}\n\nMake sure your Anthropic API key is set in Streamlit secrets."

# ─────────────────────────────────────────────
#  SIDEBAR  (filters + mode — hidden by default on mobile)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Data<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">◈ Smart Explorer</div>', unsafe_allow_html=True)

    if "working_df" in st.session_state and st.session_state.working_df is not None:
        wdf = st.session_state.working_df
        numeric_cols_sb = wdf.select_dtypes(include="number").columns.tolist()
        cat_cols_sb = wdf.select_dtypes(include="object").columns.tolist()

        st.markdown("---")
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:rgba(232,228,220,0.3);margin-bottom:0.75rem;">Filters</div>', unsafe_allow_html=True)

        filtered_override = wdf.copy()
        for col in cat_cols_sb[:3]:
            opts = st.multiselect(col, wdf[col].dropna().unique(), key=f"sb_f_{col}")
            if opts:
                filtered_override = filtered_override[filtered_override[col].isin(opts)]

        for col in numeric_cols_sb[:2]:
            cmin, cmax = float(wdf[col].min()), float(wdf[col].max())
            if cmin < cmax:
                rng = st.slider(col, cmin, cmax, (cmin, cmax), key=f"sb_r_{col}")
                filtered_override = filtered_override[filtered_override[col].between(*rng)]

        st.session_state.filtered_df = filtered_override

        st.markdown("---")
        st.download_button(
            "↓ Export CSV",
            data=filtered_override.to_csv(index=False).encode("utf-8"),
            file_name="datalens_export.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("Upload a CSV on the main page to start filtering.")

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">◈ Smart Data Explorer</div>
    <div class="hero-title">Data<span>Lens</span></div>
    <div class="hero-sub">Drop in any CSV — auto-clean, explore, visualise, and get AI-powered insights.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILE UPLOAD  — always in the main page body
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Your Data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"],
    label_visibility="collapsed",
    help="Drag & drop or tap to browse — any CSV file"
)

if uploaded_file is None:
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-title">Tap above to upload a CSV</div>
        <div class="upload-sub">Any CSV · Auto-cleaned · AI insights · Works on mobile</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.working_df = None
    st.stop()

# ─────────────────────────────────────────────
#  LOAD & CLEAN
# ─────────────────────────────────────────────
raw_df = pd.read_csv(uploaded_file)
cleaned_df, clean_report = smart_clean(raw_df)

use_cleaned = st.toggle("Auto-clean data", value=True,
                        help="Fills nulls, parses dates, removes duplicates")
working_df = cleaned_df if use_cleaned else raw_df
st.session_state.working_df = working_df

# Use sidebar-filtered df if available, else working_df
if "filtered_df" in st.session_state and st.session_state.filtered_df is not None:
    try:
        filtered_df = st.session_state.filtered_df
        # Validate it still matches current file
        if list(filtered_df.columns) != list(working_df.columns):
            filtered_df = working_df.copy()
    except Exception:
        filtered_df = working_df.copy()
else:
    filtered_df = working_df.copy()

numeric_cols = working_df.select_dtypes(include="number").columns.tolist()
cat_cols = working_df.select_dtypes(include="object").columns.tolist()
date_cols = working_df.select_dtypes(include=["datetime64"]).columns.tolist()

# Cleaning report
if clean_report and use_cleaned:
    with st.expander("✦ Cleaning applied — tap to see details"):
        for note in clean_report:
            st.markdown(f'<span class="clean-badge">✓ {note}</span>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────
missing_count = filtered_df.isnull().sum().sum()
dupe_count = filtered_df.duplicated().sum()
completeness = round((1 - missing_count / max(filtered_df.size, 1)) * 100, 1)

st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-label">Rows</div>
        <div class="metric-value">{filtered_df.shape[0]:,}<span>r</span></div>
        <div class="metric-sub">of {working_df.shape[0]:,}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Columns</div>
        <div class="metric-value">{filtered_df.shape[1]}<span>c</span></div>
        <div class="metric-sub">{len(numeric_cols)} num · {len(cat_cols)} cat</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Complete</div>
        <div class="metric-value">{completeness}<span>%</span></div>
        <div class="metric-sub">{missing_count} nulls</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Dupes</div>
        <div class="metric-value">{dupe_count}<span>r</span></div>
        <div class="metric-sub">{"none" if dupe_count == 0 else "found"}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Memory</div>
        <div class="metric-value">{filtered_df.memory_usage(deep=True).sum() / 1024:.0f}<span>kb</span></div>
        <div class="metric-sub">in memory</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ANALYSIS MODE  (selectbox in main body — visible on mobile)
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Analysis Mode</div>', unsafe_allow_html=True)
analysis_type = st.selectbox(
    "Choose what to explore",
    ["Dashboard Overview", "Distribution Analysis", "Category Comparison",
     "Correlation Analysis", "Trend Over Time", "Scatter Explorer"],
    label_visibility="collapsed"
)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_explore, tab_stats, tab_ai = st.tabs(["◈  Explore", "◈  Statistics", "◈  AI Insights"])

# ════════════════════════════════
#  TAB 1 — EXPLORE
# ════════════════════════════════
with tab_explore:

    st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df.head(8), use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{analysis_type}</div>', unsafe_allow_html=True)

    # ── DASHBOARD OVERVIEW ──
    if analysis_type == "Dashboard Overview":
        if len(numeric_cols) > 0:
            col_sel = st.selectbox("Numeric column", numeric_cols, key="dash_num")
            chart_type = st.selectbox("Chart type", ["Histogram", "Box Plot", "Violin"], key="dash_chart")

            if chart_type == "Histogram":
                fig = px.histogram(filtered_df, x=col_sel, nbins=30, title=f"Distribution · {col_sel}")
                fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.3)", marker_line_width=1)
            elif chart_type == "Box Plot":
                fig = px.box(filtered_df, y=col_sel, title=f"Box Plot · {col_sel}")
                fig.update_traces(marker_color="#ff5a32", line_color="#50b4ff")
            else:
                fig = px.violin(filtered_df, y=col_sel, title=f"Violin · {col_sel}", box=True)
                fig.update_traces(fillcolor="rgba(255,90,50,0.15)", line_color="#ff5a32")
            st.plotly_chart(style_fig(fig), use_container_width=True)

        if len(cat_cols) > 0 and len(numeric_cols) > 0:
            st.markdown("<hr>", unsafe_allow_html=True)
            cat = st.selectbox("Category column", cat_cols, key="dash_cat")
            num = st.selectbox("Numeric column", numeric_cols, key="dash_num2")
            agg = st.selectbox("Aggregation", ["Mean", "Sum", "Median", "Count"], key="dash_agg")
            agg_fn = {"Mean": "mean", "Sum": "sum", "Median": "median", "Count": "count"}[agg]
            grouped = filtered_df.groupby(cat)[num].agg(agg_fn).reset_index().sort_values(num, ascending=False).head(20)
            fig2 = px.bar(grouped, x=cat, y=num, title=f"{agg} of {num} by {cat}")
            fig2.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.2)", marker_line_width=1)
            st.plotly_chart(style_fig(fig2), use_container_width=True)

    # ── DISTRIBUTION ──
    elif analysis_type == "Distribution Analysis":
        if len(numeric_cols) == 0:
            st.warning("No numeric columns found.")
        else:
            column = st.selectbox("Numeric Column", numeric_cols, key="dist_col")
            color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="dist_color")
            color_arg = None if color_by == "None" else color_by

            fig = px.histogram(filtered_df, x=column, color=color_arg, nbins=30,
                               title=f"Histogram · {column}", barmode="overlay", opacity=0.8)
            if color_arg is None:
                fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.3)", marker_line_width=1)
            st.plotly_chart(style_fig(fig), use_container_width=True)

            fig2 = px.violin(filtered_df, y=column, color=color_arg, title=f"Violin · {column}", box=True)
            if color_arg is None:
                fig2.update_traces(fillcolor="rgba(255,90,50,0.15)", line_color="#ff5a32")
            st.plotly_chart(style_fig(fig2), use_container_width=True)

    # ── CATEGORY COMPARISON ──
    elif analysis_type == "Category Comparison":
        if len(cat_cols) == 0 or len(numeric_cols) == 0:
            st.warning("Need both categorical and numeric columns.")
        else:
            cat = st.selectbox("Category", cat_cols, key="cat_cat")
            num = st.selectbox("Numeric", numeric_cols, key="cat_num")
            agg = st.selectbox("Aggregation", ["Mean", "Sum", "Median", "Count"], key="cat_agg")
            chart = st.selectbox("Chart type", ["Bar", "Treemap", "Pie"], key="cat_chart")

            agg_fn = {"Mean": "mean", "Sum": "sum", "Median": "median", "Count": "count"}[agg]
            grouped = filtered_df.groupby(cat)[num].agg(agg_fn).reset_index().sort_values(num, ascending=True)

            if chart == "Bar":
                fig = px.bar(grouped, x=num, y=cat, orientation="h", title=f"{agg} of {num} by {cat}")
                fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.2)", marker_line_width=1)
            elif chart == "Treemap":
                fig = px.treemap(grouped, path=[cat], values=num, title=f"{agg} of {num} by {cat}",
                                 color=num, color_continuous_scale=["#0f0f18", "#ff5a32"])
            else:
                fig = px.pie(grouped, names=cat, values=num, title=f"{agg} of {num} by {cat}",
                             color_discrete_sequence=COLORS)
                fig.update_traces(textfont=dict(family="DM Mono", size=10))
            st.plotly_chart(style_fig(fig), use_container_width=True)

    # ── CORRELATION ──
    elif analysis_type == "Correlation Analysis":
        if len(numeric_cols) < 2:
            st.warning("Need at least two numeric columns.")
        else:
            method = st.selectbox("Method", ["pearson", "spearman", "kendall"], key="corr_method")
            corr = filtered_df[numeric_cols].corr(method=method)

            fig = px.imshow(corr, text_auto=".2f", title=f"Correlation Matrix ({method.title()})",
                            color_continuous_scale=[[0, "#50b4ff"], [0.5, "#0f0f18"], [1, "#ff5a32"]],
                            zmin=-1, zmax=1)
            fig.update_traces(textfont=dict(family="DM Mono", size=10, color="#f0ece4"))
            st.plotly_chart(style_fig(fig), use_container_width=True)

            st.markdown('<div class="section-label">Top Correlated Pairs</div>', unsafe_allow_html=True)
            corr_pairs = corr.abs().unstack().sort_values(ascending=False)
            corr_pairs = corr_pairs[corr_pairs < 1].drop_duplicates().head(8)
            for (c1n, c2n), val in corr_pairs.items():
                direction = "↑" if corr.loc[c1n, c2n] > 0 else "↓"
                color = "#a8e063" if corr.loc[c1n, c2n] > 0 else "#ff5a32"
                st.markdown(f"""<div style="border-bottom:1px solid rgba(255,255,255,0.05);padding:8px 0;font-family:DM Mono,monospace;font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
                    <span><span style="color:#f0ece4">{c1n}</span>
                    <span style="color:rgba(232,228,220,0.3)"> × </span>
                    <span style="color:#f0ece4">{c2n}</span></span>
                    <span style="color:{color}">{direction} {val:.3f}</span>
                </div>""", unsafe_allow_html=True)

    # ── TREND OVER TIME ──
    elif analysis_type == "Trend Over Time":
        date_col = st.selectbox("Time Column", list(filtered_df.columns), key="trend_date")
        num_col = st.selectbox("Value Column", numeric_cols, key="trend_val")
        smooth = st.selectbox("Smoothing", ["None", "7-period MA", "30-period MA"], key="trend_smooth")

        plot_df = filtered_df[[date_col, num_col]].dropna().sort_values(date_col)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df[num_col], mode="lines",
                                  name="Raw", line=dict(color="rgba(255,90,50,0.3)", width=1)))
        if smooth != "None":
            window = 7 if "7" in smooth else 30
            plot_df = plot_df.copy()
            plot_df["_ma"] = plot_df[num_col].rolling(window, min_periods=1).mean()
            fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df["_ma"], mode="lines",
                                      name=smooth, line=dict(color="#ff5a32", width=2.5)))
        fig.update_layout(title=f"{num_col} over Time")
        st.plotly_chart(style_fig(fig), use_container_width=True)

    # ── SCATTER EXPLORER ──
    elif analysis_type == "Scatter Explorer":
        if len(numeric_cols) < 2:
            st.warning("Need at least two numeric columns.")
        else:
            x_col = st.selectbox("X Axis", numeric_cols, key="sc_x")
            y_col = st.selectbox("Y Axis", numeric_cols, index=min(1, len(numeric_cols)-1), key="sc_y")
            color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols + numeric_cols, key="sc_col")
            size_col = st.selectbox("Size by (optional)", ["None"] + numeric_cols, key="sc_sz")

            color_arg = None if color_col == "None" else color_col
            size_arg = None if size_col == "None" else size_col
            fig = px.scatter(filtered_df, x=x_col, y=y_col, color=color_arg, size=size_arg,
                             title=f"{y_col} vs {x_col}", opacity=0.75,
                             trendline="ols" if color_arg is None else None,
                             color_discrete_sequence=COLORS,
                             color_continuous_scale=[[0, "#0f0f18"], [1, "#ff5a32"]])
            if color_arg is None and size_arg is None:
                fig.update_traces(marker=dict(color="#ff5a32", size=6, line=dict(color="rgba(0,0,0,0.3)", width=1)))
            st.plotly_chart(style_fig(fig), use_container_width=True)

# ════════════════════════════════
#  TAB 2 — STATISTICS
# ════════════════════════════════
with tab_stats:
    if len(numeric_cols) > 0:
        st.markdown('<div class="section-label">Numeric Summary</div>', unsafe_allow_html=True)
        stats = filtered_df[numeric_cols].describe().T
        stats["median"] = filtered_df[numeric_cols].median()
        stats["skew"] = filtered_df[numeric_cols].skew().round(3)
        stats["nulls"] = filtered_df[numeric_cols].isnull().sum()
        display_cols = ["count", "mean", "median", "std", "min", "25%", "75%", "max", "skew", "nulls"]
        stats = stats[[c for c in display_cols if c in stats.columns]].round(3)

        rows_html = ""
        for col_name, row in stats.iterrows():
            cells = "".join(
                f"<td>{v:,.3f}</td>" if isinstance(v, float) else f"<td>{int(v)}</td>"
                for v in row.values
            )
            rows_html += f"<tr><td class='col-name'>{col_name}</td>{cells}</tr>"

        headers = "".join(f"<th>{c}</th>" for c in ["Column"] + list(stats.columns))
        st.markdown(f"""
        <div class="table-wrap">
        <table class="stats-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button("↓ Export Statistics CSV",
                           data=stats.to_csv().encode("utf-8"),
                           file_name="datalens_stats.csv", mime="text/csv")

    if len(cat_cols) > 0:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Categorical Summary</div>', unsafe_allow_html=True)
        cat_sel = st.selectbox("Select column", cat_cols, key="stats_cat")
        vc = filtered_df[cat_sel].value_counts().reset_index()
        vc.columns = [cat_sel, "count"]
        vc["percent"] = (vc["count"] / vc["count"].sum() * 100).round(1)
        st.dataframe(vc.head(15), use_container_width=True, hide_index=True)
        fig = px.bar(vc.head(15), x="count", y=cat_sel, orientation="h",
                     title=f"Value Counts · {cat_sel}")
        fig.update_traces(marker_color="#ff5a32", marker_line_width=0)
        st.plotly_chart(style_fig(fig), use_container_width=True)

# ════════════════════════════════
#  TAB 3 — AI INSIGHTS
# ════════════════════════════════
with tab_ai:
    st.markdown('<div class="section-label">AI-Powered Analysis</div>', unsafe_allow_html=True)
    st.markdown("""<div style="font-family:DM Sans,sans-serif;font-size:14px;color:rgba(232,228,220,0.45);margin-bottom:1.25rem;line-height:1.7;">
    Ask anything about your data — or get an automatic analysis below.
    </div>""", unsafe_allow_html=True)

    question = st.text_input("Ask a question",
                             placeholder="e.g. What are the main trends? Any outliers?",
                             key="ai_q")
    run_ai = st.button("◈ Analyse", use_container_width=True)

    if run_ai or question:
        with st.spinner("Thinking..."):
            result = get_ai_insights(filtered_df, question)
        st.markdown(f"""<div class="ai-card">
            <div class="ai-card-label">◈ AI Analysis · Claude Sonnet</div>
            <div class="ai-card-text">{result}</div>
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Generating auto insights..."):
            auto_result = get_ai_insights(filtered_df)
        st.markdown(f"""<div class="ai-card">
            <div class="ai-card-label">◈ Auto Insights · Claude Sonnet</div>
            <div class="ai-card-text">{auto_result}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Quick Insights</div>', unsafe_allow_html=True)

    numeric_df = filtered_df.select_dtypes(include="number")
    if len(numeric_df.columns) > 0:
        highest_mean_col = numeric_df.mean().idxmax()
        highest_var_col = numeric_df.var().idxmax()

        st.markdown(f"""<div class="insight-card">
            <div class="insight-icon">◈ Highest Average</div>
            <strong>{highest_mean_col}</strong> has the highest mean —
            averaging <strong>{numeric_df[highest_mean_col].mean():,.2f}</strong>.
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="insight-card">
            <div class="insight-icon">◈ Most Variable</div>
            <strong>{highest_var_col}</strong> has the greatest spread —
            variance of <strong>{numeric_df[highest_var_col].var():,.2f}</strong>.
            Could indicate outliers or distinct groups.
        </div>""", unsafe_allow_html=True)

        if len(numeric_df.columns) > 1:
            corr = numeric_df.corr().abs()
            corr_u = corr.unstack()
            corr_u = corr_u[corr_u < 1].drop_duplicates()
            if not corr_u.empty:
                strongest = corr_u.idxmax()
                raw_corr = numeric_df.corr().loc[strongest[0], strongest[1]]
                direction = "positively" if raw_corr > 0 else "negatively"
                st.markdown(f"""<div class="insight-card">
                    <div class="insight-icon">◈ Strongest Correlation</div>
                    <strong>{strongest[0]}</strong> and <strong>{strongest[1]}</strong>
                    are {direction} correlated (r = <strong>{corr_u.max():.3f}</strong>).
                    {"Strong — worth investigating." if corr_u.max() > 0.7 else "Moderate relationship."}
                </div>""", unsafe_allow_html=True)

        skews = numeric_df.skew().abs().sort_values(ascending=False)
        if len(skews) > 0 and skews.iloc[0] > 1:
            st.markdown(f"""<div class="insight-card">
                <div class="insight-icon">◈ Skewed Distribution</div>
                <strong>{skews.index[0]}</strong> is heavily skewed
                (skewness = <strong>{skews.iloc[0]:.2f}</strong>).
                Consider log-transforming before modelling.
            </div>""", unsafe_allow_html=True)

    if missing_count > 0:
        pct = round(missing_count / max(filtered_df.size, 1) * 100, 1)
        st.markdown(f"""<div class="insight-card">
            <div class="insight-icon">◈ Data Quality</div>
            <strong>{missing_count}</strong> missing values ({pct}% of cells).
            {"Significant — consider more imputation." if pct > 5 else "Manageable — auto-clean handled most of it."}
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "↓ Export Filtered Data",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="datalens_export.csv",
        mime="text/csv"
    )
