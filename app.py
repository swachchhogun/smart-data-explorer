import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json, requests, io, datetime

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
#  SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("annotations", []), ("type_overrides", {}),
             ("show_app", False), ("dark_mode", True),
             ("last_ai_text", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
#  THEME TOKENS
# ─────────────────────────────────────────────
if st.session_state.dark_mode:
    T = {
        "bg":           "#0a0a0f",
        "bg_grad":      "radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,90,50,0.07) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(80,180,255,0.05) 0%, transparent 60%), #0a0a0f",
        "sidebar":      "#0d0d16",
        "sidebar_bdr":  "rgba(255,255,255,0.06)",
        "card":         "#0f0f18",
        "card2":        "#12101f",
        "text":         "#e8e4dc",
        "text_head":    "#f0ece4",
        "text_muted":   "rgba(232,228,220,0.4)",
        "text_dim":     "rgba(232,228,220,0.3)",
        "text_faint":   "rgba(232,228,220,0.2)",
        "accent":       "#ff5a32",
        "accent_bg":    "rgba(255,90,50,0.08)",
        "accent_bdr":   "rgba(255,90,50,0.3)",
        "accent_glow":  "rgba(255,90,50,0.2)",
        "blue":         "#50b4ff",
        "green":        "#a8e063",
        "divider":      "rgba(255,255,255,0.07)",
        "divider_faint":"rgba(255,255,255,0.04)",
        "input_bg":     "#0f0f18",
        "input_bdr":    "rgba(255,255,255,0.1)",
        "plot_bg":      "#0d0d16",
        "hover_bg":     "rgba(255,255,255,0.02)",
        "grid":         "rgba(255,255,255,0.04)",
        "line":         "rgba(255,255,255,0.07)",
        "tick":         "rgba(232,228,220,0.35)",
        "toggle_icon":  "🌙",
        "toggle_label": "Night",
    }
else:
    T = {
        "bg":           "#f5f0e8",
        "bg_grad":      "radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,90,50,0.06) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(230,100,30,0.04) 0%, transparent 60%), #f5f0e8",
        "sidebar":      "#edeae2",
        "sidebar_bdr":  "rgba(0,0,0,0.07)",
        "card":         "#ffffff",
        "card2":        "#faf7f2",
        "text":         "#2a2118",
        "text_head":    "#1a1510",
        "text_muted":   "rgba(42,33,24,0.55)",
        "text_dim":     "rgba(42,33,24,0.4)",
        "text_faint":   "rgba(42,33,24,0.25)",
        "accent":       "#e04820",
        "accent_bg":    "rgba(224,72,32,0.08)",
        "accent_bdr":   "rgba(224,72,32,0.3)",
        "accent_glow":  "rgba(224,72,32,0.15)",
        "blue":         "#1a7fc4",
        "green":        "#3d8a1e",
        "divider":      "rgba(0,0,0,0.09)",
        "divider_faint":"rgba(0,0,0,0.05)",
        "input_bg":     "#ffffff",
        "input_bdr":    "rgba(0,0,0,0.15)",
        "plot_bg":      "#fdfaf6",
        "hover_bg":     "rgba(0,0,0,0.02)",
        "grid":         "rgba(0,0,0,0.05)",
        "line":         "rgba(0,0,0,0.08)",
        "tick":         "rgba(42,33,24,0.4)",
        "toggle_icon":  "☀️",
        "toggle_label": "Day",
    }

# ─────────────────────────────────────────────
#  INJECT CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
    background: {T['bg']} !important;
    color: {T['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
[data-testid="stAppViewContainer"] {{
    background: {T['bg_grad']} !important;
}}
[data-testid="stSidebar"] {{
    background: {T['sidebar']} !important;
    border-right: 1px solid {T['sidebar_bdr']} !important;
}}
[data-testid="stSidebar"] * {{ color: {T['text']} !important; }}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {{
    background: {T['input_bg']} !important;
    border-color: {T['input_bdr']} !important;
    color: {T['text']} !important;
}}

#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
.block-container {{ padding: 1.5rem 1.25rem 4rem !important; max-width: 1400px !important; }}
@media (min-width: 768px) {{ .block-container {{ padding: 2rem 2.5rem 4rem !important; }} }}

/* ── Welcome ── */
.welcome-wrap {{ min-height: 80vh; display: flex; flex-direction: column; justify-content: center; padding: 3rem 0 2rem; }}
.welcome-eyebrow {{ font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 5px; text-transform: uppercase; color: {T['accent']}; margin-bottom: 1rem; }}
.welcome-title {{ font-family: 'Syne', sans-serif; font-size: clamp(48px, 12vw, 96px); font-weight: 800; line-height: 0.88; letter-spacing: -4px; color: {T['text_head']}; margin: 0 0 1.5rem; }}
.welcome-title span {{ color: {T['accent']}; }}
.welcome-sub {{ font-family: 'DM Sans', sans-serif; font-size: 16px; color: {T['text_muted']}; font-weight: 300; max-width: 520px; line-height: 1.8; margin-bottom: 3rem; }}
.feature-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px; background: {T['divider']}; border: 1px solid {T['divider']}; margin-bottom: 3rem; max-width: 700px; overflow: hidden; }}
@media (min-width: 600px) {{ .feature-grid {{ grid-template-columns: repeat(4, 1fr); }} }}
.feature-card {{ background: {T['card']}; padding: 1.5rem 1.25rem; transition: background 0.2s; }}
.feature-card:hover {{ background: {T['card2']}; }}
.feature-icon {{ font-size: 20px; margin-bottom: 0.6rem; }}
.feature-title {{ font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700; color: {T['text_head']}; margin-bottom: 0.3rem; }}
.feature-desc {{ font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 1px; color: {T['text_dim']}; text-transform: uppercase; line-height: 1.6; }}

/* ── Hero ── */
.hero {{ padding: 1.5rem 0 1.25rem; border-bottom: 1px solid {T['divider']}; margin-bottom: 1.75rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }}
.hero-eyebrow {{ font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 4px; text-transform: uppercase; color: {T['accent']}; margin-bottom: 0.3rem; }}
.hero-title {{ font-family: 'Syne', sans-serif; font-size: clamp(28px, 6vw, 52px); font-weight: 800; line-height: 0.92; letter-spacing: -1.5px; color: {T['text_head']}; margin: 0; }}
.hero-title span {{ color: {T['accent']}; }}
.hero-file {{ font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 2px; color: {T['text_dim']}; margin-top: 0.4rem; text-transform: uppercase; }}

/* ── Metrics ── */
.metrics-row {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px; background: {T['divider']}; border: 1px solid {T['divider']}; margin-bottom: 2rem; overflow: hidden; }}
@media (min-width: 600px) {{ .metrics-row {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (min-width: 900px) {{ .metrics-row {{ grid-template-columns: repeat(5, 1fr); }} }}
.metric-card {{ background: {T['card']}; padding: 1.2rem 1.25rem; position: relative; overflow: hidden; transition: background 0.2s; }}
.metric-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, {T['accent']}, transparent); opacity: 0; transition: opacity 0.3s; }}
.metric-card:hover::before {{ opacity: 1; }}
.metric-label {{ font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; color: {T['text_dim']}; margin-bottom: 0.4rem; }}
.metric-value {{ font-family: 'Syne', sans-serif; font-size: clamp(22px, 4vw, 32px); font-weight: 800; color: {T['text_head']}; line-height: 1; letter-spacing: -1px; }}
.metric-value span {{ font-size: 10px; font-weight: 400; color: {T['text_dim']}; font-family: 'DM Mono', monospace; margin-left: 2px; }}
.metric-sub {{ font-family: 'DM Mono', monospace; font-size: 9px; color: {T['accent']}; margin-top: 3px; }}

/* ── Section label ── */
.section-label {{ font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 4px; text-transform: uppercase; color: {T['accent']}; margin-bottom: 1rem; display: flex; align-items: center; gap: 10px; }}
.section-label::after {{ content: ''; flex: 1; height: 1px; background: {T['divider']}; }}

/* ── Inputs ── */
.stSelectbox > div > div, .stMultiSelect > div > div {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_bdr']} !important;
    color: {T['text']} !important;
}}
.stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 1px {T['accent']} !important;
}}
.stSelectbox label, .stMultiSelect label, .stTextInput label, .stTextArea label {{
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    color: {T['text_dim']} !important;
}}
.stTextInput input {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_bdr']} !important;
    color: {T['text']} !important; font-size: 15px !important;
}}
.stTextInput input:focus {{ border-color: {T['accent']} !important; box-shadow: 0 0 0 1px {T['accent']} !important; }}
.stTextArea textarea {{
    background: {T['input_bg']} !important;
    border: 1px solid {T['input_bdr']} !important;
    color: {T['text']} !important; font-size: 13px !important;
}}

/* ── Buttons ── */
.stButton > button {{
    background: transparent !important;
    border: 1px solid {T['input_bdr']} !important;
    color: {T['text']} !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    padding: 0.7rem 1.4rem !important; transition: all 0.2s !important; width: 100% !important;
}}
.stButton > button:hover {{
    background: {T['accent']} !important;
    border-color: {T['accent']} !important; color: white !important;
}}
.stDownloadButton > button {{
    background: {T['accent_bg']} !important;
    border: 1px solid {T['accent_bdr']} !important;
    color: {T['accent']} !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
    padding: 0.7rem 1.4rem !important; width: 100% !important;
}}
.stDownloadButton > button:hover {{ background: {T['accent']} !important; color: white !important; }}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {T['card']} !important;
    border: 1px dashed {T['accent_bdr']} !important; padding: 1rem !important;
}}
[data-testid="stFileUploader"] * {{ color: {T['text']} !important; }}
[data-testid="stFileUploaderDropzone"] {{ background: transparent !important; padding: 1.5rem !important; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    border-bottom: 1px solid {T['divider']} !important;
    gap: 0 !important; overflow-x: auto !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; color: {T['text_dim']} !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
    border: none !important; padding: 0.75rem 1rem !important; white-space: nowrap !important;
}}
.stTabs [aria-selected="true"] {{ color: {T['accent']} !important; border-bottom: 2px solid {T['accent']} !important; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.25rem !important; }}

/* ── Cards ── */
.insight-card {{
    background: {T['card']}; border: 1px solid {T['divider']};
    border-left: 2px solid {T['accent']}; padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem; font-family: 'DM Sans', sans-serif;
    font-size: 14px; color: {T['text_muted']}; line-height: 1.7;
    box-shadow: {'none' if st.session_state.dark_mode else '0 1px 4px rgba(0,0,0,0.06)'};
}}
.insight-card strong {{ color: {T['text_head']}; font-weight: 500; }}
.insight-icon {{ font-family: 'DM Mono', monospace; font-size: 9px; color: {T['accent']}; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 0.4rem; }}

.ai-card {{
    background: {'linear-gradient(135deg, #0f0f18 0%, #12101f 100%)' if st.session_state.dark_mode else 'linear-gradient(135deg, #fff8f5 0%, #fff3ee 100%)'};
    border: 1px solid {T['accent_glow']}; padding: 1.5rem; margin-top: 1rem; position: relative;
    box-shadow: {'none' if st.session_state.dark_mode else '0 2px 12px rgba(224,72,32,0.08)'};
}}
.ai-card::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, {T['accent']}, transparent 60%); }}
.ai-card-label {{ font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 3px; text-transform: uppercase; color: {T['accent']}; margin-bottom: 1rem; }}
.ai-card-text {{ font-family: 'DM Sans', sans-serif; font-size: 14px; color: {T['text_muted']}; line-height: 1.8; white-space: pre-wrap; }}

/* ── Annotations ── */
.annotation-panel {{ background: {T['card']}; border: 1px solid {T['divider']}; padding: 1.25rem; margin-top: 1rem; }}
.annotation-item {{ border-bottom: 1px solid {T['divider_faint']}; padding: 0.75rem 0; font-family: 'DM Sans', sans-serif; font-size: 13px; color: {T['text_muted']}; line-height: 1.6; }}
.annotation-item:last-child {{ border-bottom: none; }}
.annotation-tag {{ font-family: 'DM Mono', monospace; font-size: 9px; color: {T['accent']}; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 3px; }}

/* ── Quality ── */
.quality-bar-wrap {{ background: {T['divider']}; height: 6px; border-radius: 3px; margin-top: 4px; overflow: hidden; }}
.quality-bar {{ height: 100%; border-radius: 3px; }}
.quality-row {{ display: flex; justify-content: space-between; align-items: flex-start; padding: 10px 0; border-bottom: 1px solid {T['divider_faint']}; gap: 8px; }}
.quality-col-name {{ font-family: 'DM Sans', sans-serif; font-size: 13px; color: {T['text_head']}; }}
.quality-col-type {{ font-family: 'DM Mono', monospace; font-size: 9px; color: {T['accent']}; background: {T['accent_bg']}; padding: 2px 7px; border-radius: 2px; white-space: nowrap; flex-shrink: 0; }}
.quality-col-stats {{ font-family: 'DM Mono', monospace; font-size: 10px; color: {T['text_dim']}; text-align: right; min-width: 80px; flex-shrink: 0; }}

/* ── Badges ── */
.clean-badge {{ display: inline-block; background: {'rgba(168,224,99,0.1)' if st.session_state.dark_mode else 'rgba(61,138,30,0.08)'}; border: 1px solid {'rgba(168,224,99,0.25)' if st.session_state.dark_mode else 'rgba(61,138,30,0.25)'}; color: {T['green']}; font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 1px; text-transform: uppercase; padding: 3px 8px; margin: 3px; }}
.error-box {{ background: {T['accent_bg']}; border: 1px solid {T['accent_bdr']}; padding: 1.2rem 1.5rem; font-family: 'DM Sans', sans-serif; font-size: 14px; color: {T['text_muted']}; line-height: 1.7; margin: 1rem 0; }}
.error-box strong {{ color: {T['accent']}; }}

/* ── Tables ── */
.table-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
.stats-table {{ width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace; font-size: 11px; min-width: 600px; }}
.stats-table th {{ background: {T['accent_bg']}; color: {T['accent']}; letter-spacing: 2px; text-transform: uppercase; padding: 10px 12px; text-align: left; border-bottom: 1px solid {T['divider']}; font-size: 9px; white-space: nowrap; }}
.stats-table td {{ padding: 8px 12px; border-bottom: 1px solid {T['divider_faint']}; color: {T['text_muted']}; white-space: nowrap; }}
.stats-table tr:hover td {{ background: {T['hover_bg']}; color: {T['text']}; }}
.stats-table .col-name {{ color: {T['text_head']}; font-weight: 500; }}
.type-table {{ width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace; font-size: 11px; }}
.type-table th {{ background: {T['accent_bg']}; color: {T['accent']}; letter-spacing: 2px; text-transform: uppercase; padding: 10px 12px; text-align: left; border-bottom: 1px solid {T['divider']}; font-size: 9px; }}
.type-table td {{ padding: 6px 12px; border-bottom: 1px solid {T['divider_faint']}; color: {T['text_muted']}; vertical-align: middle; }}
.type-table .col-name {{ color: {T['text_head']}; }}
.type-pill {{ display: inline-block; background: {'rgba(80,180,255,0.1)' if st.session_state.dark_mode else 'rgba(26,127,196,0.08)'}; border: 1px solid {'rgba(80,180,255,0.2)' if st.session_state.dark_mode else 'rgba(26,127,196,0.2)'}; color: {T['blue']}; font-family: 'DM Mono', monospace; font-size: 9px; padding: 2px 8px; border-radius: 2px; }}

/* ── Sidebar brand ── */
.sidebar-brand {{ font-family: 'Syne', sans-serif; font-size: 22px; font-weight: 800; color: {T['text_head']}; letter-spacing: -0.5px; padding: 1.5rem 0 0.2rem; }}
.sidebar-brand span {{ color: {T['accent']}; }}
.sidebar-tagline {{ font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 3px; color: {T['text_faint']}; text-transform: uppercase; margin-bottom: 1.5rem; }}

/* ── Theme toggle button ── */
.theme-btn {{ display: inline-flex; align-items: center; gap: 6px; background: {T['card']}; border: 1px solid {T['divider']}; color: {T['text_muted']}; font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; padding: 6px 12px; cursor: pointer; transition: all 0.2s; border-radius: 2px; }}

hr {{ border-color: {T['divider']} !important; margin: 1.5rem 0 !important; }}
.stAlert {{ background: {T['accent_bg']} !important; border: 1px solid {T['accent_bdr']} !important; color: {T['text']} !important; }}
.stToggle label {{ font-family: 'DM Mono', monospace !important; font-size: 10px !important; text-transform: uppercase !important; color: {T['text_dim']} !important; }}

/* ── Floating theme toggle ── */
.theme-fab {{
    position: fixed;
    top: 14px;
    right: 18px;
    z-index: 9999;
    background: {T['card']};
    border: 1px solid {T['divider']};
    color: {T['text_muted']};
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 1.5px;
    padding: 7px 14px 7px 10px;
    cursor: pointer;
    border-radius: 2px;
    box-shadow: {'0 2px 16px rgba(0,0,0,0.4)' if st.session_state.dark_mode else '0 2px 16px rgba(0,0,0,0.12)'};
    display: inline-flex;
    align-items: center;
    gap: 7px;
    transition: all 0.15s;
    text-decoration: none;
    user-select: none;
}}
.theme-fab:hover {{
    background: {T['accent']};
    border-color: {T['accent']};
    color: white;
    box-shadow: 0 4px 20px {T['accent_glow']};
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME
# ─────────────────────────────────────────────
if st.session_state.dark_mode:
    COLORS = ["#ff5a32","#50b4ff","#a8e063","#f7c948","#c678dd","#56b6c2","#e06c75","#d19a66"]
else:
    COLORS = ["#e04820","#1a7fc4","#3d8a1e","#c47d00","#8b44b8","#1a8a7c","#b83248","#a05c00"]

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["plot_bg"],
        font=dict(family="DM Sans", color=T["text"], size=11),
        title_font=dict(family="Syne", size=15, color=T["text_head"]),
        colorway=COLORS,
        xaxis=dict(
            gridcolor=T["grid"], linecolor=T["line"],
            tickfont=dict(family="DM Mono", size=9, color=T["tick"]),
            title_font=dict(family="DM Mono", size=9, color=T["tick"]),
        ),
        yaxis=dict(
            gridcolor=T["grid"], linecolor=T["line"],
            tickfont=dict(family="DM Mono", size=9, color=T["tick"]),
            title_font=dict(family="DM Mono", size=9, color=T["tick"]),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Mono", size=9, color=T["tick"]),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        margin=dict(l=8, r=8, t=44, b=8),
        hoverlabel=dict(
            bgcolor=T["card"],
            font_family="DM Mono", font_size=11,
            bordercolor=T["accent_glow"],
        ),
    )
    return fig

def add_annotations_to_fig(fig, annotations):
    for ann in annotations:
        fig.add_annotation(
            x=ann.get("x", 0.5), y=ann.get("y", 0.5),
            xref=ann.get("xref","paper"), yref=ann.get("yref","paper"),
            text=f"◈ {ann['text']}",
            showarrow=ann.get("arrow", True),
            arrowhead=2, arrowcolor=T["accent"], arrowwidth=1.5,
            font=dict(family="DM Sans", size=11, color=T["text_head"]),
            bgcolor=T["card"], bordercolor=T["accent"],
            borderwidth=1, borderpad=6,
        )
    return fig

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def safe_read_csv(file):
    for enc in ["utf-8","latin-1","utf-16","cp1252"]:
        for sep in [",",";","\t"]:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=enc, sep=sep)
                if df.shape[1] > 1 or sep == ",":
                    return df, None
            except Exception:
                continue
    return None, "Could not read this file. Make sure it's a valid CSV."

def smart_clean(df):
    report, cleaned = [], df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]
    if cleaned.empty:
        return cleaned, ["File is empty."]
    for col in cleaned.select_dtypes(include="object").columns:
        try:
            p = pd.to_datetime(cleaned[col], infer_datetime_format=True, errors="coerce")
            if p.notna().mean() > 0.7:
                cleaned[col] = p
                report.append(f"Parsed '{col}' as datetime")
        except Exception: pass
    for col in cleaned.select_dtypes(include="object").columns:
        try: cleaned[col] = cleaned[col].str.strip()
        except Exception: pass
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
        report.append(f"Removed {before-len(cleaned)} empty rows")
    n_d = int(cleaned.duplicated().sum())
    if n_d > 0:
        cleaned = cleaned.drop_duplicates()
        report.append(f"Removed {n_d} duplicate rows")
    return cleaned, report

TYPE_OPTIONS = ["Auto (keep as-is)","Text / String","Integer","Float / Decimal","Date / Time","Boolean"]

def apply_type_overrides(df, overrides):
    out = df.copy()
    for col, t in overrides.items():
        if col not in out.columns: continue
        try:
            if t == "Text / String":       out[col] = out[col].astype(str)
            elif t == "Integer":           out[col] = pd.to_numeric(out[col], errors="coerce").astype("Int64")
            elif t == "Float / Decimal":   out[col] = pd.to_numeric(out[col], errors="coerce")
            elif t == "Date / Time":       out[col] = pd.to_datetime(out[col], errors="coerce")
            elif t == "Boolean":           out[col] = out[col].map(lambda x: True if str(x).lower() in ("1","true","yes","y") else False)
        except Exception: pass
    return out

@st.cache_data(show_spinner=False, ttl=300)
def get_ai_insights(data_json: str, question: str = "") -> str:
    prompt = f"""You are a data analyst. Analyze this dataset and provide clear insights.
Dataset: {data_json}
{"Question: " + question if question else "Give 4-5 key insights: patterns, outliers, distributions, findings. Be specific with numbers."}
Plain language, numbered points, concise."""
    key = st.secrets.get("GROQ_API_KEY","")
    if not key:
        return ("⚠️ No Groq API key found.\n\nSetup (free, 2 mins):\n"
                "1. Sign up at console.groq.com\n2. Create API key\n"
                "3. Streamlit Cloud → Settings → Secrets:\n   GROQ_API_KEY = \"your-key\"")
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model":"llama3-8b-8192","messages":[{"role":"user","content":prompt}],
                  "max_tokens":800,"temperature":0.4},
            timeout=20)
        d = r.json()
        if "choices" in d: return d["choices"][0]["message"]["content"]
        return f"Groq error: {d.get('error',{}).get('message', str(d))}"
    except requests.exceptions.Timeout: return "Request timed out. Try again."
    except Exception as e: return f"Could not reach Groq: {e}"

def build_summary(df):
    nd = df.select_dtypes(include="number")
    cd = df.select_dtypes(include="object")
    return json.dumps({
        "shape": list(df.shape), "columns": list(df.columns),
        "numeric_stats": nd.describe().round(2).to_dict() if len(nd.columns) > 0 else {},
        "categorical_top": {c: df[c].value_counts().head(3).to_dict() for c in cd.columns[:4]},
        "missing": df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
    }, default=str)

def generate_pdf_report(df, filename, ai_text, clean_report):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                        Table, TableStyle, HRFlowable, PageBreak)
        from reportlab.lib.styles import ParagraphStyle
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=18*mm, bottomMargin=18*mm)
        BG=colors.HexColor("#0a0a0f"); CARD=colors.HexColor("#0f0f18")
        ACCENT=colors.HexColor("#ff5a32"); TEXT=colors.HexColor("#f0ece4")
        MUTED=colors.HexColor("#6b6760"); LINE=colors.HexColor("#1e1e2a")
        BLUE=colors.HexColor("#50b4ff")
        def sty(name, **kw):
            base = dict(fontName="Helvetica", fontSize=10, textColor=TEXT, leading=14, spaceAfter=4)
            base.update(kw); return ParagraphStyle(name, **base)
        S_EY = sty("ey", fontSize=7, textColor=ACCENT, fontName="Helvetica-Bold", leading=10)
        S_TI = sty("ti", fontSize=28, textColor=TEXT, fontName="Helvetica-Bold", leading=30)
        S_MO = sty("mo", fontSize=8, textColor=BLUE, fontName="Courier", leading=12)
        S_SE = sty("se", fontSize=7, textColor=ACCENT, fontName="Helvetica-Bold", leading=10, spaceAfter=6)
        S_AI = sty("ai", fontSize=9, textColor=colors.HexColor("#c8c4bc"), leading=15)
        def HR(): return HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=10, spaceBefore=10)
        def SP(h=6): return Spacer(1, h)
        tbl_style = TableStyle([
            ("BACKGROUND",(0,0),(-1,0),ACCENT), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,1),(-1,-1),CARD), ("TEXTCOLOR",(0,1),(-1,-1),TEXT),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[CARD, colors.HexColor("#111120")]),
            ("GRID",(0,0),(-1,-1),0.3,LINE),
            ("LEFTPADDING",(0,0),(-1,-1),7), ("RIGHTPADDING",(0,0),(-1,-1),7),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ])
        story = [SP(20), Paragraph("◈ SMART DATA EXPLORER", S_EY), SP(4),
                 Paragraph("DataLens", S_TI), Paragraph("Analysis Report",
                 sty("sub", fontSize=13, textColor=MUTED, leading=16)), SP(10), HR(),
                 Paragraph(f"File: {filename}", S_MO),
                 Paragraph(f"Generated: {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}", S_MO),
                 Paragraph(f"Rows: {df.shape[0]:,}   Columns: {df.shape[1]}", S_MO), HR(), SP(10)]
        nc = df.select_dtypes(include="number").columns.tolist()
        cc = df.select_dtypes(include="object").columns.tolist()
        miss = int(df.isnull().sum().sum())
        comp = round((1 - miss / max(df.size,1)) * 100, 1)
        story.append(Paragraph("DATASET OVERVIEW", S_SE))
        ov = Table([["Metric","Value"],["Total rows",f"{df.shape[0]:,}"],["Total columns",str(df.shape[1])],
                    ["Numeric cols",str(len(nc))],["Categorical cols",str(len(cc))],
                    ["Missing values",f"{miss:,}"],["Completeness",f"{comp}%"],
                    ["Duplicate rows",str(int(df.duplicated().sum()))]], colWidths=[80*mm,80*mm])
        ov.setStyle(tbl_style)
        story += [ov, SP(16)]
        story.append(Paragraph("COLUMNS", S_SE))
        cd2 = [["Column Name","Type","Nulls","Unique"]]
        for col in df.columns:
            cd2.append([col[:35], str(df[col].dtype), str(int(df[col].isnull().sum())), str(df[col].nunique())])
        ct = Table(cd2, colWidths=[75*mm,35*mm,25*mm,25*mm])
        ct.setStyle(tbl_style)
        story += [ct, SP(16)]
        if nc:
            story += [PageBreak(), Paragraph("NUMERIC STATISTICS", S_SE)]
            stats = df[nc].describe().T.round(3)
            stats["median"] = df[nc].median().round(3)
            stats["skew"] = df[nc].skew().round(3)
            keep = ["count","mean","median","std","min","max","skew"]
            stats = stats[[c for c in keep if c in stats.columns]]
            hdr = ["Column"] + list(stats.columns)
            sd = [hdr] + [[str(rn)[:20]] + [f"{v:,.3f}" if isinstance(v,float) else str(int(v)) for v in row] for rn, row in stats.iterrows()]
            st2 = Table(sd, colWidths=[50*mm]+[18*mm]*(len(hdr)-1))
            st2.setStyle(tbl_style)
            story += [st2, SP(16)]
        if clean_report:
            story += [HR(), Paragraph("CLEANING APPLIED", S_SE)]
            for note in clean_report:
                story.append(Paragraph(f"✓  {note}", S_AI))
        story += [PageBreak(), Paragraph("AI INSIGHTS", S_SE),
                  Paragraph("Powered by Llama 3 via Groq (free)", S_MO), SP(8)]
        for line in ai_text.split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, S_AI)); story.append(SP(3))
        story += [SP(20), HR(),
                  Paragraph("Generated by DataLens · Smart Data Explorer", S_MO),
                  Paragraph(f"Report date: {datetime.datetime.now().strftime('%d %B %Y')}", S_MO)]
        doc.build(story)
        buf.seek(0); return buf.read()
    except ImportError: return None
    except Exception as e:
        st.error(f"PDF error: {e}"); return None

def col_health(s):
    null_pct = s.isnull().mean() * 100
    unique_pct = s.nunique() / max(len(s),1) * 100
    score = max(0, 100 - null_pct - (20 if unique_pct > 95 and pd.api.types.is_object_dtype(s) else 0))
    return {"null_pct": round(null_pct,1), "unique": s.nunique(), "score": round(score)}

def hcolor(score):
    if score >= 80: return "#a8e063" if st.session_state.dark_mode else "#3d8a1e"
    if score >= 50: return "#f7c948" if st.session_state.dark_mode else "#c47d00"
    return T["accent"]

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="sidebar-brand">Data<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-tagline">◈ Smart Explorer</div>', unsafe_allow_html=True)

    if st.session_state.get("working_df") is not None:
        wdf = st.session_state.working_df
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
        st.download_button("↓ Export filtered CSV",
                           data=fdf.to_csv(index=False).encode("utf-8"),
                           file_name="datalens_export.csv", mime="text/csv",
                           use_container_width=True)
        if st.button("← Start over", use_container_width=True):
            for k in ["working_df","filtered_df","raw_df","cleaned_df","clean_report",
                      "show_app","annotations","type_overrides"]:
                st.session_state.pop(k, None)
            st.rerun()
    else:
        st.caption("Upload a CSV on the main page to start.")

# ─────────────────────────────────────────────
#  THEME TOGGLE  (top of every page, right-aligned)
# ─────────────────────────────────────────────
icon  = "☀️  Day" if st.session_state.dark_mode else "🌙  Night"
_sp, _tb = st.columns([10, 1])
with _tb:
    if st.button(icon, key="theme_fab"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ─────────────────────────────────────────────
#  WELCOME SCREEN
# ─────────────────────────────────────────────
if not st.session_state.show_app:
    st.markdown(f"""
    <div class="welcome-wrap">
        <div class="welcome-eyebrow">◈ Smart Data Explorer</div>
        <div class="welcome-title">Data<span>Lens</span></div>
        <div class="welcome-sub">
            Upload any CSV and get instant charts, statistics, AI-powered insights,
            and a beautiful PDF report — all in one place, completely free.
        </div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Auto Clean</div>
                <div class="feature-desc">Nulls filled · Dupes removed · Types fixed</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">◈</div>
                <div class="feature-title">6 Chart Types</div>
                <div class="feature-desc">Histogram · Scatter · Correlation · Trend</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Free AI</div>
                <div class="feature-desc">Llama 3 via Groq · No cost · Instant</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">PDF Report</div>
                <div class="feature-desc">One-click · Stats · AI · Export</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("◈ Get started — Upload a CSV", use_container_width=True):
            st.session_state.show_app = True
            st.rerun()
    st.stop()

# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Your Data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown(f"""
    <div style="border:1px dashed {T['accent_bdr']};background:{T['card']};padding:2.5rem 1.5rem;text-align:center;margin:1rem 0;">
        <div style="font-family:Syne,sans-serif;font-size:22px;font-weight:700;color:{T['text_head']};margin-bottom:0.4rem;">Tap above to upload a CSV</div>
        <div style="font-family:DM Mono,monospace;font-size:10px;letter-spacing:2px;color:{T['text_faint']};text-transform:uppercase;">Any CSV · Auto-cleaned · Free AI · PDF report</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

with st.spinner("Reading file..."):
    raw_df, load_err = safe_read_csv(uploaded_file)

if load_err or raw_df is None:
    st.markdown(f'<div class="error-box"><strong>Could not load file</strong><br>{load_err}</div>', unsafe_allow_html=True)
    st.stop()
if raw_df.empty:
    st.markdown(f'<div class="error-box"><strong>Empty file</strong><br>The CSV has no data.</div>', unsafe_allow_html=True)
    st.stop()

st.session_state.raw_df = raw_df

try:
    cleaned_df, clean_report = smart_clean(raw_df)
except Exception as e:
    cleaned_df, clean_report = raw_df.copy(), [f"Cleaning failed: {e}"]

st.session_state.cleaned_df = cleaned_df
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
    filtered_df = base_df.copy()
    st.session_state.filtered_df = filtered_df

numeric_cols = base_df.select_dtypes(include="number").columns.tolist()
cat_cols     = base_df.select_dtypes(include="object").columns.tolist()

if clean_report and use_cleaned:
    with st.expander("✦ Cleaning applied"):
        for n in clean_report:
            st.markdown(f'<span class="clean-badge">✓ {n}</span>', unsafe_allow_html=True)

fn = uploaded_file.name if uploaded_file else "dataset.csv"
st.markdown(f"""
<div class="hero">
    <div class="hero-left">
        <div class="hero-eyebrow">◈ Smart Data Explorer</div>
        <div class="hero-title">Data<span>Lens</span></div>
        <div class="hero-file">◈ {fn} · {filtered_df.shape[0]:,} rows · {filtered_df.shape[1]} cols</div>
    </div>
</div>
""", unsafe_allow_html=True)

missing_count = int(filtered_df.isnull().sum().sum())
dupe_count    = int(filtered_df.duplicated().sum())
completeness  = round((1 - missing_count / max(filtered_df.size,1)) * 100, 1)

st.markdown(f"""
<div class="metrics-row">
  <div class="metric-card"><div class="metric-label">Rows</div>
    <div class="metric-value">{filtered_df.shape[0]:,}<span>r</span></div>
    <div class="metric-sub">of {base_df.shape[0]:,}</div></div>
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

st.markdown('<div class="section-label">Analysis Mode</div>', unsafe_allow_html=True)
analysis_type = st.selectbox("Mode",
    ["Dashboard Overview","Distribution Analysis","Category Comparison",
     "Correlation Analysis","Trend Over Time","Scatter Explorer"],
    label_visibility="collapsed")

tab_explore, tab_quality, tab_types, tab_stats, tab_ai, tab_report = st.tabs([
    "◈  Explore", "◈  Data Quality", "◈  Column Types",
    "◈  Statistics", "◈  AI Insights", "◈  PDF Report"
])

# ═══ EXPLORE ═══
with tab_explore:
    st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df.head(8), use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{analysis_type}</div>', unsafe_allow_html=True)

    with st.expander("◈ Chart Annotations", expanded=False):
        ann_text  = st.text_input("Annotation text", placeholder="e.g. Sharp spike in Q3", key="ann_text")
        c1,c2,c3 = st.columns(3)
        with c1: ann_x     = st.number_input("X (0–1)", 0.0, 1.0, 0.5, 0.05, key="ann_x")
        with c2: ann_y     = st.number_input("Y (0–1)", 0.0, 1.0, 0.9, 0.05, key="ann_y")
        with c3: ann_arrow = st.toggle("Arrow", value=True, key="ann_arrow")
        if st.button("◈ Add annotation", key="add_ann"):
            if ann_text.strip():
                st.session_state.annotations.append({
                    "text": ann_text.strip(), "x": ann_x, "y": ann_y,
                    "xref":"paper","yref":"paper","arrow": ann_arrow})
                st.success(f"Added: {ann_text.strip()}")
        if st.session_state.annotations:
            st.markdown('<div class="annotation-panel">', unsafe_allow_html=True)
            for i, ann in enumerate(st.session_state.annotations):
                st.markdown(f'<div class="annotation-item"><div class="annotation-tag">◈ Note {i+1}</div>{ann["text"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("✕ Clear all", key="clear_ann"):
                st.session_state.annotations = []
                st.rerun()

    anns = st.session_state.annotations
    accent = T["accent"]

    try:
        if analysis_type == "Dashboard Overview":
            if numeric_cols:
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
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)
            if cat_cols and numeric_cols:
                st.markdown("<hr>", unsafe_allow_html=True)
                cat = st.selectbox("Category column", cat_cols, key="dash_cat")
                num = st.selectbox("Numeric column", numeric_cols, key="dash_num2")
                agg = st.selectbox("Aggregation", ["Mean","Sum","Median","Count"], key="dash_agg")
                agg_fn = {"Mean":"mean","Sum":"sum","Median":"median","Count":"count"}[agg]
                grouped = filtered_df.groupby(cat)[num].agg(agg_fn).reset_index().sort_values(num, ascending=False).head(20)
                fig2 = px.bar(grouped, x=cat, y=num, title=f"{agg} of {num} by {cat}")
                fig2.update_traces(marker_color=accent, marker_line_width=0)
                st.plotly_chart(style_fig(add_annotations_to_fig(fig2, anns)), use_container_width=True)

        elif analysis_type == "Distribution Analysis":
            if not numeric_cols: st.warning("No numeric columns.")
            else:
                column   = st.selectbox("Numeric Column", numeric_cols, key="dist_col")
                color_by = st.selectbox("Color by (optional)", ["None"]+cat_cols, key="dist_color")
                ca = None if color_by == "None" else color_by
                fig = px.histogram(filtered_df, x=column, color=ca, nbins=30,
                                   title=f"Histogram · {column}", barmode="overlay", opacity=0.8)
                if not ca: fig.update_traces(marker_color=accent, marker_line_color="rgba(0,0,0,0.15)", marker_line_width=1)
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)
                fig2 = px.violin(filtered_df, y=column, color=ca, title=f"Violin · {column}", box=True)
                if not ca: fig2.update_traces(fillcolor=T["accent_glow"], line_color=accent)
                st.plotly_chart(style_fig(add_annotations_to_fig(fig2, anns)), use_container_width=True)

        elif analysis_type == "Category Comparison":
            if not cat_cols or not numeric_cols: st.warning("Need both categorical and numeric columns.")
            else:
                cat   = st.selectbox("Category", cat_cols, key="cat_cat")
                num   = st.selectbox("Numeric", numeric_cols, key="cat_num")
                agg   = st.selectbox("Aggregation", ["Mean","Sum","Median","Count"], key="cat_agg")
                chart = st.selectbox("Chart type", ["Bar","Treemap","Pie"], key="cat_chart")
                agg_fn = {"Mean":"mean","Sum":"sum","Median":"median","Count":"count"}[agg]
                grouped = filtered_df.groupby(cat)[num].agg(agg_fn).reset_index().sort_values(num, ascending=True)
                if chart == "Bar":
                    fig = px.bar(grouped, x=num, y=cat, orientation="h", title=f"{agg} of {num} by {cat}")
                    fig.update_traces(marker_color=accent, marker_line_width=0)
                elif chart == "Treemap":
                    fig = px.treemap(grouped, path=[cat], values=num, title=f"{agg} of {num} by {cat}",
                                     color=num, color_continuous_scale=[T["card"], accent])
                else:
                    fig = px.pie(grouped, names=cat, values=num, title=f"{agg} of {num} by {cat}",
                                 color_discrete_sequence=COLORS)
                    fig.update_traces(textfont=dict(family="DM Mono", size=10))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        elif analysis_type == "Correlation Analysis":
            if len(numeric_cols) < 2: st.warning("Need at least two numeric columns.")
            else:
                method = st.selectbox("Method", ["pearson","spearman","kendall"], key="corr_method")
                corr   = filtered_df[numeric_cols].corr(method=method)
                fig    = px.imshow(corr, text_auto=".2f", title=f"Correlation Matrix ({method.title()})",
                                   color_continuous_scale=[[0,T["blue"]],[0.5,T["card"]],[1,accent]],
                                   zmin=-1, zmax=1)
                fig.update_traces(textfont=dict(family="DM Mono", size=10, color=T["text_head"]))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)
                st.markdown('<div class="section-label">Top Pairs</div>', unsafe_allow_html=True)
                cp = corr.abs().unstack().sort_values(ascending=False)
                cp = cp[cp < 1].drop_duplicates().head(8)
                for (c1n,c2n), val in cp.items():
                    d   = "↑" if corr.loc[c1n,c2n] > 0 else "↓"
                    clr = T["green"] if corr.loc[c1n,c2n] > 0 else accent
                    st.markdown(f"""<div style="border-bottom:1px solid {T['divider_faint']};padding:8px 0;font-family:DM Mono,monospace;font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
                        <span><span style="color:{T['text_head']}">{c1n}</span> <span style="color:{T['text_dim']}">×</span> <span style="color:{T['text_head']}">{c2n}</span></span>
                        <span style="color:{clr}">{d} {val:.3f}</span></div>""", unsafe_allow_html=True)

        elif analysis_type == "Trend Over Time":
            date_col = st.selectbox("Time Column", list(filtered_df.columns), key="trend_date")
            if not numeric_cols: st.warning("No numeric columns.")
            else:
                num_col = st.selectbox("Value Column", numeric_cols, key="trend_val")
                smooth  = st.selectbox("Smoothing", ["None","7-period MA","30-period MA"], key="trend_smooth")
                plot_df = filtered_df[[date_col,num_col]].dropna().sort_values(date_col)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df[num_col], mode="lines",
                                          name="Raw", line=dict(color=T["accent_glow"], width=1)))
                if smooth != "None":
                    w = 7 if "7" in smooth else 30
                    plot_df = plot_df.copy()
                    plot_df["_ma"] = plot_df[num_col].rolling(w, min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df["_ma"], mode="lines",
                                              name=smooth, line=dict(color=accent, width=2.5)))
                fig.update_layout(title=f"{num_col} over Time")
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        elif analysis_type == "Scatter Explorer":
            if len(numeric_cols) < 2: st.warning("Need at least two numeric columns.")
            else:
                x_col     = st.selectbox("X Axis", numeric_cols, key="sc_x")
                y_col     = st.selectbox("Y Axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="sc_y")
                color_col = st.selectbox("Color by (optional)", ["None"]+cat_cols+numeric_cols, key="sc_col")
                size_col  = st.selectbox("Size by (optional)", ["None"]+numeric_cols, key="sc_sz")
                ca = None if color_col == "None" else color_col
                sa = None if size_col  == "None" else size_col
                fig = px.scatter(filtered_df, x=x_col, y=y_col, color=ca, size=sa,
                                 title=f"{y_col} vs {x_col}", opacity=0.75,
                                 trendline="ols" if ca is None else None,
                                 color_discrete_sequence=COLORS,
                                 color_continuous_scale=[[0,T["card"]],[1,accent]])
                if ca is None and sa is None:
                    fig.update_traces(marker=dict(color=accent, size=6, line=dict(color="rgba(0,0,0,0.15)", width=1)))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Chart error</strong><br>Try a different column or mode.<br><small style="opacity:0.5">{e}</small></div>', unsafe_allow_html=True)

# ═══ DATA QUALITY ═══
with tab_quality:
    st.markdown('<div class="section-label">Before vs After Cleaning</div>', unsafe_allow_html=True)
    raw_nulls = int(raw_df.isnull().sum().sum())
    raw_dupes = int(raw_df.duplicated().sum())
    cn   = int(cleaned_df.isnull().sum().sum())
    cd_d = int(cleaned_df.duplicated().sum())
    st.markdown(f"""
    <div class="metrics-row" style="grid-template-columns:repeat(2,1fr);margin-bottom:1.5rem;">
        <div class="metric-card"><div class="metric-label">Nulls — raw</div>
            <div class="metric-value" style="color:{T['accent']}">{raw_nulls:,}</div></div>
        <div class="metric-card"><div class="metric-label">Nulls — cleaned</div>
            <div class="metric-value" style="color:{T['green']}">{cn:,}</div></div>
        <div class="metric-card"><div class="metric-label">Dupes — raw</div>
            <div class="metric-value" style="color:{T['accent']}">{raw_dupes:,}</div></div>
        <div class="metric-card"><div class="metric-label">Dupes — cleaned</div>
            <div class="metric-value" style="color:{T['green']}">{cd_d:,}</div></div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Column Health</div>', unsafe_allow_html=True)
    for col in base_df.columns:
        h  = col_health(base_df[col])
        bc = hcolor(h["score"])
        st.markdown(f"""
        <div class="quality-row">
            <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">
                    <span class="quality-col-name">{col}</span>
                    <span class="quality-col-type">{str(base_df[col].dtype)}</span>
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
        st.info("No numeric columns.")
    else:
        try:
            oc = st.selectbox("Column to check", numeric_cols, key="out_col")
            s  = filtered_df[oc].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1; lo, hi = q1-1.5*iqr, q3+1.5*iqr
            outliers = filtered_df[(filtered_df[oc] < lo) | (filtered_df[oc] > hi)]
            pct = round(len(outliers)/max(len(filtered_df),1)*100, 1)
            st.markdown(f"""<div class="insight-card">
                <div class="insight-icon">◈ IQR Method · {oc}</div>
                Normal range: <strong>{lo:,.2f}</strong> to <strong>{hi:,.2f}</strong><br>
                <strong>{len(outliers):,} rows ({pct}%)</strong> outside this range.
                {"Significant — worth investigating." if pct > 5 else "Small proportion — likely fine."}
            </div>""", unsafe_allow_html=True)
            fig = px.box(filtered_df, y=oc, title=f"Outliers · {oc}", points="outliers")
            fig.update_traces(marker_color=accent, line_color=T["blue"],
                              marker=dict(color=accent, size=5, opacity=0.7))
            st.plotly_chart(style_fig(fig), use_container_width=True)
            if len(outliers) > 0:
                with st.expander(f"View outlier rows ({min(len(outliers),50)} shown)"):
                    st.dataframe(outliers.head(50), use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Outlier error: {e}")

# ═══ COLUMN TYPES ═══
with tab_types:
    st.markdown('<div class="section-label">Column Type Editor</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.7;">Override auto-detected column types. Changes apply immediately to all charts and stats.</div>', unsafe_allow_html=True)
    hdr2 = ["Column","Current Type","Override To"]
    st.markdown(f"""<div class="table-wrap"><table class="type-table">
        <thead><tr>{"".join(f"<th>{h}</th>" for h in hdr2)}</tr></thead><tbody>""", unsafe_allow_html=True)
    for col in base_df.columns:
        st.markdown(f"""<tr>
            <td class="col-name">{col}</td>
            <td><span class="type-pill">{str(base_df[col].dtype)}</span></td>
            <td style="color:{T['text_dim']}">use selector below</td>
        </tr>""", unsafe_allow_html=True)
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
                st.session_state.type_overrides[sel_col] = sel_type
                st.success(f"'{sel_col}' → {sel_type}")
            else:
                st.session_state.type_overrides.pop(sel_col, None)
                st.info(f"Override removed for '{sel_col}'.")
    with col2:
        if st.button("✕ Clear all overrides", key="clear_types"):
            st.session_state.type_overrides = {}
            st.success("All overrides cleared.")
    if st.session_state.type_overrides:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Active Overrides</div>', unsafe_allow_html=True)
        for col, t in st.session_state.type_overrides.items():
            st.markdown(f'<span class="clean-badge">{col} → {t}</span>', unsafe_allow_html=True)

# ═══ STATISTICS ═══
with tab_stats:
    if numeric_cols:
        st.markdown('<div class="section-label">Numeric Summary</div>', unsafe_allow_html=True)
        try:
            stats = filtered_df[numeric_cols].describe().T
            stats["median"] = filtered_df[numeric_cols].median()
            stats["skew"]   = filtered_df[numeric_cols].skew().round(3)
            stats["nulls"]  = filtered_df[numeric_cols].isnull().sum()
            dc2 = ["count","mean","median","std","min","25%","75%","max","skew","nulls"]
            stats = stats[[c for c in dc2 if c in stats.columns]].round(3)
            rows_html = ""
            for cn2, row in stats.iterrows():
                cells = "".join(f"<td>{v:,.3f}</td>" if isinstance(v,float) else f"<td>{int(v)}</td>" for v in row.values)
                rows_html += f"<tr><td class='col-name'>{cn2}</td>{cells}</tr>"
            headers = "".join(f"<th>{c}</th>" for c in ["Column"]+list(stats.columns))
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
            fig = px.bar(vc.head(15), x="count", y=cat_sel, orientation="h",
                         title=f"Value Counts · {cat_sel}")
            fig.update_traces(marker_color=accent, marker_line_width=0)
            st.plotly_chart(style_fig(fig), use_container_width=True)
        except Exception as e:
            st.warning(f"Categorical error: {e}")

# ═══ AI INSIGHTS ═══
with tab_ai:
    st.markdown('<div class="section-label">AI-Powered Analysis</div>', unsafe_allow_html=True)
    has_key = bool(st.secrets.get("GROQ_API_KEY",""))
    if not has_key:
        st.markdown(f"""<div class="error-box">
            <strong>Free AI setup — 2 mins, no card needed:</strong><br><br>
            1. Go to <strong>console.groq.com</strong> → sign up free<br>
            2. Click API Keys → Create key<br>
            3. Streamlit Cloud → Settings → Secrets:<br><br>
            <code style="background:{T['accent_bg']};padding:4px 10px;font-family:DM Mono,monospace;">GROQ_API_KEY = "gsk_xxxx"</code>
        </div>""", unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.25rem;line-height:1.7;">Ask anything about your data, or get an auto-analysis below.</div>', unsafe_allow_html=True)
    question = st.text_input("Ask a question", placeholder="e.g. What are the main trends? Any outliers?", key="ai_q")
    run_ai = st.button("◈ Analyse with AI", use_container_width=True)
    data_json = build_summary(filtered_df)
    if run_ai or question:
        with st.spinner("Thinking..."):
            result = get_ai_insights(data_json, question)
        st.session_state.last_ai_text = result
        st.markdown(f"""<div class="ai-card">
            <div class="ai-card-label">◈ AI Answer · Llama 3 (free via Groq)</div>
            <div class="ai-card-text">{result}</div>
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Generating auto insights..."):
            auto = get_ai_insights(data_json)
        st.session_state.last_ai_text = auto
        st.markdown(f"""<div class="ai-card">
            <div class="ai-card-label">◈ Auto Insights · Llama 3 (free via Groq)</div>
            <div class="ai-card-text">{auto}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Statistical Quick Insights</div>', unsafe_allow_html=True)
    try:
        ndf = filtered_df.select_dtypes(include="number")
        if len(ndf.columns) > 0:
            hmc = ndf.mean().idxmax(); hvc = ndf.var().idxmax()
            st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Highest Average</div>
                <strong>{hmc}</strong> has the highest mean — <strong>{ndf[hmc].mean():,.2f}</strong>.
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Most Variable</div>
                <strong>{hvc}</strong> has the greatest spread — variance <strong>{ndf[hvc].var():,.2f}</strong>.
            </div>""", unsafe_allow_html=True)
            if len(ndf.columns) > 1:
                corr = ndf.corr().abs(); cu = corr.unstack(); cu = cu[cu < 1].drop_duplicates()
                if not cu.empty:
                    strongest = cu.idxmax(); rc = ndf.corr().loc[strongest[0], strongest[1]]
                    d = "positively" if rc > 0 else "negatively"
                    st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Strongest Correlation</div>
                        <strong>{strongest[0]}</strong> and <strong>{strongest[1]}</strong> are {d} correlated (r = <strong>{cu.max():.3f}</strong>).
                        {"Strong — worth investigating." if cu.max() > 0.7 else "Moderate."}
                    </div>""", unsafe_allow_html=True)
            skews = ndf.skew().abs().sort_values(ascending=False)
            if len(skews) > 0 and skews.iloc[0] > 1:
                st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Skewed Distribution</div>
                    <strong>{skews.index[0]}</strong> is heavily skewed ({skews.iloc[0]:.2f}).
                    Consider log-transforming before modelling.
                </div>""", unsafe_allow_html=True)
        if missing_count > 0:
            pct = round(missing_count/max(filtered_df.size,1)*100,1)
            st.markdown(f"""<div class="insight-card"><div class="insight-icon">◈ Data Quality</div>
                <strong>{missing_count}</strong> missing values ({pct}% of cells).
                {"Significant — consider further imputation." if pct > 5 else "Manageable."}
            </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Quick insights error: {e}")
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("↓ Export filtered data",
                       data=filtered_df.to_csv(index=False).encode("utf-8"),
                       file_name="datalens_export.csv", mime="text/csv")

# ═══ PDF REPORT ═══
with tab_report:
    st.markdown('<div class="section-label">Download PDF Report</div>', unsafe_allow_html=True)
    st.markdown(f"""<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T['text_muted']};margin-bottom:1.5rem;line-height:1.8;">
    Generate a professionally formatted PDF containing your dataset overview, column details,
    numeric statistics, cleaning summary, and AI insights.
    </div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="insight-card">
        <div class="insight-icon">◈ Report includes</div>
        Cover page · Dataset overview · Column health · Numeric statistics · Cleaning report · AI insights
    </div>""", unsafe_allow_html=True)
    ai_text_for_pdf = st.session_state.get("last_ai_text", "Run AI analysis in the AI Insights tab first to include it in your report.")
    if st.button("◈ Generate PDF Report", use_container_width=True, key="gen_pdf"):
        with st.spinner("Building your report..."):
            pdf_bytes = generate_pdf_report(filtered_df, fn, ai_text_for_pdf,
                                            clean_report if use_cleaned else [])
        if pdf_bytes:
            st.download_button("↓ Download Report PDF", data=pdf_bytes,
                               file_name=f"datalens_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                               mime="application/pdf", use_container_width=True)
            st.markdown(f"""<div class="insight-card" style="border-left-color:{T['green']};">
                <div class="insight-icon" style="color:{T['green']};">◈ Report ready</div>
                Your PDF has been generated. Click the button above to download it.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="error-box">
                <strong>PDF generation requires reportlab</strong><br>
                Add <code>reportlab</code> to your requirements.txt and redeploy.
            </div>""", unsafe_allow_html=True)
