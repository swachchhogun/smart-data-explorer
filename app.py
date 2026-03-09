import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="DataLens",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
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

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #e8e4dc !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: #ff5a32 !important;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding: 2rem 2.5rem 4rem !important; max-width: 1400px !important; }

/* ── Hero Header ── */
.hero {
    padding: 3.5rem 0 2.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #ff5a32;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(48px, 7vw, 88px);
    font-weight: 800;
    line-height: 0.92;
    letter-spacing: -3px;
    color: #f0ece4;
    margin: 0 0 1rem;
}
.hero-title span { color: #ff5a32; }
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    color: rgba(232,228,220,0.45);
    font-weight: 300;
    max-width: 480px;
    line-height: 1.6;
}

/* ── Metric Cards ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2.5rem;
    border-radius: 2px;
    overflow: hidden;
}
.metric-card {
    background: #0f0f18;
    padding: 1.75rem 2rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #ff5a32, transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.metric-card:hover::before { opacity: 1; }
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(232,228,220,0.35);
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 42px;
    font-weight: 800;
    color: #f0ece4;
    line-height: 1;
    letter-spacing: -2px;
}
.metric-value span {
    font-size: 14px;
    font-weight: 400;
    letter-spacing: 0;
    color: rgba(232,228,220,0.35);
    font-family: 'DM Mono', monospace;
    margin-left: 4px;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #ff5a32;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.07);
}

/* ── Data Table ── */
.stDataFrame {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 2px !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    background: #0f0f18 !important;
}

/* ── Selectbox / Inputs ── */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #0f0f18 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 2px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within {
    border-color: #ff5a32 !important;
    box-shadow: 0 0 0 1px #ff5a32 !important;
}
.stSelectbox label, .stMultiSelect label {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: rgba(232,228,220,0.45) !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 2rem 0 !important; }

/* ── Insights ── */
.insight-card {
    background: #0f0f18;
    border: 1px solid rgba(255,255,255,0.06);
    border-left: 2px solid #ff5a32;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    color: rgba(232,228,220,0.75);
    line-height: 1.6;
}
.insight-card strong { color: #f0ece4; font-weight: 500; }
.insight-icon {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #ff5a32;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

/* ── Upload Zone ── */
.upload-zone {
    border: 1px dashed rgba(255,255,255,0.12);
    background: #0f0f18;
    padding: 4rem 2rem;
    text-align: center;
    margin: 3rem 0;
}
.upload-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: #f0ece4;
    margin-bottom: 0.5rem;
    letter-spacing: -1px;
}
.upload-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    color: rgba(232,228,220,0.3);
    text-transform: uppercase;
}

/* ── Warning / Info ── */
.stAlert {
    background: rgba(255, 90, 50, 0.08) !important;
    border: 1px solid rgba(255,90,50,0.2) !important;
    border-radius: 2px !important;
    color: #e8e4dc !important;
}

/* ── Plotly charts background ── */
.js-plotly-plot { border: 1px solid rgba(255,255,255,0.06); }

/* ── Sidebar header ── */
.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 800;
    color: #f0ece4;
    letter-spacing: -0.5px;
    padding: 1.5rem 0 0.25rem;
}
.sidebar-brand span { color: #ff5a32; }
.sidebar-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    color: rgba(232,228,220,0.25);
    text-transform: uppercase;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0f0f18",
    font=dict(family="DM Sans", color="#e8e4dc", size=12),
    title_font=dict(family="Syne", size=18, color="#f0ece4"),
    colorway=["#ff5a32", "#50b4ff", "#a8e063", "#f7c948", "#c678dd", "#56b6c2"],
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.08)",
        tickfont=dict(family="DM Mono", size=10, color="rgba(232,228,220,0.4)"),
        title_font=dict(family="DM Mono", size=10, color="rgba(232,228,220,0.4)"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        linecolor="rgba(255,255,255,0.08)",
        tickfont=dict(family="DM Mono", size=10, color="rgba(232,228,220,0.4)"),
        title_font=dict(family="DM Mono", size=10, color="rgba(232,228,220,0.4)"),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono", size=10, color="rgba(232,228,220,0.5)")
    ),
    margin=dict(l=20, r=20, t=50, b=20),
)

def style_fig(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Data<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">◈ Smart Explorer v1</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        numeric_cols = df_raw.select_dtypes(include="number").columns
        cat_cols = df_raw.select_dtypes(include="object").columns

        st.markdown("---")
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:rgba(232,228,220,0.35);margin-bottom:1rem;">Filters</div>', unsafe_allow_html=True)

        filtered_df = df_raw.copy()
        for col in cat_cols[:3]:
            options = st.multiselect(col, df_raw[col].dropna().unique(), key=f"filter_{col}")
            if options:
                filtered_df = filtered_df[filtered_df[col].isin(options)]

        st.markdown("---")
        st.markdown('<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:rgba(232,228,220,0.35);margin-bottom:1rem;">Analysis Mode</div>', unsafe_allow_html=True)

        analysis_type = st.selectbox(
            "Mode",
            ["Dashboard Overview", "Distribution Analysis", "Category Comparison", "Correlation Analysis", "Trend Over Time"],
            label_visibility="collapsed"
        )
    else:
        filtered_df = None
        numeric_cols = []
        cat_cols = []
        analysis_type = None

# ─────────────────────────────────────────────
#  MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">◈ Smart Data Explorer</div>
    <div class="hero-title">Data<span>Lens</span></div>
    <div class="hero-sub">Drop in any CSV and instantly surface patterns, distributions, correlations, and trends — no code required.</div>
</div>
""", unsafe_allow_html=True)

# ── NO FILE STATE ──
if uploaded_file is None:
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-title">Upload a dataset to begin</div>
        <div class="upload-sub">CSV files · Any size · Instant analysis</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── METRICS ──
missing = filtered_df.isnull().sum().sum()
st.markdown(f"""
<div class="metrics-row">
    <div class="metric-card">
        <div class="metric-label">Rows</div>
        <div class="metric-value">{filtered_df.shape[0]:,}<span>rows</span></div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Columns</div>
        <div class="metric-value">{filtered_df.shape[1]}<span>cols</span></div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Missing Values</div>
        <div class="metric-value">{missing}<span>nulls</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── DATA PREVIEW ──
st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
st.dataframe(
    filtered_df.head(8),
    use_container_width=True,
    hide_index=True,
)

st.markdown("<hr>", unsafe_allow_html=True)

# ── ANALYSIS ──
st.markdown(f'<div class="section-label">{analysis_type}</div>', unsafe_allow_html=True)

# DASHBOARD OVERVIEW
if analysis_type == "Dashboard Overview":
    if len(numeric_cols) > 0:
        col_sel = st.selectbox("Numeric column — distribution", numeric_cols)
        fig = px.histogram(filtered_df, x=col_sel, nbins=30, title=f"Distribution · {col_sel}")
        fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.3)", marker_line_width=1)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    if len(cat_cols) > 0 and len(numeric_cols) > 0:
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox("Category column", cat_cols)
        with c2:
            num = st.selectbox("Numeric column", numeric_cols)
        grouped = filtered_df.groupby(cat)[num].mean().reset_index().sort_values(num, ascending=False)
        fig = px.bar(grouped, x=cat, y=num, title=f"Avg {num} by {cat}")
        fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.2)", marker_line_width=1)
        st.plotly_chart(style_fig(fig), use_container_width=True)

# DISTRIBUTION
elif analysis_type == "Distribution Analysis":
    if len(numeric_cols) == 0:
        st.warning("No numeric columns found.")
    else:
        column = st.selectbox("Numeric Column", numeric_cols)
        c1, c2 = st.columns(2)
        with c1:
            fig = px.histogram(filtered_df, x=column, nbins=30, title=f"Histogram · {column}")
            fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.3)", marker_line_width=1)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        with c2:
            fig2 = px.box(filtered_df, y=column, title=f"Box Plot · {column}")
            fig2.update_traces(marker_color="#ff5a32", line_color="#50b4ff")
            st.plotly_chart(style_fig(fig2), use_container_width=True)

# CATEGORY COMPARISON
elif analysis_type == "Category Comparison":
    if len(cat_cols) == 0 or len(numeric_cols) == 0:
        st.warning("Need both categorical and numeric columns.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox("Category Column", cat_cols)
        with c2:
            num = st.selectbox("Numeric Column", numeric_cols)
        grouped = filtered_df.groupby(cat)[num].mean().reset_index().sort_values(num, ascending=True)
        fig = px.bar(grouped, x=num, y=cat, orientation="h", title=f"Avg {num} by {cat}")
        fig.update_traces(marker_color="#ff5a32", marker_line_color="rgba(0,0,0,0.2)", marker_line_width=1)
        st.plotly_chart(style_fig(fig), use_container_width=True)

# CORRELATION
elif analysis_type == "Correlation Analysis":
    if len(numeric_cols) < 2:
        st.warning("Need at least two numeric columns.")
    else:
        corr = filtered_df[numeric_cols].corr()
        fig = px.imshow(
            corr,
            text_auto=".2f",
            title="Correlation Matrix",
            color_continuous_scale=[[0, "#0f0f18"], [0.5, "#1a1a2e"], [1, "#ff5a32"]],
        )
        fig.update_traces(textfont=dict(family="DM Mono", size=11, color="#f0ece4"))
        st.plotly_chart(style_fig(fig), use_container_width=True)

# TREND OVER TIME
elif analysis_type == "Trend Over Time":
    if len(numeric_cols) == 0:
        st.warning("Need numeric columns.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            date_col = st.selectbox("Time Column", filtered_df.columns)
        with c2:
            num_col = st.selectbox("Value Column", numeric_cols)
        fig = px.line(filtered_df, x=date_col, y=num_col, title=f"{num_col} over Time")
        fig.update_traces(line_color="#ff5a32", line_width=2)
        fig.update_layout(fill="tozeroy")
        st.plotly_chart(style_fig(fig), use_container_width=True)

# ─────────────────────────────────────────────
#  KEY INSIGHTS
# ─────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Key Insights</div>', unsafe_allow_html=True)

numeric_df = filtered_df.select_dtypes(include="number")

if len(numeric_df.columns) > 0:
    highest_mean = numeric_df.mean().idxmax()
    highest_var = numeric_df.var().idxmax()
    mean_val = numeric_df[highest_mean].mean()
    var_val = numeric_df[highest_var].var()

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-icon">◈ Highest Average</div>
        <strong>{highest_mean}</strong> has the highest mean value across all numeric columns
        — averaging <strong>{mean_val:,.2f}</strong>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-icon">◈ Most Variable</div>
        <strong>{highest_var}</strong> shows the greatest spread in the data
        — variance of <strong>{var_val:,.2f}</strong>.
    </div>
    """, unsafe_allow_html=True)

    if len(numeric_df.columns) > 1:
        corr = numeric_df.corr().abs()
        corr_unstack = corr.unstack()
        corr_unstack = corr_unstack[corr_unstack < 1]
        if not corr_unstack.empty:
            strongest = corr_unstack.idxmax()
            corr_val = corr_unstack.max()
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-icon">◈ Strongest Correlation</div>
                <strong>{strongest[0]}</strong> and <strong>{strongest[1]}</strong> are the most
                correlated pair — correlation coefficient of <strong>{corr_val:.3f}</strong>.
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No numeric columns available for insights.")
