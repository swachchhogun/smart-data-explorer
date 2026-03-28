"""
app.py  —  DataLens · Smart CSV Data Explorer
Entry point. Imports all modules and orchestrates the Streamlit UI.

  app.py          ← you are here
  config.py       ← theme tokens & constants
  styles.py       ← CSS + JS injection
  data_utils.py   ← CSV reading, cleaning, type overrides, export
  chart_utils.py  ← Plotly helpers, sparklines, NL chart renderer, dashboard builder
  ai_utils.py     ← Groq API: insights + NL-to-chart-spec
  pdf_utils.py    ← ReportLab PDF report generator
  samples.py      ← built-in sample datasets
"""

import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config      import get_theme, TYPE_OPTIONS
from styles      import inject
from data_utils  import safe_read_csv, smart_clean, apply_type_overrides, to_excel_bytes, col_health
from chart_utils import (style_fig, add_annotations_to_fig, make_sparkline_svg,
                         render_nl_chart, empty_state, ai_card_html, build_dashboard_fig)
from ai_utils    import get_ai_insights, build_summary, nl_to_chart_spec
from pdf_utils   import generate_pdf_report
from samples     import make_sample_dataset, SAMPLES

# ── Page config ────────────────────────────────────────────
st.set_page_config(page_title="DataLens", page_icon="◈",
                   layout="wide", initial_sidebar_state="collapsed")

# ── Session state ──────────────────────────────────────────
for k, v in [("annotations",[]), ("type_overrides",{}), ("show_app",False),
             ("dark_mode",True), ("last_ai_text",""), ("sample_df",None), ("sample_name","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme ──────────────────────────────────────────────────
T, COLORS, AI_CARD_BG, AI_CARD_SH, BADGE_BG, BADGE_BDR, PILL_BG, PILL_BDR = get_theme()
inject(T, COLORS, AI_CARD_BG, AI_CARD_SH, BADGE_BG, BADGE_BDR, PILL_BG, PILL_BDR)

# ── Theme-baked helpers ────────────────────────────────────
def _sf(fig):        return style_fig(fig, T, COLORS)
def _an(fig, anns):  return add_annotations_to_fig(fig, anns, T)
def hcolor(score):
    if score >= 80: return T["green"]
    if score >= 50: return T["yellow"]
    return T["accent"]

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Data<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">◈ Smart Explorer</div>', unsafe_allow_html=True)
    if st.session_state.get("working_df") is not None:
        wdf    = st.session_state.working_df
        num_sb = wdf.select_dtypes(include="number").columns.tolist()
        cat_sb = wdf.select_dtypes(include="object").columns.tolist()
        st.markdown("---")
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{T["text_dim"]};margin-bottom:0.75rem;">Filters</div>', unsafe_allow_html=True)
        fdf = wdf.copy()
        for col in cat_sb[:3]:
            opts = st.multiselect(col, sorted(wdf[col].dropna().unique().tolist()), key=f"sb_f_{col}")
            if opts: fdf = fdf[fdf[col].isin(opts)]
        for col in num_sb[:2]:
            cmin, cmax = float(wdf[col].min()), float(wdf[col].max())
            if cmin < cmax:
                rng = st.slider(col, cmin, cmax, (cmin, cmax), key=f"sb_r_{col}")
                fdf = fdf[fdf[col].between(*rng)]
        st.session_state.filtered_df = fdf
        st.markdown("---")
        st.download_button("↓ Export filtered CSV", data=fdf.to_csv(index=False).encode("utf-8"),
                           file_name="datalens_export.csv", mime="text/csv", use_container_width=True)
        if st.button("← Start over", use_container_width=True):
            for k in ["working_df","filtered_df","raw_df","cleaned_df","clean_report",
                      "show_app","annotations","type_overrides","sample_df","sample_name",
                      "nl_run_prompt","nl_auto_run","last_ai_text"]:
                st.session_state.pop(k, None)
            st.rerun()
    else:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;color:{T["text_faint"]};text-transform:uppercase;padding:0.5rem 0;">Upload a CSV on the main page to unlock filters & export.</div>', unsafe_allow_html=True)

# ── Theme toggle ───────────────────────────────────────────
_icon = "☀️ Day" if st.session_state.dark_mode else "🌙 Night"
st.markdown('<div class="theme-pill-wrap">', unsafe_allow_html=True)
_gap, _pill = st.columns([30, 1])
with _pill:
    if st.button(_icon, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Welcome page ───────────────────────────────────────────
if not st.session_state.show_app:
    st.markdown(f"""
    <div class="welcome-wrap">
        <div class="welcome-eyebrow">◈ Smart Data Explorer</div>
        <div class="welcome-title">Data<span>Lens</span></div>
        <div class="welcome-sub">Upload any CSV and get an instant dashboard, AI-powered insights,
            charts, and a PDF report — completely free.</div>
        <div class="feature-grid">
            <div class="feature-card"><div class="feature-icon">📊</div>
                <div class="feature-title">Auto Dashboard</div>
                <div class="feature-desc">KPIs · Charts · Trend · Pie · Download</div></div>
            <div class="feature-card"><div class="feature-icon">⚡</div>
                <div class="feature-title">Auto Clean</div>
                <div class="feature-desc">Nulls · Dupes · Type inference</div></div>
            <div class="feature-card"><div class="feature-icon">🤖</div>
                <div class="feature-title">Free AI</div>
                <div class="feature-desc">Llama 3.3 70B · Ask anything</div></div>
            <div class="feature-card"><div class="feature-icon">📄</div>
                <div class="feature-title">Export</div>
                <div class="feature-desc">PDF · CSV · Excel · Dashboard HTML</div></div>
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2px;
                    color:{T['text_faint']};text-transform:uppercase;margin-bottom:2rem;">
            Supports CSV up to 200MB &nbsp;·&nbsp; No signup &nbsp;·&nbsp; No data stored
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">Try a sample dataset</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.25rem;line-height:1.7;">No CSV? Load one of these instantly and explore all features right away.</div>', unsafe_allow_html=True)
    s_cols = st.columns(4)
    for i, (sname, smeta) in enumerate(SAMPLES.items()):
        with s_cols[i]:
            st.markdown(f"""<div style="background:{T['card']};border:1px solid {T['divider']};
                border-top:2px solid {T['accent']};padding:1.25rem 1rem 1rem;margin-bottom:0.5rem;">
                <div style="font-size:24px;margin-bottom:0.5rem;">{smeta['icon']}</div>
                <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:700;color:{T['text_head']};margin-bottom:0.3rem;">{sname}</div>
                <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['text_dim']};letter-spacing:1px;text-transform:uppercase;margin-bottom:0.5rem;">{smeta['rows']} rows · {smeta['cols']} cols</div>
                <div style="font-family:'DM Sans',sans-serif;font-size:12px;color:{T['text_muted']};line-height:1.5;">{smeta['desc']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Load →", key=f"sample_{i}", use_container_width=True):
                st.session_state.sample_df   = make_sample_dataset(sname)
                st.session_state.sample_name = sname
                st.session_state.show_app    = True
                st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("◈ Upload your own CSV instead", use_container_width=True):
            st.session_state.show_app = True; st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════
# ── Main app ──────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
st.markdown('<div class="section-label">Upload Your Data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is not None:
    st.session_state.sample_df   = None
    st.session_state.sample_name = ""

if uploaded_file is None and st.session_state.get("sample_df") is not None:
    raw_df, load_err, _is_sample = st.session_state.sample_df.copy(), None, True
elif uploaded_file is not None:
    with st.spinner("Reading file…"):
        raw_df, load_err = safe_read_csv(uploaded_file)
    _is_sample = False
else:
    st.markdown('<div class="empty-state" style="margin-top:1rem;"><div class="empty-state-icon">📂</div><div class="empty-state-title">Drop a CSV file above</div><div class="empty-state-sub">Any CSV · Auto-cleaned · Free AI · PDF report</div></div>', unsafe_allow_html=True)
    st.stop()
    _is_sample = False

if load_err or raw_df is None:
    st.markdown(f'<div class="error-box"><strong>Could not load file</strong><br>{load_err}</div>', unsafe_allow_html=True); st.stop()
if raw_df.empty:
    st.markdown('<div class="error-box"><strong>Empty file</strong><br>The CSV has no data rows.</div>', unsafe_allow_html=True); st.stop()

st.session_state.raw_df = raw_df
try: cleaned_df, clean_report = smart_clean(raw_df)
except Exception as e: cleaned_df, clean_report = raw_df.copy(), [f"Cleaning failed: {e}"]
st.session_state.cleaned_df   = cleaned_df
st.session_state.clean_report = clean_report

use_cleaned = st.toggle("Auto-clean data", value=True, help="Fills nulls, fixes types, removes duplicates")
base_df = cleaned_df if use_cleaned else raw_df
if st.session_state.type_overrides:
    base_df = apply_type_overrides(base_df, st.session_state.type_overrides)
st.session_state.working_df = base_df

if (st.session_state.get("filtered_df") is not None
        and list(st.session_state.filtered_df.columns) == list(base_df.columns)):
    filtered_df = st.session_state.filtered_df
else:
    filtered_df = base_df.copy(); st.session_state.filtered_df = filtered_df

numeric_cols = base_df.select_dtypes(include="number").columns.tolist()
cat_cols     = base_df.select_dtypes(include="object").columns.tolist()
date_cols    = [c for c in filtered_df.columns
                if pd.api.types.is_datetime64_any_dtype(filtered_df[c])
                or c.lower() in ["date","order date","time","month","year","day","week","period"]]

if clean_report and use_cleaned:
    with st.expander(f"✦ Cleaning applied — {len(clean_report)} action{'s' if len(clean_report)!=1 else ''}"):
        for n in clean_report:
            st.markdown(f'<span class="clean-badge">✓ {n}</span>', unsafe_allow_html=True)

fn = st.session_state.get("sample_name") or (uploaded_file.name if uploaded_file else "dataset.csv")
missing_count = int(filtered_df.isnull().sum().sum())
dupe_count    = int(filtered_df.duplicated().sum())
completeness  = round((1 - missing_count / max(filtered_df.size,1)) * 100, 1)
mem_kb        = filtered_df.memory_usage(deep=True).sum() / 1024

# Hero
sample_badge = (f' &nbsp;<span style="background:{T["accent_bg"]};border:1px solid {T["accent_bdr"]};color:{T["accent"]};font-size:8px;padding:2px 7px;border-radius:2px;letter-spacing:1px;">SAMPLE</span>'
                if _is_sample else "")
st.markdown(f"""<div class="hero">
    <div class="hero-eyebrow">◈ Smart Data Explorer</div>
    <div class="hero-title">Data<span>Lens</span></div>
    <div class="hero-file">◈ {fn} · {filtered_df.shape[0]:,} rows · {filtered_df.shape[1]} cols{sample_badge}</div>
</div>""", unsafe_allow_html=True)

# Metric cards
st.markdown(f"""<div class="metrics-row">
  <div class="metric-card"><div class="metric-label">Rows</div><div class="metric-value">{filtered_df.shape[0]:,}<span>r</span></div><div class="metric-sub">of {base_df.shape[0]:,} total</div></div>
  <div class="metric-card"><div class="metric-label">Columns</div><div class="metric-value">{filtered_df.shape[1]}<span>c</span></div><div class="metric-sub">{len(numeric_cols)} num · {len(cat_cols)} cat</div></div>
  <div class="metric-card"><div class="metric-label">Complete</div><div class="metric-value">{completeness}<span>%</span></div><div class="metric-sub">{missing_count:,} nulls</div></div>
  <div class="metric-card"><div class="metric-label">Duplicates</div><div class="metric-value">{dupe_count}<span>r</span></div><div class="metric-sub">{"✓ none" if dupe_count==0 else "⚠ detected"}</div></div>
  <div class="metric-card"><div class="metric-label">Memory</div><div class="metric-value">{mem_kb:.0f}<span>kb</span></div><div class="metric-sub">in memory</div></div>
</div>""", unsafe_allow_html=True)

# Status bar
dot_color  = T["green"] if completeness >= 80 else (T["yellow"] if completeness >= 50 else T["accent"])
clean_txt  = f"{len(clean_report)} ops applied" if (use_cleaned and clean_report) else "raw mode"
filter_act = filtered_df.shape[0] != base_df.shape[0]
filter_txt = f"{filtered_df.shape[0]:,} / {base_df.shape[0]:,} rows" if filter_act else "all rows"
filter_clr = T["accent"] if filter_act else T["text_dim"]
st.markdown(f"""<div class="status-bar">
    <div class="status-item"><span class="status-dot" style="background:{dot_color};box-shadow:0 0 6px {dot_color};"></span><span>Completeness <strong>{completeness}%</strong></span></div>
    <div class="status-item">◈ <strong style="color:{T['text_head']}">{filtered_df.shape[0]:,}</strong> rows &nbsp;·&nbsp; <strong style="color:{T['text_head']}">{filtered_df.shape[1]}</strong> cols</div>
    <div class="status-item" style="color:{filter_clr};">◈ {filter_txt}</div>
    <div class="status-item">◈ {clean_txt}</div>
    <div class="status-item" style="margin-left:auto;">◈ {"☀ Day" if not st.session_state.dark_mode else "◑ Night"}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Analysis Mode</div>', unsafe_allow_html=True)
analysis_type = st.selectbox("Mode", [
    "Dashboard Overview","Distribution Analysis","Category Comparison",
    "Correlation Analysis","Trend Over Time","Scatter Explorer",
    "Heatmap","Box Plot Comparison","Scatter Matrix",
], label_visibility="collapsed")

tab_dash, tab_explore, tab_nl, tab_quality, tab_types, tab_stats, tab_ai, tab_report = st.tabs([
    "◈  Dashboard","◈  Explore","◈  AI Chart","◈  Data Quality",
    "◈  Column Types","◈  Statistics","◈  AI Insights","◈  PDF Report",
])
accent = T["accent"]

# ═══ DASHBOARD ═════════════════════════════════════════════
with tab_dash:
    st.markdown('<div class="section-label">Auto Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.25rem;line-height:1.7;">DataLens reads your columns and auto-builds the most relevant dashboard. Download as interactive HTML or PNG.</div>', unsafe_allow_html=True)

    # ── KPI row ──────────────────────────────────────────
    # Find best value column
    value_col_d = numeric_cols[0] if numeric_cols else None
    for kw in ["revenue","sales","profit","amount","value","price","score","total","income"]:
        for c in numeric_cols:
            if kw in c.lower():
                value_col_d = c; break

    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T["accent"]};margin-bottom:0.6rem;">Key Metrics</div>', unsafe_allow_html=True)
    kpi_cols = st.columns(4)
    kpis = []
    if value_col_d:
        kpis.append({"label":f"Total {value_col_d}","value":f"{filtered_df[value_col_d].sum():,.0f}","sub":f"avg {filtered_df[value_col_d].mean():,.1f}"})
        kpis.append({"label":f"Max {value_col_d}","value":f"{filtered_df[value_col_d].max():,.0f}","sub":f"min {filtered_df[value_col_d].min():,.0f}"})
    else:
        kpis.append({"label":"Total Rows","value":f"{len(filtered_df):,}","sub":"records"})
    if cat_cols:
        top_cat = filtered_df[cat_cols[0]].value_counts().index[0]
        top_pct = round(filtered_df[cat_cols[0]].value_counts().iloc[0]/len(filtered_df)*100,1)
        kpis.append({"label":f"Top {cat_cols[0]}","value":str(top_cat),"sub":f"{top_pct}% of data"})
    kpis.append({"label":"Completeness","value":f"{completeness}%","sub":f"{missing_count:,} nulls"})
    kpis.append({"label":"Total Rows","value":f"{len(filtered_df):,}","sub":f"{len(filtered_df.columns)} columns"})

    for i, kpi in enumerate(kpis[:4]):
        with kpi_cols[i]:
            st.markdown(f"""<div style="background:{T['card']};border:1px solid {T['divider']};
                border-top:2px solid {T['accent']};padding:1rem;text-align:center;margin-bottom:0.75rem;">
                <div style="font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T['text_dim']};margin-bottom:0.3rem;">{kpi['label']}</div>
                <div style="font-family:'Syne',sans-serif;font-size:clamp(16px,3vw,26px);font-weight:800;color:{T['text_head']};line-height:1;letter-spacing:-1px;">{kpi['value']}</div>
                <div style="font-family:'DM Mono',monospace;font-size:9px;color:{T['accent']};margin-top:4px;">{kpi['sub']}</div>
            </div>""", unsafe_allow_html=True)

    # ── Dashboard figure ─────────────────────────────────
    try:
        fig_dash, has_date, vcol, bcat, bnum = build_dashboard_fig(
            filtered_df, fn, T, COLORS,
            numeric_cols, cat_cols, date_cols,
            missing_count, completeness,
        )
        st.plotly_chart(fig_dash, use_container_width=True, config={
            "displayModeBar": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"datalens_dashboard_{fn.replace('.csv','').replace(' ','_')}",
                "height": 900, "width": 1600, "scale": 2,
            },
        })
    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Dashboard error</strong><br>{e}</div>', unsafe_allow_html=True)
        fig_dash = None
        has_date = False

    # ── Download row ────────────────────────────────────
    dl1, dl2, dl3 = st.columns(3)
    with dl1:
        st.download_button("↓ Download data (CSV)",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name=f"datalens_{fn.replace('.csv','')}_data.csv",
            mime="text/csv", use_container_width=True)
    with dl2:
        if fig_dash is not None:
            html_str = fig_dash.to_html(include_plotlyjs="cdn", full_html=True,
                                         config={"responsive":True})
            st.download_button("↓ Download dashboard (HTML)",
                data=html_str.encode("utf-8"),
                file_name=f"datalens_dashboard_{fn.replace('.csv','').replace(' ','_')}.html",
                mime="text/html", use_container_width=True)
    with dl3:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;color:{T["text_faint"]};padding:0.7rem 0;text-align:center;">Use the 📷 icon on the chart above to save as PNG</div>', unsafe_allow_html=True)

    _date_txt = "trend detected" if has_date else "no date column"
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;color:{T["text_faint"]};margin-top:0.5rem;">◈ Auto-built · {_date_txt} · {len(numeric_cols)} numeric · {len(cat_cols)} categorical</div>', unsafe_allow_html=True)

# ═══ EXPLORE ═══════════════════════════════════════════════
with tab_explore:
    st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df.head(10), use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{analysis_type}</div>', unsafe_allow_html=True)

    with st.expander("◈ Chart Annotations", expanded=False):
        ann_text = st.text_input("Annotation text", placeholder="e.g. Sharp spike in Q3", key="ann_text")
        c1,c2,c3 = st.columns(3)
        with c1: ann_x     = st.number_input("X (0–1)", 0.0, 1.0, 0.5, 0.05, key="ann_x")
        with c2: ann_y_val = st.number_input("Y (0–1)", 0.0, 1.0, 0.9, 0.05, key="ann_y")
        with c3: ann_arrow = st.toggle("Arrow", value=True, key="ann_arrow")
        if st.button("◈ Add annotation", key="add_ann"):
            if ann_text.strip():
                st.session_state.annotations.append({"text":ann_text.strip(),"x":ann_x,"y":ann_y_val,"xref":"paper","yref":"paper","arrow":ann_arrow})
                st.toast(f"Added: {ann_text.strip()}", icon="✅")
            else:
                st.toast("Enter some text first", icon="⚠️")
        if st.session_state.annotations:
            st.markdown('<div class="annotation-panel">', unsafe_allow_html=True)
            for i, ann in enumerate(st.session_state.annotations):
                st.markdown(f'<div class="annotation-item"><div class="annotation-tag">◈ Note {i+1}</div>{ann["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("✕ Clear all annotations", key="clear_ann"):
                st.session_state.annotations = []; st.rerun()

    anns = st.session_state.annotations
    try:
        if analysis_type == "Dashboard Overview":
            if not numeric_cols:
                st.markdown(empty_state("📊","No numeric columns","Upload a dataset with numeric data"), unsafe_allow_html=True)
            else:
                col_sel    = st.selectbox("Numeric column", numeric_cols, key="dash_num")
                chart_type = st.selectbox("Chart type", ["Histogram","Box Plot","Violin"], key="dash_chart")
                if chart_type == "Histogram":
                    fig = px.histogram(filtered_df, x=col_sel, nbins=30, title=f"Distribution · {col_sel}")
                    fig.update_traces(marker_color=accent, marker_line_color="rgba(0,0,0,0.15)", marker_line_width=1)
                elif chart_type == "Box Plot":
                    fig = px.box(filtered_df, y=col_sel, title=f"Box Plot · {col_sel}")
                    fig.update_traces(marker_color=accent, line_color=T["blue"])
                else:
                    fig = px.violin(filtered_df, y=col_sel, title=f"Violin · {col_sel}", box=True)
                    fig.update_traces(fillcolor=T["accent_glow"], line_color=accent)
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)
            if cat_cols and numeric_cols:
                st.markdown("<hr>", unsafe_allow_html=True)
                cat = st.selectbox("Category column", cat_cols, key="dash_cat")
                num = st.selectbox("Numeric column", numeric_cols, key="dash_num2")
                agg = st.selectbox("Aggregation", ["Mean","Sum","Median","Count"], key="dash_agg")
                agg_fn = {"Mean":"mean","Sum":"sum","Median":"median","Count":"count"}[agg]
                grouped = filtered_df.groupby(cat)[num].agg(agg_fn).reset_index().sort_values(num, ascending=False).head(20)
                fig2 = px.bar(grouped, x=cat, y=num, title=f"{agg} of {num} by {cat}")
                fig2.update_traces(marker_color=accent, marker_line_width=0)
                st.plotly_chart(_sf(_an(fig2, anns)), use_container_width=True)

        elif analysis_type == "Distribution Analysis":
            if not numeric_cols: st.markdown(empty_state("📈","No numeric columns","Need numeric data"), unsafe_allow_html=True)
            else:
                column   = st.selectbox("Numeric Column", numeric_cols, key="dist_col")
                color_by = st.selectbox("Color by (optional)", ["None"]+cat_cols, key="dist_color")
                ca = None if color_by == "None" else color_by
                fig = px.histogram(filtered_df, x=column, color=ca, nbins=30, title=f"Histogram · {column}", barmode="overlay", opacity=0.8)
                if not ca: fig.update_traces(marker_color=accent, marker_line_color="rgba(0,0,0,0.12)", marker_line_width=1)
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)
                fig2 = px.violin(filtered_df, y=column, color=ca, title=f"Violin · {column}", box=True)
                if not ca: fig2.update_traces(fillcolor=T["accent_glow"], line_color=accent)
                st.plotly_chart(_sf(_an(fig2, anns)), use_container_width=True)

        elif analysis_type == "Category Comparison":
            if not cat_cols or not numeric_cols: st.markdown(empty_state("🗂️","Need categorical + numeric columns","Upload data with both types"), unsafe_allow_html=True)
            else:
                cat   = st.selectbox("Category", cat_cols, key="cat_cat")
                num   = st.selectbox("Numeric", numeric_cols, key="cat_num")
                agg   = st.selectbox("Aggregation", ["Mean","Sum","Median","Count"], key="cat_agg")
                chart = st.selectbox("Chart type", ["Bar","Treemap","Pie"], key="cat_chart")
                agg_fn  = {"Mean":"mean","Sum":"sum","Median":"median","Count":"count"}[agg]
                grouped = filtered_df.groupby(cat)[num].agg(agg_fn).reset_index().sort_values(num, ascending=True)
                if chart == "Bar":
                    fig = px.bar(grouped, x=num, y=cat, orientation="h", title=f"{agg} of {num} by {cat}")
                    fig.update_traces(marker_color=accent, marker_line_width=0)
                elif chart == "Treemap":
                    fig = px.treemap(grouped, path=[cat], values=num, title=f"{agg} of {num} by {cat}", color=num, color_continuous_scale=[T["card"],accent])
                else:
                    fig = px.pie(grouped, names=cat, values=num, title=f"{agg} of {num} by {cat}", color_discrete_sequence=COLORS, hole=0.3)
                    fig.update_traces(textfont=dict(family="DM Mono", size=10))
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)

        elif analysis_type == "Correlation Analysis":
            if len(numeric_cols) < 2: st.markdown(empty_state("🔗","Need 2+ numeric columns","Correlation needs at least two numeric columns"), unsafe_allow_html=True)
            else:
                method = st.selectbox("Method", ["pearson","spearman","kendall"], key="corr_method")
                corr   = filtered_df[numeric_cols].corr(method=method)
                fig    = px.imshow(corr, text_auto=".2f", title=f"Correlation Matrix ({method.title()})", color_continuous_scale=[[0,T["blue"]],[0.5,T["card"]],[1,accent]], zmin=-1, zmax=1)
                fig.update_traces(textfont=dict(family="DM Mono", size=10, color=T["text_head"]))
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)
                st.markdown('<div class="section-label">Top Correlated Pairs</div>', unsafe_allow_html=True)
                cp = corr.abs().unstack().sort_values(ascending=False)
                cp = cp[cp < 1].drop_duplicates().head(8)
                for (c1n,c2n), val in cp.items():
                    d = "↑" if corr.loc[c1n,c2n] > 0 else "↓"; clr = T["green"] if corr.loc[c1n,c2n] > 0 else accent
                    st.markdown(f'<div style="border-bottom:1px solid {T["divider_faint"]};padding:8px 0;font-family:DM Mono,monospace;font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;"><span style="color:{T["text_head"]}">{c1n} <span style="color:{T["text_faint"]}">×</span> {c2n}</span><span style="color:{clr}">{d} {val:.3f}</span></div>', unsafe_allow_html=True)

        elif analysis_type == "Trend Over Time":
            date_col = st.selectbox("Time Column", list(filtered_df.columns), key="trend_date")
            if not numeric_cols: st.markdown(empty_state("📉","No numeric columns","Need a numeric value column"), unsafe_allow_html=True)
            else:
                num_col = st.selectbox("Value Column", numeric_cols, key="trend_val")
                smooth  = st.selectbox("Smoothing", ["None","7-period MA","30-period MA"], key="trend_smooth")
                plot_df = filtered_df[[date_col,num_col]].dropna().sort_values(date_col)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df[num_col], mode="lines", name="Raw", line=dict(color=T["accent_glow"], width=1)))
                if smooth != "None":
                    w = 7 if "7" in smooth else 30
                    plot_df = plot_df.copy(); plot_df["_ma"] = plot_df[num_col].rolling(w, min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df["_ma"], mode="lines", name=smooth, line=dict(color=accent, width=2.5)))
                fig.update_layout(title=f"{num_col} over Time")
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)

        elif analysis_type == "Scatter Explorer":
            if len(numeric_cols) < 2: st.markdown(empty_state("🔵","Need 2+ numeric columns","Scatter needs at least two numeric columns"), unsafe_allow_html=True)
            else:
                x_col     = st.selectbox("X Axis", numeric_cols, key="sc_x")
                y_col     = st.selectbox("Y Axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="sc_y")
                color_col = st.selectbox("Color by (optional)", ["None"]+cat_cols+numeric_cols, key="sc_col")
                size_col  = st.selectbox("Size by (optional)", ["None"]+numeric_cols, key="sc_sz")
                ca = None if color_col=="None" else color_col; sa = None if size_col=="None" else size_col
                fig = px.scatter(filtered_df, x=x_col, y=y_col, color=ca, size=sa, title=f"{y_col} vs {x_col}",
                                 opacity=0.72, trendline="ols" if ca is None else None,
                                 color_discrete_sequence=COLORS, color_continuous_scale=[[0,T["card"]],[1,accent]])
                if ca is None and sa is None:
                    fig.update_traces(marker=dict(color=accent, size=6, line=dict(color="rgba(0,0,0,0.12)", width=1)))
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)

        elif analysis_type == "Heatmap":
            if not cat_cols or not numeric_cols:
                st.markdown(empty_state("🟥","Need categorical + numeric columns","Heatmap requires both column types"), unsafe_allow_html=True)
            else:
                row_col = st.selectbox("Row", cat_cols, key="hm_row")
                col_col = st.selectbox("Column", [c for c in cat_cols if c != row_col] or cat_cols, key="hm_col")
                val_col = st.selectbox("Value (aggregated)", numeric_cols, key="hm_val")
                agg_sel = st.selectbox("Aggregation", ["Mean","Sum","Count","Median"], key="hm_agg")
                fn_map  = {"Mean":"mean","Sum":"sum","Count":"count","Median":"median"}
                pivot_df = filtered_df.groupby([row_col, col_col])[val_col].agg(fn_map[agg_sel]).reset_index()
                pivot    = pivot_df.pivot(index=row_col, columns=col_col, values=val_col).fillna(0)
                fig = px.imshow(pivot, text_auto=".1f", title=f"{agg_sel} of {val_col} · {row_col} vs {col_col}",
                                color_continuous_scale=[[0,T["plot_bg"]],[0.5,T["blue"]],[1,accent]], aspect="auto")
                fig.update_traces(textfont=dict(family="DM Mono", size=9))
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)

        elif analysis_type == "Box Plot Comparison":
            if not numeric_cols:
                st.markdown(empty_state("📦","No numeric columns","Need numeric data for box plots"), unsafe_allow_html=True)
            else:
                mode = st.radio("Mode", ["Multi-column","Split by category"], horizontal=True, key="bp_mode")
                if mode == "Multi-column":
                    cols_sel = st.multiselect("Columns to compare", numeric_cols, default=numeric_cols[:min(4,len(numeric_cols))], key="bp_cols")
                    if cols_sel:
                        melt_df = filtered_df[cols_sel].melt(var_name="Column", value_name="Value")
                        fig = px.box(melt_df, x="Column", y="Value", title="Box Plot Comparison", color="Column", color_discrete_sequence=COLORS)
                        fig.update_traces(marker=dict(size=4, opacity=0.5))
                        st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)
                else:
                    if not cat_cols:
                        st.markdown(empty_state("🗂️","No categorical columns","Need a category column to split by"), unsafe_allow_html=True)
                    else:
                        num_sel = st.selectbox("Numeric column", numeric_cols, key="bp_num")
                        cat_sel = st.selectbox("Split by", cat_cols, key="bp_cat")
                        fig = px.box(filtered_df, x=cat_sel, y=num_sel, color=cat_sel, title=f"{num_sel} by {cat_sel}", color_discrete_sequence=COLORS, points="outliers")
                        fig.update_traces(marker=dict(size=4, opacity=0.6))
                        st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)

        elif analysis_type == "Scatter Matrix":
            if len(numeric_cols) < 2:
                st.markdown(empty_state("🔶","Need 2+ numeric columns","Scatter matrix needs at least two numeric columns"), unsafe_allow_html=True)
            else:
                max_cols = st.slider("Number of columns to include", 2, min(8,len(numeric_cols)), min(4,len(numeric_cols)), key="sm_n")
                cols_sel = numeric_cols[:max_cols]
                color_by = st.selectbox("Color by (optional)", ["None"]+cat_cols, key="sm_color")
                ca = None if color_by == "None" else color_by
                fig = px.scatter_matrix(filtered_df, dimensions=cols_sel, color=ca, title=f"Scatter Matrix · {len(cols_sel)} columns", color_discrete_sequence=COLORS, opacity=0.65)
                fig.update_traces(diagonal_visible=False, marker=dict(size=3, line=dict(width=0)))
                fig.update_layout(height=600)
                st.plotly_chart(_sf(_an(fig, anns)), use_container_width=True)

    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Chart error</strong><br>Try a different column or mode.<br><small style="opacity:0.4;font-family:DM Mono,monospace;font-size:11px;">{e}</small></div>', unsafe_allow_html=True)

# ═══ AI CHART ══════════════════════════════════════════════
with tab_nl:
    st.markdown('<div class="section-label">Natural Language Chart Builder</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.8;">Describe any chart in plain English and AI will build it instantly.</div>', unsafe_allow_html=True)

    examples = ["bar chart of count by category","scatter plot of the two most correlated columns",
                "histogram of the main numeric column","pie chart showing top categories",
                "line chart of values over time","box plot comparing a numeric column by category"]
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{T["text_dim"]};margin-bottom:0.6rem;">Try an example</div>', unsafe_allow_html=True)
    ex_cols = st.columns(3)
    for i, ex in enumerate(examples):
        with ex_cols[i % 3]:
            if st.button(ex, key=f"nl_ex_{i}"):
                st.session_state["nl_run_prompt"] = ex
                st.session_state["nl_auto_run"]   = True

    st.markdown("<br>", unsafe_allow_html=True)
    nl_prompt = st.text_input("Describe your chart", placeholder='"bar chart of average sales by region"', key="nl_input")
    nl_go = st.button("◈ Generate Chart", use_container_width=True, key="nl_go")

    if nl_go and nl_prompt.strip():
        st.session_state["nl_run_prompt"] = nl_prompt.strip()
        st.session_state["nl_auto_run"]   = True

    run_prompt = st.session_state.get("nl_run_prompt","")
    should_run = st.session_state.pop("nl_auto_run", False)

    if should_run and run_prompt:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:{T["text_dim"]};margin-bottom:0.75rem;">◈ Running: <span style="color:{T["accent"]}">{run_prompt}</span></div>', unsafe_allow_html=True)
        with st.spinner("Reading your request…"):
            spec = nl_to_chart_spec(run_prompt, list(filtered_df.columns), numeric_cols, cat_cols)

        if spec.get("error") == "no_key":
            st.markdown(f'<div class="error-box"><strong>Groq API key needed</strong><br>Add GROQ_API_KEY to Streamlit Secrets.</div>', unsafe_allow_html=True)
        elif spec.get("error"):
            st.markdown(f'<div class="error-box"><strong>Could not generate chart</strong><br>{spec["error"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="status-bar" style="margin-bottom:1.25rem;">
                <div class="status-item">◈ Type <strong style="color:{T['text_head']}">{spec.get("chart_type","—").title()}</strong></div>
                <div class="status-item">◈ X <strong style="color:{T['text_head']}">{spec.get("x") or "—"}</strong></div>
                <div class="status-item">◈ Y <strong style="color:{T['text_head']}">{spec.get("y") or "—"}</strong></div>
                <div class="status-item">◈ Agg <strong style="color:{T['text_head']}">{spec.get("aggregation","none")}</strong></div>
            </div>""", unsafe_allow_html=True)
            anns_nl = st.session_state.annotations
            fig, err = render_nl_chart(spec, filtered_df, T, COLORS, accent, anns_nl)
            if err:
                st.markdown(f'<div class="error-box"><strong>Render error</strong><br>{err}</div>', unsafe_allow_html=True)
            else:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;color:{T["text_faint"]};margin-top:0.5rem;">Generated from: "{run_prompt}"</div>', unsafe_allow_html=True)
    elif not run_prompt:
        st.markdown('<div class="section-label">Your columns</div>', unsafe_allow_html=True)
        cols_html = "".join([f'<span style="display:inline-block;background:{T["accent_bg"]};border:1px solid {T["accent_bdr"]};color:{T["accent"]};font-family:DM Mono,monospace;font-size:9px;padding:3px 10px;margin:3px;border-radius:2px;">{c}</span>' for c in filtered_df.columns])
        st.markdown(f'<div style="margin-bottom:1rem;">{cols_html}</div>', unsafe_allow_html=True)

# ═══ DATA QUALITY ══════════════════════════════════════════
with tab_quality:
    st.markdown('<div class="section-label">Before vs After Cleaning</div>', unsafe_allow_html=True)
    raw_nulls=int(raw_df.isnull().sum().sum()); raw_dupes=int(raw_df.duplicated().sum())
    cn=int(cleaned_df.isnull().sum().sum()); cd_d=int(cleaned_df.duplicated().sum())
    st.markdown(f"""<div class="metrics-row" style="grid-template-columns:repeat(2,1fr);margin-bottom:1.5rem;">
        <div class="metric-card"><div class="metric-label">Nulls — Raw</div><div class="metric-value" style="color:{T['accent']}">{raw_nulls:,}</div></div>
        <div class="metric-card"><div class="metric-label">Nulls — Cleaned</div><div class="metric-value" style="color:{T['green']}">{cn:,}</div></div>
        <div class="metric-card"><div class="metric-label">Dupes — Raw</div><div class="metric-value" style="color:{T['accent']}">{raw_dupes:,}</div></div>
        <div class="metric-card"><div class="metric-label">Dupes — Cleaned</div><div class="metric-value" style="color:{T['green']}">{cd_d:,}</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Column Health</div>', unsafe_allow_html=True)
    for col in base_df.columns:
        h = col_health(base_df[col]); bc = hcolor(h["score"])
        st.markdown(f"""<div class="quality-row">
            <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                    <span class="quality-col-name">{col}</span>
                    <span class="quality-col-type">{str(base_df[col].dtype)}</span>
                </div>
                <div class="quality-bar-wrap"><div class="quality-bar" style="width:{h['score']}%;background:{bc};"></div></div>
            </div>
            <div class="quality-col-stats">{h['null_pct']}% null<br>{h['unique']:,} unique</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Outlier Detection — IQR Method</div>', unsafe_allow_html=True)
    if not numeric_cols:
        st.markdown(empty_state("📊","No numeric columns","Outlier detection requires numeric data"), unsafe_allow_html=True)
    else:
        try:
            oc = st.selectbox("Column to inspect", numeric_cols, key="out_col")
            s  = filtered_df[oc].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3-q1; lo, hi = q1-1.5*iqr, q3+1.5*iqr
            outliers = filtered_df[(filtered_df[oc]<lo)|(filtered_df[oc]>hi)]
            pct  = round(len(outliers)/max(len(filtered_df),1)*100,1)
            flag = T["accent"] if pct > 5 else T["green"]
            st.markdown(f"""<div class="insight-card" style="border-left-color:{flag};">
                <div class="insight-icon">◈ {oc}</div>
                Normal range: <strong>{lo:,.2f}</strong> → <strong>{hi:,.2f}</strong> &nbsp;·&nbsp;
                <strong style="color:{flag}">{len(outliers):,} rows ({pct}%)</strong> outside bounds.
                {'⚠ Significant — worth investigating.' if pct > 5 else '✓ Small proportion — likely fine.'}
            </div>""", unsafe_allow_html=True)
            fig = px.box(filtered_df, y=oc, title=f"Box Plot · {oc}", points="outliers")
            fig.update_traces(marker_color=accent, line_color=T["blue"], marker=dict(color=accent, size=5, opacity=0.7))
            st.plotly_chart(_sf(fig), use_container_width=True)
            if len(outliers) > 0:
                with st.expander(f"View {min(len(outliers),50)} outlier rows"):
                    st.dataframe(outliers.head(50), use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Outlier error: {e}")

# ═══ COLUMN TYPES ══════════════════════════════════════════
with tab_types:
    st.markdown('<div class="section-label">Column Type Editor</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.7;">Override auto-detected column types. Changes apply immediately across all tabs.</div>', unsafe_allow_html=True)
    headers_html = "".join(f"<th>{h}</th>" for h in ["Column","Detected Type","Active Override"])
    st.markdown(f'<div class="table-wrap"><table class="type-table"><thead><tr>{headers_html}</tr></thead><tbody>', unsafe_allow_html=True)
    for col in base_df.columns:
        override_note = st.session_state.type_overrides.get(col,"—")
        clr = T["accent"] if col in st.session_state.type_overrides else T["text_faint"]
        st.markdown(f'<tr><td class="col-name">{col}</td><td><span class="type-pill">{str(base_df[col].dtype)}</span></td><td style="color:{clr};font-size:10px;">{override_note}</td></tr>', unsafe_allow_html=True)
    st.markdown("</tbody></table></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Set Override</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: sel_col  = st.selectbox("Column", base_df.columns.tolist(), key="type_col")
    with c2: sel_type = st.selectbox("New type", TYPE_OPTIONS, key="type_sel")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◈ Apply override", key="apply_type"):
            if sel_type != "Auto (keep as-is)":
                st.session_state.type_overrides[sel_col] = sel_type; st.toast(f"'{sel_col}' → {sel_type}", icon="✅")
            else:
                st.session_state.type_overrides.pop(sel_col, None); st.toast(f"Override removed for '{sel_col}'", icon="✅")
    with col2:
        if st.button("✕ Clear all overrides", key="clear_types"):
            st.session_state.type_overrides = {}; st.toast("All overrides cleared", icon="✅")
    if st.session_state.type_overrides:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Active Overrides</div>', unsafe_allow_html=True)
        for col, t in st.session_state.type_overrides.items():
            st.markdown(f'<span class="clean-badge">{col} → {t}</span>', unsafe_allow_html=True)

# ═══ STATISTICS ════════════════════════════════════════════
with tab_stats:
    if not numeric_cols and not cat_cols:
        st.markdown(empty_state("📋","Nothing to summarise","Upload data with numeric or categorical columns"), unsafe_allow_html=True)
    if numeric_cols:
        st.markdown('<div class="section-label">Numeric Summary</div>', unsafe_allow_html=True)
        try:
            stats = filtered_df[numeric_cols].describe().T
            stats["median"] = filtered_df[numeric_cols].median()
            stats["skew"]   = filtered_df[numeric_cols].skew().round(3)
            stats["nulls"]  = filtered_df[numeric_cols].isnull().sum()
            dc2   = ["count","mean","median","std","min","25%","75%","max","skew","nulls"]
            stats = stats[[c for c in dc2 if c in stats.columns]].round(3)
            rows_html = ""
            for cn2, row in stats.iterrows():
                col_vals = filtered_df[cn2].dropna().sample(min(80,len(filtered_df)),random_state=42).values
                spark    = make_sparkline_svg(col_vals, T["sparkline"])
                cells    = "".join(f"<td>{v:,.3f}</td>" if isinstance(v,float) else f"<td>{int(v)}</td>" for v in row.values)
                rows_html += f"<tr><td class='col-name'>{cn2}</td>{cells}<td class='sparkline-cell'>{spark}</td></tr>"
            headers = "".join(f"<th>{c}</th>" for c in ["Column"]+list(stats.columns)+["Trend"])
            st.markdown(f'<div class="table-wrap"><table class="stats-table"><thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button("↓ Export stats CSV", data=stats.to_csv().encode("utf-8"), file_name="datalens_stats.csv", mime="text/csv")
            with dl2:
                try:
                    xl = to_excel_bytes(filtered_df)
                    st.download_button("↓ Export full data XLSX", data=xl, file_name=f"datalens_{fn.replace('.csv','')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception:
                    st.caption("Install openpyxl to enable XLSX export.")
        except Exception as e:
            st.warning(f"Stats error: {e}")
    if cat_cols:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Categorical Summary</div>', unsafe_allow_html=True)
        try:
            cat_sel = st.selectbox("Column", cat_cols, key="stats_cat")
            vc = filtered_df[cat_sel].value_counts().reset_index()
            vc.columns = [cat_sel,"count"]; vc["percent"] = (vc["count"]/vc["count"].sum()*100).round(1)
            st.dataframe(vc.head(15), use_container_width=True, hide_index=True)
            fig = px.bar(vc.head(15), x="count", y=cat_sel, orientation="h", title=f"Value Counts · {cat_sel}")
            fig.update_traces(marker_color=accent, marker_line_width=0)
            st.plotly_chart(_sf(fig), use_container_width=True)
        except Exception as e:
            st.warning(f"Categorical error: {e}")

# ═══ AI INSIGHTS ═══════════════════════════════════════════
with tab_ai:
    st.markdown('<div class="section-label">AI-Powered Analysis</div>', unsafe_allow_html=True)
    has_key = bool(st.secrets.get("GROQ_API_KEY",""))
    if not has_key:
        st.markdown(f"""<div class="error-box"><strong>Free AI setup — 2 mins, no card needed:</strong><br><br>
            1. Go to <strong>console.groq.com</strong> → sign up free<br>
            2. Click API Keys → Create key<br>
            3. Streamlit Cloud → Settings → Secrets:<br><br>
            <code style="background:{T['accent_bg']};padding:4px 10px;font-family:DM Mono,monospace;font-size:12px;">GROQ_API_KEY = "gsk_xxxx"</code>
        </div>""", unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.25rem;line-height:1.7;">Ask anything about your dataset in plain English — or scroll down for auto-generated insights.</div>', unsafe_allow_html=True)
    question  = st.text_input("Ask a question", placeholder="e.g. Which columns are most correlated? What are the main outliers?", key="ai_q")
    run_ai    = st.button("◈ Analyse with AI", use_container_width=True)
    data_json = build_summary(filtered_df)
    if run_ai or question:
        with st.spinner("Thinking…"):
            result = get_ai_insights(data_json, question)
        st.session_state.last_ai_text = result
        st.markdown(ai_card_html("AI Answer · Llama 3.3 70B via Groq", result), unsafe_allow_html=True)
    else:
        with st.spinner("Generating auto insights…"):
            auto = get_ai_insights(data_json)
        st.session_state.last_ai_text = auto
        st.markdown(ai_card_html("Auto Insights · Llama 3.3 70B via Groq", auto), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Statistical Quick Insights</div>', unsafe_allow_html=True)
    try:
        ndf = filtered_df.select_dtypes(include="number")
        if len(ndf.columns) > 0:
            hmc=ndf.mean().idxmax(); hvc=ndf.var().idxmax()
            st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Highest Average</div><strong>{hmc}</strong> has the highest mean at <strong>{ndf[hmc].mean():,.2f}</strong>.</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Most Variable</div><strong>{hvc}</strong> shows the greatest spread — variance <strong>{ndf[hvc].var():,.2f}</strong>.</div>', unsafe_allow_html=True)
            if len(ndf.columns) > 1:
                corr=ndf.corr().abs(); cu=corr.unstack(); cu=cu[cu<1].drop_duplicates()
                if not cu.empty:
                    strongest=cu.idxmax(); rc=ndf.corr().loc[strongest[0],strongest[1]]
                    d="positively" if rc>0 else "negatively"; strength="Strong" if cu.max()>0.7 else "Moderate"
                    st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Strongest Correlation</div><strong>{strongest[0]}</strong> and <strong>{strongest[1]}</strong> are {d} correlated (r = <strong>{cu.max():.3f}</strong>). {strength} relationship.</div>', unsafe_allow_html=True)
            skews=ndf.skew().abs().sort_values(ascending=False)
            if len(skews)>0 and skews.iloc[0]>1:
                st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Skewed Distribution</div><strong>{skews.index[0]}</strong> is heavily skewed (skew = {skews.iloc[0]:.2f}). Consider log-transforming before modelling.</div>', unsafe_allow_html=True)
        if missing_count > 0:
            pct=round(missing_count/max(filtered_df.size,1)*100,1); flag=T["accent"] if pct>5 else T["yellow"]
            st.markdown(f'<div class="insight-card" style="border-left-color:{flag};"><div class="insight-icon">◈ Data Quality</div><strong>{missing_count:,}</strong> missing values ({pct}%). {"Significant — consider further imputation." if pct>5 else "Manageable."}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Quick insights error: {e}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Export Filtered Data</div>', unsafe_allow_html=True)
    dl_c1, dl_c2 = st.columns(2)
    with dl_c1:
        st.download_button("↓ Export as CSV", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name="datalens_export.csv", mime="text/csv")
    with dl_c2:
        try:
            xl = to_excel_bytes(filtered_df)
            st.download_button("↓ Export as XLSX", data=xl, file_name=f"datalens_{fn.replace('.csv','')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            st.caption("Install openpyxl for XLSX export.")

# ═══ PDF REPORT ════════════════════════════════════════════
with tab_report:
    st.markdown('<div class="section-label">Download PDF Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.8;">Generate a professionally formatted PDF with your dataset overview, column health, numeric statistics, cleaning summary, and AI insights.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-card"><div class="insight-icon">◈ Report includes</div>Cover page &nbsp;·&nbsp; Dataset overview &nbsp;·&nbsp; Column health &nbsp;·&nbsp; Numeric statistics &nbsp;·&nbsp; Cleaning report &nbsp;·&nbsp; AI insights</div>', unsafe_allow_html=True)
    if not st.session_state.get("last_ai_text"):
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:1px;color:{T["text_faint"]};margin-bottom:1rem;text-transform:uppercase;">Tip — run AI Insights first to include AI analysis in your PDF.</div>', unsafe_allow_html=True)
    ai_text_for_pdf = st.session_state.get("last_ai_text") or "No AI insights generated yet."
    if st.button("◈ Generate PDF Report", use_container_width=True, key="gen_pdf"):
        with st.spinner("Building your report…"):
            pdf_bytes = generate_pdf_report(filtered_df, fn, ai_text_for_pdf, clean_report if use_cleaned else [])
        if pdf_bytes:
            st.download_button("↓ Download Report PDF", data=pdf_bytes,
                               file_name=f"datalens_{fn.replace('.csv','').replace(' ','_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                               mime="application/pdf", use_container_width=True)
            st.markdown(f'<div class="insight-card" style="border-left-color:{T["green"]};"><div class="insight-icon" style="color:{T["green"]};">◈ Report ready</div>Click above to download your PDF.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="error-box"><strong>reportlab not found</strong><br>Add <code>reportlab</code> to requirements.txt and redeploy.</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <div><span class="footer-brand">DataLens</span>
        <span class="footer-hide-mobile">&nbsp;◈&nbsp; Smart Data Explorer</span></div>
    <div class="footer-right">
        <span>{filtered_df.shape[0]:,} rows · {filtered_df.shape[1]} cols</span>
        <span class="footer-hide-mobile">Groq · Llama 3.3 70B</span>
        <span class="footer-hide-mobile"><span class="kbd">T</span> theme</span>
        <span>{datetime.datetime.now().strftime('%d %b %Y')}</span>
    </div>
</div>
""", unsafe_allow_html=True)
