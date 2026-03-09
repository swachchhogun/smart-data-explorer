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
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important; color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,90,50,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(80,180,255,0.05) 0%, transparent 60%),
        #0a0a0f !important;
}
[data-testid="stSidebar"] { background: #0d0d16 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
[data-testid="stSidebar"] * { color: #e8e4dc !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 1.5rem 1.25rem 4rem !important; max-width: 1400px !important; }
@media (min-width: 768px) { .block-container { padding: 2rem 2.5rem 4rem !important; } }

.hero { padding: 2rem 0 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 2rem; }
.hero-eyebrow { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 4px; text-transform: uppercase; color: #ff5a32; margin-bottom: 0.6rem; }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(38px, 10vw, 80px); font-weight: 800; line-height: 0.92; letter-spacing: -2px; color: #f0ece4; margin: 0 0 0.75rem; }
.hero-title span { color: #ff5a32; }
.hero-sub { font-family: 'DM Sans', sans-serif; font-size: 14px; color: rgba(232,228,220,0.4); font-weight: 300; max-width: 480px; line-height: 1.7; }

.upload-zone { border: 1px dashed rgba(255,255,255,0.12); background: #0f0f18; padding: 3rem 1.5rem; text-align: center; margin: 1.5rem 0; border-radius: 2px; }
.upload-title { font-family: 'Syne', sans-serif; font-size: clamp(20px, 5vw, 28px); font-weight: 700; color: #f0ece4; margin-bottom: 0.5rem; letter-spacing: -0.5px; }
.upload-sub { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 2px; color: rgba(232,228,220,0.25); text-transform: uppercase; }

.metrics-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.06); margin-bottom: 2rem; overflow: hidden; }
@media (min-width: 600px) { .metrics-row { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 900px) { .metrics-row { grid-template-columns: repeat(5, 1fr); } }
.metric-card { background: #0f0f18; padding: 1.2rem 1.25rem; position: relative; overflow: hidden; }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #ff5a32, transparent); opacity: 0; transition: opacity 0.3s; }
.metric-card:hover::before { opacity: 1; }
.metric-label { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: rgba(232,228,220,0.3); margin-bottom: 0.4rem; }
.metric-value { font-family: 'Syne', sans-serif; font-size: clamp(24px, 5vw, 34px); font-weight: 800; color: #f0ece4; line-height: 1; letter-spacing: -1px; }
.metric-value span { font-size: 10px; font-weight: 400; color: rgba(232,228,220,0.3); font-family: 'DM Mono', monospace; margin-left: 2px; }
.metric-sub { font-family: 'DM Mono', monospace; font-size: 9px; color: #ff5a32; margin-top: 3px; }

.section-label { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 4px; text-transform: uppercase; color: #ff5a32; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px; }
.section-label::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.07); }

.stSelectbox > div > div, .stMultiSelect > div > div { background: #0f0f18 !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #e8e4dc !important; }
.stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within { border-color: #ff5a32 !important; box-shadow: 0 0 0 1px #ff5a32 !important; }
.stSelectbox label, .stMultiSelect label, .stTextInput label { font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: rgba(232,228,220,0.4) !important; }
.stTextInput input { background: #0f0f18 !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #e8e4dc !important; font-size: 15px !important; }
.stTextInput input:focus { border-color: #ff5a32 !important; box-shadow: 0 0 0 1px #ff5a32 !important; }

.stButton > button { background: transparent !important; border: 1px solid rgba(255,255,255,0.15) !important; color: #e8e4dc !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; padding: 0.7rem 1.4rem !important; transition: all 0.2s !important; width: 100% !important; }
.stButton > button:hover { background: #ff5a32 !important; border-color: #ff5a32 !important; color: white !important; }
.stDownloadButton > button { background: rgba(255,90,50,0.1) !important; border: 1px solid rgba(255,90,50,0.3) !important; color: #ff5a32 !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; padding: 0.7rem 1.4rem !important; width: 100% !important; }
.stDownloadButton > button:hover { background: #ff5a32 !important; color: white !important; }

[data-testid="stFileUploader"] { background: #0f0f18 !important; border: 1px dashed rgba(255,90,50,0.3) !important; padding: 1rem !important; }
[data-testid="stFileUploader"] * { color: #e8e4dc !important; }
[data-testid="stFileUploaderDropzone"] { background: transparent !important; padding: 1.5rem !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.07) !important; gap: 0 !important; overflow-x: auto !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: rgba(232,228,220,0.35) !important; font-family: 'DM Mono', monospace !important; font-size: 10px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; border: none !important; padding: 0.75rem 1rem !important; white-space: nowrap !important; }
.stTabs [aria-selected="true"] { color: #ff5a32 !important; border-bottom: 2px solid #ff5a32 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.25rem !important; }

.insight-card { background: #0f0f18; border: 1px solid rgba(255,255,255,0.06); border-left: 2px solid #ff5a32; padding: 1.1rem 1.25rem; margin-bottom: 0.75rem; font-family: 'DM Sans', sans-serif; font-size: 14px; color: rgba(232,228,220,0.7); line-height: 1.7; }
.insight-card strong { color: #f0ece4; font-weight: 500; }
.insight-icon { font-family: 'DM Mono', monospace; font-size: 9px; color: #ff5a32; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 0.4rem; }

.ai-card { background: linear-gradient(135deg, #0f0f18 0%, #12101f 100%); border: 1px solid rgba(255,90,50,0.2); padding: 1.5rem; margin-top: 1rem; position: relative; }
.ai-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, #ff5a32, transparent 60%); }
.ai-card-label { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 3px; text-transform: uppercase; color: #ff5a32; margin-bottom: 1rem; }
.ai-card-text { font-family: 'DM Sans', sans-serif; font-size: 14px; color: rgba(232,228,220,0.8); line-height: 1.8; white-space: pre-wrap; }

.quality-bar-wrap { background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px; margin-top: 4px; overflow: hidden; }
.quality-bar { height: 100%; border-radius: 3px; }
.quality-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.04); gap: 8px; }
.quality-col-name { font-family: 'DM Sans', sans-serif; font-size: 13px; color: #f0ece4; }
.quality-col-type { font-family: 'DM Mono', monospace; font-size: 9px; color: rgba(255,90,50,0.7); background: rgba(255,90,50,0.08); padding: 2px 7px; border-radius: 2px; white-space: nowrap; flex-shrink: 0; }
.quality-col-stats { font-family: 'DM Mono', monospace; font-size: 10px; color: rgba(232,228,220,0.35); text-align: right; min-width: 80px; flex-shrink: 0; }

.clean-badge { display: inline-block; background: rgba(168,224,99,0.1); border: 1px solid rgba(168,224,99,0.25); color: #a8e063; font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 1px; text-transform: uppercase; padding: 3px 8px; margin: 3px; }
.error-box { background: rgba(255,90,50,0.07); border: 1px solid rgba(255,90,50,0.25); padding: 1.2rem 1.5rem; font-family: 'DM Sans', sans-serif; font-size: 14px; color: rgba(232,228,220,0.75); line-height: 1.7; margin: 1rem 0; }
.error-box strong { color: #ff5a32; }

.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.stats-table { width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace; font-size: 11px; min-width: 600px; }
.stats-table th { background: rgba(255,90,50,0.08); color: #ff5a32; letter-spacing: 2px; text-transform: uppercase; padding: 10px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 9px; white-space: nowrap; }
.stats-table td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); color: rgba(232,228,220,0.7); white-space: nowrap; }
.stats-table tr:hover td { background: rgba(255,255,255,0.02); color: #e8e4dc; }
.stats-table .col-name { color: #f0ece4; font-weight: 500; }

hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }
.stAlert { background: rgba(255,90,50,0.07) !important; border: 1px solid rgba(255,90,50,0.18) !important; color: #e8e4dc !important; }
.stToggle label { font-family: 'DM Mono', monospace !important; font-size: 10px !important; text-transform: uppercase !important; color: rgba(232,228,220,0.5) !important; }
.sidebar-brand { font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; color: #f0ece4; letter-spacing: -0.5px; padding: 1.5rem 0 0.2rem; }
.sidebar-brand span { color: #ff5a32; }
.sidebar-tagline { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 3px; color: rgba(232,228,220,0.2); text-transform: uppercase; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
COLORS = ["#ff5a32", "#50b4ff", "#a8e063", "#f7c948", "#c678dd", "#56b6c2", "#e06c75", "#d19a66"]

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0d0d16",
        font=dict(family="DM Sans", color="#e8e4dc", size=11),
        title_font=dict(family="Syne", size=15, color="#f0ece4"),
        colorway=COLORS,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.07)",
                   tickfont=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)"),
                   title_font=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)")),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.07)",
                   tickfont=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)"),
                   title_font=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.35)")),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(family="DM Mono", size=9, color="rgba(232,228,220,0.45)"),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=8, r=8, t=44, b=8),
        hoverlabel=dict(bgcolor="#0f0f18", font_family="DM Mono", font_size=11, bordercolor="rgba(255,90,50,0.3)"),
    )
    return fig

# ─────────────────────────────────────────────
#  SAFE CSV LOADER
# ─────────────────────────────────────────────
def safe_read_csv(file):
    for enc in ["utf-8", "latin-1", "utf-16", "cp1252"]:
        for sep in [",", ";", "\t"]:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=enc, sep=sep)
                if df.shape[1] > 1 or sep == ",":
                    return df, None
            except Exception:
                continue
    return None, "Could not read this file. Make sure it's a valid CSV."

# ─────────────────────────────────────────────
#  SMART CLEAN
# ─────────────────────────────────────────────
def smart_clean(df: pd.DataFrame):
    report = []
    cleaned = df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]
    if cleaned.empty:
        return cleaned, ["File appears to be empty."]

    for col in cleaned.select_dtypes(include="object").columns:
        try:
            parsed = pd.to_datetime(cleaned[col], infer_datetime_format=True, errors="coerce")
            if parsed.notna().mean() > 0.7:
                cleaned[col] = parsed
                report.append(f"Parsed '{col}' as datetime")
        except Exception:
            pass

    for col in cleaned.select_dtypes(include="object").columns:
        try:
            cleaned[col] = cleaned[col].str.strip()
        except Exception:
            pass

    for col in cleaned.select_dtypes(include="number").columns:
        n = int(cleaned[col].isnull().sum())
        if n > 0:
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
            report.append(f"Filled {n} nulls in '{col}' with median")

    for col in cleaned.select_dtypes(include="object").columns:
        n = int(cleaned[col].isnull().sum())
        if n > 0 and not cleaned[col].mode().empty:
            cleaned[col] = cleaned[col].fillna(cleaned[col].mode()[0])
            report.append(f"Filled {n} nulls in '{col}' with mode")

    before = len(cleaned)
    cleaned = cleaned.dropna(how="all").dropna(axis=1, how="all")
    if before - len(cleaned) > 0:
        report.append(f"Removed {before - len(cleaned)} fully empty rows")

    n_dupes = int(cleaned.duplicated().sum())
    if n_dupes > 0:
        cleaned = cleaned.drop_duplicates()
        report.append(f"Removed {n_dupes} duplicate rows")

    return cleaned, report

# ─────────────────────────────────────────────
#  FREE AI — Groq (Llama 3, no cost)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=300)
def get_ai_insights(data_json: str, question: str = "") -> str:
    prompt = f"""You are a data analyst. Analyze this dataset and provide clear insights.

Dataset:
{data_json}

{"Question: " + question if question else "Give 4-5 key insights: patterns, outliers, distributions, interesting findings. Be specific with numbers."}

Plain language, numbered points, brief."""

    groq_key = st.secrets.get("GROQ_API_KEY", "")
    if not groq_key:
        return ("⚠️ No Groq API key found.\n\n"
                "Setup (free, 2 mins, no card):\n"
                "1. Sign up at console.groq.com\n"
                "2. Create an API key\n"
                "3. Streamlit Cloud → your app → Settings → Secrets:\n\n"
                "   GROQ_API_KEY = \"your-key-here\"")
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            json={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 800, "temperature": 0.4},
            timeout=20
        )
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Groq error: {data.get('error', {}).get('message', str(data))}"
    except requests.exceptions.Timeout:
        return "Request timed out — Groq may be busy. Try again."
    except Exception as e:
        return f"Could not reach Groq: {str(e)}"

def build_summary(df: pd.DataFrame) -> str:
    nd = df.select_dtypes(include="number")
    cd = df.select_dtypes(include="object")
    return json.dumps({
        "shape": list(df.shape),
        "columns": list(df.columns),
        "numeric_stats": nd.describe().round(2).to_dict() if len(nd.columns) > 0 else {},
        "categorical_top": {c: df[c].value_counts().head(3).to_dict() for c in cd.columns[:4]},
        "missing": df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
    }, default=str)

# ─────────────────────────────────────────────
#  QUALITY HELPERS
# ─────────────────────────────────────────────
def col_health(s):
    null_pct = s.isnull().mean() * 100
    unique_pct = s.nunique() / max(len(s), 1) * 100
    score = max(0, 100 - null_pct - (20 if unique_pct > 95 and pd.api.types.is_object_dtype(s) else 0))
    return {"null_pct": round(null_pct, 1), "unique": s.nunique(), "score": round(score)}

def hcolor(score):
    if score >= 80: return "#a8e063"
    if score >= 50: return "#f7c948"
    return "#ff5a32"

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Data<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">◈ Smart Explorer</div>', unsafe_allow_html=True)

    if st.session_state.get("working_df") is not None:
        wdf = st.session_state.working_df
        num_sb = wdf.select_dtypes(include="number").columns.tolist()
        cat_sb = wdf.select_dtypes(include="object").columns.tolist()
        st.markdown("---")
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:rgba(232,228,220,0.3);margin-bottom:0.75rem;">Filters</div>', unsafe_allow_html=True)
        fdf = wdf.copy()
        for col in cat_sb[:3]:
            opts = st.multiselect(col, sorted(wdf[col].dropna().unique().tolist()), key=f"sb_f_{col}")
            if opts:
                fdf = fdf[fdf[col].isin(opts)]
        for col in num_sb[:2]:
            cmin, cmax = float(wdf[col].min()), float(wdf[col].max())
            if cmin < cmax:
                rng = st.slider(col, cmin, cmax, (cmin, cmax), key=f"sb_r_{col}")
                fdf = fdf[fdf[col].between(*rng)]
        st.session_state.filtered_df = fdf
        st.markdown("---")
        st.download_button("↓ Export filtered CSV",
                           data=fdf.to_csv(index=False).encode("utf-8"),
                           file_name="datalens_export.csv", mime="text/csv",
                           use_container_width=True)
    else:
        st.caption("Upload a CSV on the main page to start filtering.")

# ─────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">◈ Smart Data Explorer</div>
    <div class="hero-title">Data<span>Lens</span></div>
    <div class="hero-sub">Upload any CSV — auto-clean, explore, visualise, and get free AI-powered insights.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FILE UPLOAD
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Your Data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-title">Tap above to upload a CSV</div>
        <div class="upload-sub">Any CSV · Auto-cleaned · Free AI · Mobile friendly</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.working_df = None
    st.session_state.filtered_df = None
    st.stop()

# ─────────────────────────────────────────────
#  LOAD
# ─────────────────────────────────────────────
with st.spinner("Reading file..."):
    raw_df, load_err = safe_read_csv(uploaded_file)

if load_err or raw_df is None:
    st.markdown(f'<div class="error-box"><strong>Could not load file</strong><br>{load_err}</div>',
                unsafe_allow_html=True)
    st.stop()

if raw_df.empty:
    st.markdown('<div class="error-box"><strong>Empty file</strong><br>The CSV has no data.</div>',
                unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
#  CLEAN
# ─────────────────────────────────────────────
try:
    cleaned_df, clean_report = smart_clean(raw_df)
except Exception as e:
    cleaned_df, clean_report = raw_df.copy(), [f"Cleaning failed: {e}"]

use_cleaned = st.toggle("Auto-clean data", value=True, help="Fills nulls, fixes types, removes duplicates")
working_df = cleaned_df if use_cleaned else raw_df
st.session_state.working_df = working_df

# Sync filter
if (st.session_state.get("filtered_df") is not None
        and list(st.session_state.filtered_df.columns) == list(working_df.columns)):
    filtered_df = st.session_state.filtered_df
else:
    filtered_df = working_df.copy()
    st.session_state.filtered_df = filtered_df

numeric_cols = working_df.select_dtypes(include="number").columns.tolist()
cat_cols = working_df.select_dtypes(include="object").columns.tolist()

if clean_report and use_cleaned:
    with st.expander("✦ Cleaning applied"):
        for n in clean_report:
            st.markdown(f'<span class="clean-badge">✓ {n}</span>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  METRICS
# ─────────────────────────────────────────────
missing_count = int(filtered_df.isnull().sum().sum())
dupe_count = int(filtered_df.duplicated().sum())
completeness = round((1 - missing_count / max(filtered_df.size, 1)) * 100, 1)

st.markdown(f"""
<div class="metrics-row">
  <div class="metric-card"><div class="metric-label">Rows</div>
    <div class="metric-value">{filtered_df.shape[0]:,}<span>r</span></div>
    <div class="metric-sub">of {working_df.shape[0]:,}</div></div>
  <div class="metric-card"><div class="metric-label">Columns</div>
    <div class="metric-value">{filtered_df.shape[1]}<span>c</span></div>
    <div class="metric-sub">{len(numeric_cols)} num · {len(cat_cols)} cat</div></div>
  <div class="metric-card"><div class="metric-label">Complete</div>
    <div class="metric-value">{completeness}<span>%</span></div>
    <div class="metric-sub">{missing_count} nulls</div></div>
  <div class="metric-card"><div class="metric-label">Dupes</div>
    <div class="metric-value">{dupe_count}<span>r</span></div>
    <div class="metric-sub">{"none" if dupe_count == 0 else "detected"}</div></div>
  <div class="metric-card"><div class="metric-label">Memory</div>
    <div class="metric-value">{filtered_df.memory_usage(deep=True).sum() / 1024:.0f}<span>kb</span></div>
    <div class="metric-sub">in memory</div></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ANALYSIS MODE
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Analysis Mode</div>', unsafe_allow_html=True)
analysis_type = st.selectbox(
    "Mode", ["Dashboard Overview", "Distribution Analysis", "Category Comparison",
             "Correlation Analysis", "Trend Over Time", "Scatter Explorer"],
    label_visibility="collapsed"
)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_explore, tab_quality, tab_stats, tab_ai = st.tabs([
    "◈  Explore", "◈  Data Quality", "◈  Statistics", "◈  AI Insights"
])

# ═══════════════
#  EXPLORE
# ═══════════════
with tab_explore:
    st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df.head(8), use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{analysis_type}</div>', unsafe_allow_html=True)

    try:
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

        elif analysis_type == "Distribution Analysis":
            if not numeric_cols:
                st.warning("No numeric columns found.")
            else:
                column = st.selectbox("Numeric Column", numeric_cols, key="dist_col")
                color_by = st.selectbox("Color by (optional)", ["None"] + cat_cols, key="dist_color")
                color_arg = None if color_by == "None" else color_by
                fig = px.histogram(filtered_df, x=column, color=color_arg, nbins=30,
                                   title=f"Histogram · {column}", barmode="overlay", opacity=0.8)
                if not color_arg:
                    fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.3)", marker_line_width=1)
                st.plotly_chart(style_fig(fig), use_container_width=True)
                fig2 = px.violin(filtered_df, y=column, color=color_arg, title=f"Violin · {column}", box=True)
                if not color_arg:
                    fig2.update_traces(fillcolor="rgba(255,90,50,0.15)", line_color="#ff5a32")
                st.plotly_chart(style_fig(fig2), use_container_width=True)

        elif analysis_type == "Category Comparison":
            if not cat_cols or not numeric_cols:
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
                cp = corr.abs().unstack().sort_values(ascending=False)
                cp = cp[cp < 1].drop_duplicates().head(8)
                for (c1n, c2n), val in cp.items():
                    d = "↑" if corr.loc[c1n, c2n] > 0 else "↓"
                    col = "#a8e063" if corr.loc[c1n, c2n] > 0 else "#ff5a32"
                    st.markdown(f"""<div style="border-bottom:1px solid rgba(255,255,255,0.05);padding:8px 0;font-family:DM Mono,monospace;font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
                        <span><span style="color:#f0ece4">{c1n}</span> <span style="color:rgba(232,228,220,0.3)">×</span> <span style="color:#f0ece4">{c2n}</span></span>
                        <span style="color:{col}">{d} {val:.3f}</span>
                    </div>""", unsafe_allow_html=True)

        elif analysis_type == "Trend Over Time":
            date_col = st.selectbox("Time Column", list(filtered_df.columns), key="trend_date")
            if not numeric_cols:
                st.warning("No numeric columns.")
            else:
                num_col = st.selectbox("Value Column", numeric_cols, key="trend_val")
                smooth = st.selectbox("Smoothing", ["None", "7-period MA", "30-period MA"], key="trend_smooth")
                plot_df = filtered_df[[date_col, num_col]].dropna().sort_values(date_col)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df[num_col], mode="lines",
                                          name="Raw", line=dict(color="rgba(255,90,50,0.3)", width=1)))
                if smooth != "None":
                    w = 7 if "7" in smooth else 30
                    plot_df = plot_df.copy()
                    plot_df["_ma"] = plot_df[num_col].rolling(w, min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df["_ma"], mode="lines",
                                              name=smooth, line=dict(color="#ff5a32", width=2.5)))
                fig.update_layout(title=f"{num_col} over Time")
                st.plotly_chart(style_fig(fig), use_container_width=True)

        elif analysis_type == "Scatter Explorer":
            if len(numeric_cols) < 2:
                st.warning("Need at least two numeric columns.")
            else:
                x_col = st.selectbox("X Axis", numeric_cols, key="sc_x")
                y_col = st.selectbox("Y Axis", numeric_cols, index=min(1, len(numeric_cols)-1), key="sc_y")
                color_col = st.selectbox("Color by (optional)", ["None"] + cat_cols + numeric_cols, key="sc_col")
                size_col = st.selectbox("Size by (optional)", ["None"] + numeric_cols, key="sc_sz")
                ca = None if color_col == "None" else color_col
                sa = None if size_col == "None" else size_col
                fig = px.scatter(filtered_df, x=x_col, y=y_col, color=ca, size=sa,
                                 title=f"{y_col} vs {x_col}", opacity=0.75,
                                 trendline="ols" if ca is None else None,
                                 color_discrete_sequence=COLORS,
                                 color_continuous_scale=[[0, "#0f0f18"], [1, "#ff5a32"]])
                if ca is None and sa is None:
                    fig.update_traces(marker=dict(color="#ff5a32", size=6, line=dict(color="rgba(0,0,0,0.3)", width=1)))
                st.plotly_chart(style_fig(fig), use_container_width=True)

    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Chart error</strong><br>Try a different column or mode.<br><small style="opacity:0.5">{e}</small></div>',
                    unsafe_allow_html=True)

# ═══════════════
#  DATA QUALITY
# ═══════════════
with tab_quality:
    st.markdown('<div class="section-label">Before vs After Cleaning</div>', unsafe_allow_html=True)
    raw_nulls = int(raw_df.isnull().sum().sum())
    raw_dupes = int(raw_df.duplicated().sum())
    cn = int(cleaned_df.isnull().sum().sum())
    cd_d = int(cleaned_df.duplicated().sum())

    st.markdown(f"""
    <div class="metrics-row" style="grid-template-columns:repeat(2,1fr);margin-bottom:1.5rem;">
        <div class="metric-card"><div class="metric-label">Nulls — raw</div>
            <div class="metric-value" style="color:#ff5a32">{raw_nulls:,}</div></div>
        <div class="metric-card"><div class="metric-label">Nulls — cleaned</div>
            <div class="metric-value" style="color:#a8e063">{cn:,}</div></div>
        <div class="metric-card"><div class="metric-label">Dupes — raw</div>
            <div class="metric-value" style="color:#ff5a32">{raw_dupes:,}</div></div>
        <div class="metric-card"><div class="metric-label">Dupes — cleaned</div>
            <div class="metric-value" style="color:#a8e063">{cd_d:,}</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Column Health</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;color:rgba(232,228,220,0.2);margin-bottom:1rem;text-transform:uppercase;">Bar = completeness. Green = healthy, red = issues.</div>', unsafe_allow_html=True)

    for col in working_df.columns:
        h = col_health(working_df[col])
        dtype_str = str(working_df[col].dtype)
        bc = hcolor(h["score"])
        st.markdown(f"""
        <div class="quality-row">
            <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                    <span class="quality-col-name">{col}</span>
                    <span class="quality-col-type">{dtype_str}</span>
                </div>
                <div class="quality-bar-wrap">
                    <div class="quality-bar" style="width:{h['score']}%;background:{bc};"></div>
                </div>
            </div>
            <div class="quality-col-stats">{h['null_pct']}% null<br>{h['unique']:,} unique</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Outlier Detection</div>', unsafe_allow_html=True)

    if not numeric_cols:
        st.info("No numeric columns to check.")
    else:
        try:
            oc = st.selectbox("Column to check", numeric_cols, key="out_col")
            s = filtered_df[oc].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outliers = filtered_df[(filtered_df[oc] < lo) | (filtered_df[oc] > hi)]
            pct = round(len(outliers) / max(len(filtered_df), 1) * 100, 1)
            st.markdown(f"""<div class="insight-card">
                <div class="insight-icon">◈ IQR Method · {oc}</div>
                Normal range: <strong>{lo:,.2f}</strong> to <strong>{hi:,.2f}</strong><br>
                <strong>{len(outliers):,} rows ({pct}%)</strong> fall outside this range.
                {"Significant — worth investigating." if pct > 5 else "Small proportion — likely fine."}
            </div>""", unsafe_allow_html=True)
            fig = px.box(filtered_df, y=oc, title=f"Outliers · {oc}", points="outliers")
            fig.update_traces(marker_color="#ff5a32", line_color="#50b4ff",
                              marker=dict(color="#ff5a32", size=5, opacity=0.7))
            st.plotly_chart(style_fig(fig), use_container_width=True)
            if len(outliers) > 0:
                with st.expander(f"View outlier rows ({min(len(outliers), 50)} shown)"):
                    st.dataframe(outliers.head(50), use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Outlier detection error: {e}")

# ═══════════════
#  STATISTICS
# ═══════════════
with tab_stats:
    if numeric_cols:
        st.markdown('<div class="section-label">Numeric Summary</div>', unsafe_allow_html=True)
        try:
            stats = filtered_df[numeric_cols].describe().T
            stats["median"] = filtered_df[numeric_cols].median()
            stats["skew"] = filtered_df[numeric_cols].skew().round(3)
            stats["nulls"] = filtered_df[numeric_cols].isnull().sum()
            dc = ["count", "mean", "median", "std", "min", "25%", "75%", "max", "skew", "nulls"]
            stats = stats[[c for c in dc if c in stats.columns]].round(3)
            rows_html = ""
            for cn2, row in stats.iterrows():
                cells = "".join(f"<td>{v:,.3f}</td>" if isinstance(v, float) else f"<td>{int(v)}</td>" for v in row.values)
                rows_html += f"<tr><td class='col-name'>{cn2}</td>{cells}</tr>"
            headers = "".join(f"<th>{c}</th>" for c in ["Column"] + list(stats.columns))
            st.markdown(f"""<div class="table-wrap"><table class="stats-table">
                <thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody>
            </table></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("↓ Export statistics CSV",
                               data=stats.to_csv().encode("utf-8"),
                               file_name="datalens_stats.csv", mime="text/csv")
        except Exception as e:
            st.warning(f"Stats error: {e}")

    if cat_cols:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Categorical Summary</div>', unsafe_allow_html=True)
        try:
            cat_sel = st.selectbox("Column", cat_cols, key="stats_cat")
            vc = filtered_df[cat_sel].value_counts().reset_index()
            vc.columns = [cat_sel, "count"]
            vc["percent"] = (vc["count"] / vc["count"].sum() * 100).round(1)
            st.dataframe(vc.head(15), use_container_width=True, hide_index=True)
            fig = px.bar(vc.head(15), x="count", y=cat_sel, orientation="h", title=f"Value Counts · {cat_sel}")
            fig.update_traces(marker_color="#ff5a32", marker_line_width=0)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        except Exception as e:
            st.warning(f"Categorical summary error: {e}")

# ═══════════════
#  AI INSIGHTS
# ═══════════════
with tab_ai:
    st.markdown('<div class="section-label">AI-Powered Analysis</div>', unsafe_allow_html=True)

    has_key = bool(st.secrets.get("GROQ_API_KEY", ""))
    if not has_key:
        st.markdown("""<div class="error-box">
            <strong>Free AI setup — 2 mins, no card needed:</strong><br><br>
            1. Go to <strong>console.groq.com</strong> → sign up free<br>
            2. Click <strong>API Keys</strong> → Create API key<br>
            3. In Streamlit Cloud → your app → <strong>Settings → Secrets</strong>, add:<br><br>
            <code style="background:rgba(255,255,255,0.07);padding:4px 10px;font-family:DM Mono,monospace;font-size:12px;">GROQ_API_KEY = "gsk_xxxxxxxxxxxx"</code><br><br>
            Groq runs Llama 3 for free. No credit card, no usage limits for normal use.
        </div>""", unsafe_allow_html=True)

    st.markdown('<div style="font-family:DM Sans,sans-serif;font-size:14px;color:rgba(232,228,220,0.45);margin-bottom:1.25rem;line-height:1.7;">Ask anything about your data, or get an auto-analysis.</div>', unsafe_allow_html=True)

    question = st.text_input("Ask a question", placeholder="e.g. What are the main trends? Any outliers?", key="ai_q")
    run_ai = st.button("◈ Analyse with AI", use_container_width=True)
    data_json = build_summary(filtered_df)

    if run_ai or question:
        with st.spinner("Thinking..."):
            result = get_ai_insights(data_json, question)
        st.markdown(f"""<div class="ai-card">
            <div class="ai-card-label">◈ AI Answer · Llama 3 (free via Groq)</div>
            <div class="ai-card-text">{result}</div>
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Generating auto insights..."):
            auto_result = get_ai_insights(data_json)
        st.markdown(f"""<div class="ai-card">
            <div class="ai-card-label">◈ Auto Insights · Llama 3 (free via Groq)</div>
            <div class="ai-card-text">{auto_result}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Statistical Quick Insights</div>', unsafe_allow_html=True)

    try:
        ndf = filtered_df.select_dtypes(include="number")
        if len(ndf.columns) > 0:
            hmc = ndf.mean().idxmax()
            hvc = ndf.var().idxmax()
            st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Highest Average</div>
                <strong>{hmc}</strong> has the highest mean — <strong>{ndf[hmc].mean():,.2f}</strong>.
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Most Variable</div>
                <strong>{hvc}</strong> has the greatest spread — variance <strong>{ndf[hvc].var():,.2f}</strong>.
                Could indicate outliers or distinct groups.
            </div>""", unsafe_allow_html=True)
            if len(ndf.columns) > 1:
                corr = ndf.corr().abs()
                cu = corr.unstack()
                cu = cu[cu < 1].drop_duplicates()
                if not cu.empty:
                    strongest = cu.idxmax()
                    rc = ndf.corr().loc[strongest[0], strongest[1]]
                    d = "positively" if rc > 0 else "negatively"
                    st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Strongest Correlation</div>
                        <strong>{strongest[0]}</strong> and <strong>{strongest[1]}</strong> are {d} correlated
                        (r = <strong>{cu.max():.3f}</strong>).
                        {"Strong — worth investigating." if cu.max() > 0.7 else "Moderate relationship."}
                    </div>""", unsafe_allow_html=True)
            skews = ndf.skew().abs().sort_values(ascending=False)
            if len(skews) > 0 and skews.iloc[0] > 1:
                st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Skewed Distribution</div>
                    <strong>{skews.index[0]}</strong> is heavily skewed (skewness = <strong>{skews.iloc[0]:.2f}</strong>).
                    Consider log-transforming before modelling.
                </div>""", unsafe_allow_html=True)
        if missing_count > 0:
            pct = round(missing_count / max(filtered_df.size, 1) * 100, 1)
            st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Data Quality</div>
                <strong>{missing_count}</strong> missing values ({pct}% of cells).
                {"Significant — consider further imputation." if pct > 5 else "Manageable — auto-clean handled most of it."}
            </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not compute quick insights: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("↓ Export filtered data",
                       data=filtered_df.to_csv(index=False).encode("utf-8"),
                       file_name="datalens_export.csv", mime="text/csv")
