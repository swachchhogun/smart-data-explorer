import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json, requests, io, datetime

st.set_page_config(page_title="DataLens", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")

for k, v in [("annotations", []), ("type_overrides", {}), ("show_app", False),
             ("dark_mode", True), ("last_ai_text", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Theme tokens ──────────────────────────────────────────
if st.session_state.dark_mode:
    T = dict(
        bg="#0a0a0f",
        bg_grad="radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,90,50,0.07) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(80,180,255,0.05) 0%, transparent 60%), #0a0a0f",
        sidebar="#0d0d16", sidebar_bdr="rgba(255,255,255,0.06)",
        card="#0f0f18", card2="#12101f",
        text="#e8e4dc", text_head="#f0ece4",
        text_muted="rgba(232,228,220,0.45)", text_dim="rgba(232,228,220,0.3)", text_faint="rgba(232,228,220,0.18)",
        accent="#ff5a32", accent_bg="rgba(255,90,50,0.08)", accent_bdr="rgba(255,90,50,0.3)", accent_glow="rgba(255,90,50,0.2)",
        blue="#50b4ff", green="#a8e063", yellow="#f7c948",
        divider="rgba(255,255,255,0.07)", divider_faint="rgba(255,255,255,0.04)",
        input_bg="#0f0f18", input_bdr="rgba(255,255,255,0.1)",
        plot_bg="#0d0d16", hover_bg="rgba(255,255,255,0.025)",
        grid="rgba(255,255,255,0.04)", line="rgba(255,255,255,0.07)", tick="rgba(232,228,220,0.35)",
        footer_bg="#08080c", pill_shadow="0 2px 14px rgba(0,0,0,0.5)", card_shadow="none",
        sparkline="#ff5a32",
    )
    COLORS = ["#ff5a32","#50b4ff","#a8e063","#f7c948","#c678dd","#56b6c2","#e06c75","#d19a66"]
    AI_CARD_BG = "linear-gradient(135deg, #0f0f18 0%, #12101f 100%)"; AI_CARD_SH = "none"
    BADGE_BG="rgba(168,224,99,0.1)"; BADGE_BDR="rgba(168,224,99,0.25)"
    PILL_BG="rgba(80,180,255,0.1)"; PILL_BDR="rgba(80,180,255,0.2)"
else:
    T = dict(
        bg="#f0f4f8",
        bg_grad="radial-gradient(ellipse 80% 50% at 20% 10%, rgba(67,97,238,0.06) 0%, transparent 60%), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(76,201,188,0.05) 0%, transparent 60%), #f0f4f8",
        sidebar="#e4eaf2", sidebar_bdr="rgba(0,0,0,0.08)",
        card="#ffffff", card2="#f7f9fc",
        text="#1e2433", text_head="#0f1623",
        text_muted="rgba(30,36,51,0.6)", text_dim="rgba(30,36,51,0.4)", text_faint="rgba(30,36,51,0.22)",
        accent="#4361ee", accent_bg="rgba(67,97,238,0.08)", accent_bdr="rgba(67,97,238,0.28)", accent_glow="rgba(67,97,238,0.15)",
        blue="#0077b6", green="#2d7d46", yellow="#b07d00",
        divider="rgba(0,0,0,0.08)", divider_faint="rgba(0,0,0,0.05)",
        input_bg="#ffffff", input_bdr="rgba(0,0,0,0.14)",
        plot_bg="#f7f9fc", hover_bg="rgba(0,0,0,0.025)",
        grid="rgba(0,0,0,0.055)", line="rgba(0,0,0,0.09)", tick="rgba(30,36,51,0.45)",
        footer_bg="#e4eaf2", pill_shadow="0 2px 10px rgba(0,0,0,0.12)", card_shadow="0 1px 4px rgba(0,0,0,0.06)",
        sparkline="#4361ee",
    )
    COLORS = ["#4361ee","#0077b6","#2d7d46","#b5500a","#7b2d8b","#0e7490","#9b2335","#7a5c00"]
    AI_CARD_BG = "linear-gradient(135deg, #f5f7ff 0%, #eef1fd 100%)"; AI_CARD_SH = "0 2px 12px rgba(67,97,238,0.08)"
    BADGE_BG="rgba(45,125,70,0.08)"; BADGE_BDR="rgba(45,125,70,0.25)"
    PILL_BG="rgba(0,119,182,0.08)"; PILL_BDR="rgba(0,119,182,0.2)"

# ── CSS ───────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');
*,*::before,*::after{{box-sizing:border-box;}}

html,body,[data-testid="stAppViewContainer"]{{background:{T['bg']} !important;color:{T['text']} !important;font-family:'DM Sans',sans-serif !important;}}
[data-testid="stAppViewContainer"]{{background:{T['bg_grad']} !important;}}
[data-testid="stSidebar"]{{background:{T['sidebar']} !important;border-right:1px solid {T['sidebar_bdr']} !important;}}
[data-testid="stSidebar"] *{{color:{T['text']} !important;}}
[data-testid="stSidebar"] .stSelectbox>div>div,[data-testid="stSidebar"] .stMultiSelect>div>div{{background:{T['input_bg']} !important;border-color:{T['input_bdr']} !important;}}
#MainMenu,footer,header{{visibility:hidden;}}
[data-testid="stDecoration"]{{display:none;}}
.block-container{{padding:1.5rem 1.25rem 5rem !important;max-width:1400px !important;}}
@media(min-width:768px){{.block-container{{padding:2rem 2.5rem 5rem !important;}}}}

/* ── Entrance animation ── */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
.metric-card{{animation:fadeUp 0.35s ease both;}}
.metric-card:nth-child(1){{animation-delay:0.05s;}}
.metric-card:nth-child(2){{animation-delay:0.10s;}}
.metric-card:nth-child(3){{animation-delay:0.15s;}}
.metric-card:nth-child(4){{animation-delay:0.20s;}}
.metric-card:nth-child(5){{animation-delay:0.25s;}}
.insight-card{{animation:fadeUp 0.3s ease both;}}

/* ── Welcome ── */
.welcome-wrap{{min-height:80vh;display:flex;flex-direction:column;justify-content:center;padding:3rem 0 2rem;}}
.welcome-eyebrow{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:5px;text-transform:uppercase;color:{T['accent']};margin-bottom:1rem;}}
.welcome-title{{font-family:'Syne',sans-serif;font-size:clamp(48px,12vw,96px);font-weight:800;line-height:0.88;letter-spacing:-4px;color:{T['text_head']};margin:0 0 1.5rem;}}
.welcome-title span{{color:{T['accent']};}}
.welcome-sub{{font-family:'DM Sans',sans-serif;font-size:16px;color:{T['text_muted']};font-weight:300;max-width:520px;line-height:1.8;margin-bottom:3rem;}}
.feature-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:{T['divider']};border:1px solid {T['divider']};margin-bottom:3rem;max-width:700px;overflow:hidden;}}
@media(min-width:600px){{.feature-grid{{grid-template-columns:repeat(4,1fr);}}}}
.feature-card{{background:{T['card']};padding:1.5rem 1.25rem;transition:background 0.2s;}}
.feature-card:hover{{background:{T['card2']};}}
.feature-icon{{font-size:20px;margin-bottom:0.6rem;}}
.feature-title{{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:{T['text_head']};margin-bottom:0.3rem;}}
.feature-desc{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;color:{T['text_dim']};text-transform:uppercase;line-height:1.6;}}

/* ── Hero ── */
.hero{{padding:1.5rem 0 1.25rem;border-bottom:1px solid {T['divider']};margin-bottom:1.25rem;}}
.hero-eyebrow{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T['accent']};margin-bottom:0.3rem;}}
.hero-title{{font-family:'Syne',sans-serif;font-size:clamp(28px,6vw,52px);font-weight:800;line-height:0.92;letter-spacing:-1.5px;color:{T['text_head']};margin:0;}}
.hero-title span{{color:{T['accent']};}}
.hero-file{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:2px;color:{T['text_dim']};margin-top:0.5rem;text-transform:uppercase;}}

/* ── Status bar ── */
.status-bar{{display:flex;align-items:center;gap:18px;flex-wrap:wrap;padding:0.55rem 0.9rem;margin-bottom:1.5rem;background:{T['card']};border:1px solid {T['divider']};border-left:2px solid {T['accent']};font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;box-shadow:{T['card_shadow']};}}
.status-dot{{width:6px;height:6px;border-radius:50%;display:inline-block;flex-shrink:0;}}
.status-item{{display:flex;align-items:center;gap:6px;color:{T['text_dim']};}}
.status-item strong{{color:{T['text_head']};font-weight:500;}}

/* ── Metrics ── */
.metrics-row{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:{T['divider']};border:1px solid {T['divider']};margin-bottom:1.5rem;overflow:hidden;}}
@media(min-width:600px){{.metrics-row{{grid-template-columns:repeat(3,1fr);}}}}
@media(min-width:900px){{.metrics-row{{grid-template-columns:repeat(5,1fr);}}}}
.metric-card{{background:{T['card']};padding:1.2rem 1.25rem;position:relative;overflow:hidden;transition:background 0.2s;}}
.metric-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{T['accent']},transparent);opacity:0;transition:opacity 0.3s;}}
.metric-card:hover::before{{opacity:1;}}
.metric-label{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{T['text_dim']};margin-bottom:0.4rem;}}
.metric-value{{font-family:'Syne',sans-serif;font-size:clamp(22px,4vw,32px);font-weight:800;color:{T['text_head']};line-height:1;letter-spacing:-1px;}}
.metric-value span{{font-size:10px;font-weight:400;color:{T['text_dim']};font-family:'DM Mono',monospace;margin-left:2px;}}
.metric-sub{{font-family:'DM Mono',monospace;font-size:9px;color:{T['accent']};margin-top:3px;}}

/* ── Section label ── */
.section-label{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T['accent']};margin-bottom:1rem;display:flex;align-items:center;gap:10px;}}
.section-label::after{{content:'';flex:1;height:1px;background:{T['divider']};}}

/* ── Inputs ── */
.stSelectbox>div>div,.stMultiSelect>div>div{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;}}
.stSelectbox>div>div:focus-within,.stMultiSelect>div>div:focus-within{{border-color:{T['accent']} !important;box-shadow:0 0 0 1px {T['accent']} !important;}}
.stSelectbox label,.stMultiSelect label,.stTextInput label,.stTextArea label{{font-family:'DM Mono',monospace !important;font-size:10px !important;letter-spacing:2px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;}}
.stTextInput input{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;font-size:15px !important;}}
.stTextInput input:focus{{border-color:{T['accent']} !important;box-shadow:0 0 0 1px {T['accent']} !important;}}
.stTextArea textarea{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;font-size:13px !important;}}
.stTextArea textarea:focus{{border-color:{T['accent']} !important;box-shadow:0 0 0 1px {T['accent']} !important;}}
.stNumberInput input{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;}}

/* ── Buttons ── */
.stButton>button{{background:transparent !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;font-family:'DM Mono',monospace !important;font-size:10px !important;letter-spacing:2px !important;text-transform:uppercase !important;padding:0.7rem 1.4rem !important;transition:all 0.2s !important;width:100% !important;border-radius:2px !important;}}
.stButton>button:hover{{background:{T['accent']} !important;border-color:{T['accent']} !important;color:white !important;}}
.stButton>button:active{{transform:scale(0.98) !important;}}
.stDownloadButton>button{{background:{T['accent_bg']} !important;border:1px solid {T['accent_bdr']} !important;color:{T['accent']} !important;font-family:'DM Mono',monospace !important;font-size:10px !important;letter-spacing:2px !important;text-transform:uppercase !important;padding:0.7rem 1.4rem !important;width:100% !important;border-radius:2px !important;}}
.stDownloadButton>button:hover{{background:{T['accent']} !important;color:white !important;border-color:{T['accent']} !important;}}

/* ── File uploader ── */
[data-testid="stFileUploader"]{{background:{T['card']} !important;border:1px dashed {T['accent_bdr']} !important;padding:1rem !important;transition:border-color 0.2s !important;}}
[data-testid="stFileUploader"]:hover{{border-color:{T['accent']} !important;}}
[data-testid="stFileUploader"] *{{color:{T['text']} !important;}}
[data-testid="stFileUploaderDropzone"]{{background:transparent !important;padding:1.5rem !important;}}
[data-testid="stFileUploader"] button,[data-testid="stFileUploaderDropzone"] button{{background:{T['accent_bg']} !important;border:1px solid {T['accent_bdr']} !important;color:{T['accent']} !important;font-family:'DM Mono',monospace !important;font-size:10px !important;letter-spacing:2px !important;text-transform:uppercase !important;padding:0.5rem 1.2rem !important;border-radius:2px !important;width:auto !important;transition:all 0.2s !important;}}
[data-testid="stFileUploader"] button:hover,[data-testid="stFileUploaderDropzone"] button:hover{{background:{T['accent']} !important;color:#fff !important;border-color:{T['accent']} !important;}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{{background:transparent !important;border-bottom:1px solid {T['divider']} !important;gap:0 !important;overflow-x:auto !important;}}
.stTabs [data-baseweb="tab"]{{background:transparent !important;color:{T['text_dim']} !important;font-family:'DM Mono',monospace !important;font-size:10px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;border:none !important;padding:0.75rem 1rem !important;white-space:nowrap !important;transition:color 0.15s !important;}}
.stTabs [aria-selected="true"]{{color:{T['accent']} !important;border-bottom:2px solid {T['accent']} !important;}}
.stTabs [data-baseweb="tab-panel"]{{padding-top:1.25rem !important;}}

/* ── Cards ── */
.insight-card{{background:{T['card']};border:1px solid {T['divider']};border-left:3px solid {T['accent']};padding:1.1rem 1.25rem;margin-bottom:0.75rem;font-family:'DM Sans',sans-serif;font-size:14px;color:{T['text_muted']};line-height:1.7;box-shadow:{T['card_shadow']};}}
.insight-card strong{{color:{T['text_head']};font-weight:500;}}
.insight-icon{{font-family:'DM Mono',monospace;font-size:9px;color:{T['accent']};letter-spacing:3px;text-transform:uppercase;margin-bottom:0.5rem;}}

/* ── AI card with copy button ── */
.ai-card{{background:{AI_CARD_BG};border:1px solid {T['accent_glow']};padding:1.5rem;margin-top:1rem;position:relative;box-shadow:{AI_CARD_SH};}}
.ai-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,{T['accent']},transparent 60%);}}
.ai-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;}}
.ai-card-label{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:{T['accent']};}}
.ai-copy-btn{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;text-transform:uppercase;color:{T['text_dim']};background:{T['input_bg']};border:1px solid {T['divider']};padding:3px 10px;cursor:pointer;border-radius:2px;transition:all 0.15s;user-select:none;}}
.ai-copy-btn:hover{{color:{T['accent']};border-color:{T['accent_bdr']};}}
.ai-card-text{{font-family:'DM Sans',sans-serif;font-size:14px;color:{T['text_muted']};line-height:1.8;white-space:pre-wrap;}}

/* ── Empty state ── */
.empty-state{{text-align:center;padding:3rem 1rem;border:1px dashed {T['divider']};background:{T['card']};}}
.empty-state-icon{{font-size:32px;margin-bottom:0.75rem;opacity:0.45;}}
.empty-state-title{{font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:{T['text_head']};margin-bottom:0.4rem;}}
.empty-state-sub{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;color:{T['text_faint']};text-transform:uppercase;}}

/* ── Annotations ── */
.annotation-panel{{background:{T['card']};border:1px solid {T['divider']};padding:1.25rem;margin-top:1rem;box-shadow:{T['card_shadow']};}}
.annotation-item{{border-bottom:1px solid {T['divider_faint']};padding:0.75rem 0;font-family:'DM Sans',sans-serif;font-size:13px;color:{T['text_muted']};line-height:1.6;}}
.annotation-item:last-child{{border-bottom:none;}}
.annotation-tag{{font-family:'DM Mono',monospace;font-size:9px;color:{T['accent']};letter-spacing:2px;text-transform:uppercase;margin-bottom:3px;}}

/* ── Quality ── */
.quality-bar-wrap{{background:{T['divider']};height:5px;border-radius:3px;margin-top:5px;overflow:hidden;}}
.quality-bar{{height:100%;border-radius:3px;}}
.quality-row{{display:flex;justify-content:space-between;align-items:flex-start;padding:10px 0;border-bottom:1px solid {T['divider_faint']};gap:8px;}}
.quality-col-name{{font-family:'DM Sans',sans-serif;font-size:13px;color:{T['text_head']};}}
.quality-col-type{{font-family:'DM Mono',monospace;font-size:9px;color:{T['accent']};background:{T['accent_bg']};padding:2px 7px;border-radius:2px;white-space:nowrap;flex-shrink:0;}}
.quality-col-stats{{font-family:'DM Mono',monospace;font-size:10px;color:{T['text_dim']};text-align:right;min-width:80px;flex-shrink:0;line-height:1.6;}}

/* ── Badges / errors ── */
.clean-badge{{display:inline-block;background:{BADGE_BG};border:1px solid {BADGE_BDR};color:{T['green']};font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;text-transform:uppercase;padding:3px 8px;margin:3px;}}
.error-box{{background:{T['accent_bg']};border:1px solid {T['accent_bdr']};padding:1.2rem 1.5rem;font-family:'DM Sans',sans-serif;font-size:14px;color:{T['text_muted']};line-height:1.7;margin:1rem 0;}}
.error-box strong{{color:{T['accent']};}}

/* ── Stats table with sparkline column ── */
.table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid {T['divider']};box-shadow:{T['card_shadow']};}}
.stats-table{{width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;font-size:11px;min-width:600px;}}
.stats-table th{{background:{T['accent_bg']};color:{T['accent']};letter-spacing:2px;text-transform:uppercase;padding:10px 14px;text-align:left;border-bottom:1px solid {T['divider']};font-size:9px;white-space:nowrap;}}
.stats-table td{{padding:7px 14px;border-bottom:1px solid {T['divider_faint']};color:{T['text_muted']};white-space:nowrap;vertical-align:middle;}}
.stats-table tr:nth-child(even) td{{background:{T['hover_bg']};}}
.stats-table tr:hover td{{color:{T['text']};}}
.stats-table .col-name{{color:{T['text_head']};font-weight:500;}}
.sparkline-cell{{padding:6px 14px !important;}}

/* ── Type table ── */
.type-table{{width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;font-size:11px;}}
.type-table th{{background:{T['accent_bg']};color:{T['accent']};letter-spacing:2px;text-transform:uppercase;padding:10px 14px;text-align:left;border-bottom:1px solid {T['divider']};font-size:9px;}}
.type-table td{{padding:7px 14px;border-bottom:1px solid {T['divider_faint']};color:{T['text_muted']};vertical-align:middle;}}
.type-table tr:nth-child(even) td{{background:{T['hover_bg']};}}
.type-table .col-name{{color:{T['text_head']};}}
.type-pill{{display:inline-block;background:{PILL_BG};border:1px solid {PILL_BDR};color:{T['blue']};font-family:'DM Mono',monospace;font-size:9px;padding:2px 8px;border-radius:2px;}}

/* ── Sidebar ── */
.sidebar-brand{{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:{T['text_head']};letter-spacing:-0.5px;padding:1.5rem 0 0.2rem;}}
.sidebar-brand span{{color:{T['accent']};}}
.sidebar-tagline{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:3px;color:{T['text_faint']};text-transform:uppercase;margin-bottom:1.5rem;}}

/* ── Theme toggle pill ── */
.theme-pill-wrap{{position:fixed;top:0.75rem;right:1rem;z-index:999;}}
.theme-pill-wrap .stButton>button{{border-radius:20px !important;padding:5px 16px 5px 12px !important;font-size:10px !important;letter-spacing:1px !important;box-shadow:{T['pill_shadow']} !important;white-space:nowrap !important;background:{T['card']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;width:auto !important;}}
.theme-pill-wrap .stButton>button:hover{{background:{T['accent']} !important;border-color:{T['accent']} !important;color:#fff !important;}}
#scroll-top-btn{{position:fixed;bottom:3.5rem;right:1rem;z-index:200;width:32px;height:32px;border-radius:50%;background:{T['card']};border:1px solid {T['divider']};color:{T['text_dim']};font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.3s,background 0.2s;box-shadow:{T['pill_shadow']};}}
#scroll-top-btn:hover{{background:{T['accent']};color:#fff;border-color:{T['accent']};}}
#scroll-top-btn.visible{{opacity:1;}}

/* ── Footer ── */
.footer{{position:fixed;bottom:0;left:0;right:0;z-index:100;background:{T['footer_bg']};border-top:1px solid {T['divider']};padding:7px 2rem;display:flex;align-items:center;justify-content:space-between;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:{T['text_faint']};}}
.footer-brand{{color:{T['accent']};font-weight:500;}}
.footer-right{{display:flex;align-items:center;gap:18px;}}
.kbd{{display:inline-block;background:{T['card']};border:1px solid {T['divider']};border-radius:2px;padding:1px 5px;font-family:'DM Mono',monospace;font-size:8px;color:{T['text_faint']};}}

/* ── Misc ── */
hr{{border-color:{T['divider']} !important;margin:1.5rem 0 !important;}}
.stAlert{{background:{T['accent_bg']} !important;border:1px solid {T['accent_bdr']} !important;color:{T['text']} !important;}}
.stToggle label{{font-family:'DM Mono',monospace !important;font-size:10px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;letter-spacing:1px !important;}}
[data-testid="stExpander"]{{border:1px solid {T['divider']} !important;background:{T['card']} !important;}}
[data-testid="stExpander"] summary{{font-family:'DM Mono',monospace !important;font-size:10px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;}}
[data-testid="stDataFrame"]{{border:1px solid {T['divider']} !important;box-shadow:{T['card_shadow']};}}
</style>

<script>
document.addEventListener('keydown', function(e) {{
    if (e.key === 't' || e.key === 'T') {{
        if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
        var btns = window.parent.document.querySelectorAll('button');
        btns.forEach(function(b) {{
            if (b.innerText.includes('Day') || b.innerText.includes('Night')) {{ b.click(); }}
        }});
    }}
}});
(function() {{
    var btn = document.createElement('button');
    btn.id = 'scroll-top-btn'; btn.innerHTML = '↑'; btn.title = 'Back to top';
    btn.onclick = function() {{ window.parent.document.querySelector('.main').scrollTo({{top:0,behavior:'smooth'}}); }};
    document.body.appendChild(btn);
    var mainEl = window.parent.document.querySelector('.main');
    if (mainEl) {{ mainEl.addEventListener('scroll', function() {{ btn.classList.toggle('visible', this.scrollTop > 300); }}); }}
}})();
</script>
""", unsafe_allow_html=True)

# ── Plotly helpers ────────────────────────────────────────
def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor=T["plot_bg"],
        font=dict(family="DM Sans", color=T["text"], size=11),
        title_font=dict(family="Syne", size=15, color=T["text_head"]),
        colorway=COLORS,
        xaxis=dict(gridcolor=T["grid"], linecolor=T["line"], zeroline=False,
                   tickfont=dict(family="DM Mono", size=9, color=T["tick"]),
                   title_font=dict(family="DM Mono", size=9, color=T["tick"])),
        yaxis=dict(gridcolor=T["grid"], linecolor=T["line"], zeroline=False,
                   tickfont=dict(family="DM Mono", size=9, color=T["tick"]),
                   title_font=dict(family="DM Mono", size=9, color=T["tick"])),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(family="DM Mono", size=9, color=T["tick"]),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=8, r=8, t=48, b=8),
        hoverlabel=dict(bgcolor=T["card"], font_family="DM Mono", font_size=11, bordercolor=T["accent_glow"]),
    )
    return fig

def add_annotations_to_fig(fig, annotations):
    for ann in annotations:
        fig.add_annotation(
            x=ann.get("x",0.5), y=ann.get("y",0.5),
            xref=ann.get("xref","paper"), yref=ann.get("yref","paper"),
            text=f"◈ {ann['text']}", showarrow=ann.get("arrow",True),
            arrowhead=2, arrowcolor=T["accent"], arrowwidth=1.5,
            font=dict(family="DM Sans", size=11, color=T["text_head"]),
            bgcolor=T["card"], bordercolor=T["accent"], borderwidth=1, borderpad=6,
        )
    return fig

def make_sparkline_svg(values, color, w=80, h=24):
    """Tiny inline SVG sparkline for stats table."""
    try:
        vals = [float(v) for v in values if pd.notna(v)]
        if len(vals) < 2: return ""
        mn, mx = min(vals), max(vals)
        rng = mx - mn or 1
        pts = []
        for i, v in enumerate(vals):
            x = round(i / (len(vals)-1) * w, 1)
            y = round(h - (v - mn) / rng * (h-4) - 2, 1)
            pts.append(f"{x},{y}")
        path = "M" + " L".join(pts)
        return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
                f'style="display:block;overflow:visible;">'
                f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                f'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
                f'</svg>')
    except Exception:
        return ""

def empty_state(icon, title, sub):
    return (f'<div class="empty-state"><div class="empty-state-icon">{icon}</div>'
            f'<div class="empty-state-title">{title}</div>'
            f'<div class="empty-state-sub">{sub}</div></div>')

def ai_card_html(label, text):
    escaped = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    safe_text = text.replace("`","'").replace('"', "'")
    return f"""<div class="ai-card">
  <div class="ai-card-header">
    <div class="ai-card-label">◈ {label}</div>
    <span class="ai-copy-btn" onclick="navigator.clipboard.writeText(`{safe_text}`);this.innerText='Copied ✓';setTimeout(()=>this.innerText='Copy',1500)">Copy</span>
  </div>
  <div class="ai-card-text">{escaped}</div>
</div>"""

# ── Data helpers ──────────────────────────────────────────
def safe_read_csv(file):
    for enc in ["utf-8","latin-1","utf-16","cp1252"]:
        for sep in [",",";","\t"]:
            try:
                file.seek(0)
                df = pd.read_csv(file, encoding=enc, sep=sep)
                if df.shape[1] > 1 or sep == ",": return df, None
            except Exception: continue
    return None, "Could not read this file. Make sure it's a valid CSV."

def smart_clean(df):
    report, cleaned = [], df.copy()
    cleaned.columns = [c.strip() for c in cleaned.columns]
    if cleaned.empty: return cleaned, ["File is empty."]
    for col in cleaned.select_dtypes(include="object").columns:
        try:
            p = pd.to_datetime(cleaned[col], infer_datetime_format=True, errors="coerce")
            if p.notna().mean() > 0.7:
                cleaned[col] = p; report.append(f"Parsed '{col}' as datetime")
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
    if before - len(cleaned) > 0: report.append(f"Removed {before-len(cleaned)} empty rows")
    n_d = int(cleaned.duplicated().sum())
    if n_d > 0: cleaned = cleaned.drop_duplicates(); report.append(f"Removed {n_d} duplicate rows")
    return cleaned, report

TYPE_OPTIONS = ["Auto (keep as-is)","Text / String","Integer","Float / Decimal","Date / Time","Boolean"]

def apply_type_overrides(df, overrides):
    out = df.copy()
    for col, t in overrides.items():
        if col not in out.columns: continue
        try:
            if t == "Text / String":     out[col] = out[col].astype(str)
            elif t == "Integer":         out[col] = pd.to_numeric(out[col], errors="coerce").astype("Int64")
            elif t == "Float / Decimal": out[col] = pd.to_numeric(out[col], errors="coerce")
            elif t == "Date / Time":     out[col] = pd.to_datetime(out[col], errors="coerce")
            elif t == "Boolean":         out[col] = out[col].map(lambda x: True if str(x).lower() in ("1","true","yes","y") else False)
        except Exception: pass
    return out

@st.cache_data(show_spinner=False, ttl=300)
def get_ai_insights(data_json: str, question: str = "") -> str:
    prompt = (f"You are a senior data analyst. Analyze this dataset concisely and professionally.\n"
              f"Dataset: {data_json}\n"
              f"{'Question: ' + question if question else 'Give 4-5 key insights: patterns, outliers, distributions, findings. Use specific numbers. Be direct.'}\n"
              f"Format: numbered points, plain language, no filler.")
    key = st.secrets.get("GROQ_API_KEY","")
    if not key:
        return ("⚠️ No Groq API key found.\n\nSetup (free, 2 mins):\n"
                "1. Sign up at console.groq.com\n2. Create API key\n"
                "3. Streamlit Cloud → Settings → Secrets:\n   GROQ_API_KEY = \"your-key\"")
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":[{"role":"user","content":prompt}],
                  "max_tokens":800,"temperature":0.3}, timeout=20)
        d = r.json()
        if "choices" in d: return d["choices"][0]["message"]["content"]
        return f"Groq error: {d.get('error',{}).get('message', str(d))}"
    except requests.exceptions.Timeout: return "Request timed out. Try again."
    except Exception as e: return f"Could not reach Groq: {e}"

def build_summary(df):
    nd = df.select_dtypes(include="number"); cd = df.select_dtypes(include="object")
    return json.dumps({
        "shape": list(df.shape), "columns": list(df.columns),
        "numeric_stats": nd.describe().round(2).to_dict() if len(nd.columns) > 0 else {},
        "categorical_top": {c: df[c].value_counts().head(3).to_dict() for c in cd.columns[:4]},
        "missing": df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
    }, default=str)

def nl_to_chart_spec(user_request: str, df_columns: list, numeric_cols: list, cat_cols: list) -> dict:
    """Ask the LLM to return a JSON chart spec from a natural language request."""
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return {"error": "no_key"}
    col_info = (f"All columns: {df_columns}\n"
                f"Numeric columns: {numeric_cols}\n"
                f"Categorical columns: {cat_cols}")
    prompt = f"""You are a data visualization assistant. Given a natural language chart request and available columns, return ONLY a valid JSON object — no explanation, no markdown, no backticks.

{col_info}

User request: "{user_request}"

Return a JSON object with these exact keys:
- "chart_type": one of: bar, line, scatter, histogram, box, pie, violin, area
- "x": column name for x-axis (or null)
- "y": column name for y-axis (or null)
- "color": column name to color by (or null)
- "aggregation": one of: mean, sum, count, median, none
- "title": a short descriptive chart title
- "error": null, or a short message if the request can't be fulfilled with available columns

Only use column names that exist exactly in the provided lists. Return ONLY the JSON."""
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 300, "temperature": 0.1}, timeout=15)
        d = r.json()
        if "choices" not in d:
            return {"error": d.get("error", {}).get("message", "API error")}
        raw = d["choices"][0]["message"]["content"].strip()
        # strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        spec = json.loads(raw)
        return spec
    except json.JSONDecodeError:
        return {"error": "Could not parse AI response. Try rephrasing your request."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again."}
    except Exception as e:
        return {"error": str(e)}

def render_nl_chart(spec: dict, df, style_fig, add_annotations_to_fig, anns, COLORS, accent, T):
    """Render a Plotly chart from an AI-generated spec dict."""
    ct = spec.get("chart_type", "bar")
    x  = spec.get("x")
    y  = spec.get("y")
    color = spec.get("color")
    agg = spec.get("aggregation", "none")
    title = spec.get("title", "Chart")

    # Validate columns exist
    all_cols = list(df.columns)
    if x and x not in all_cols: x = None
    if y and y not in all_cols: y = None
    if color and color not in all_cols: color = None

    plot_df = df.copy()

    # Aggregate if needed
    if agg != "none" and x and y:
        fn_map = {"mean": "mean", "sum": "sum", "count": "count", "median": "median"}
        fn = fn_map.get(agg, "mean")
        group_cols = [x] + ([color] if color else [])
        try:
            plot_df = df.groupby(group_cols)[y].agg(fn).reset_index()
        except Exception:
            plot_df = df.copy()

    try:
        if ct == "bar":
            if x and y:
                fig = px.bar(plot_df, x=x, y=y, color=color, title=title,
                             color_discrete_sequence=COLORS)
                if not color: fig.update_traces(marker_color=accent, marker_line_width=0)
            elif x:
                vc = plot_df[x].value_counts().reset_index()
                vc.columns = [x, "count"]
                fig = px.bar(vc, x=x, y="count", title=title)
                fig.update_traces(marker_color=accent, marker_line_width=0)
            else:
                return None, "Bar chart needs at least an X column."

        elif ct == "line":
            if x and y:
                fig = px.line(plot_df, x=x, y=y, color=color, title=title,
                              color_discrete_sequence=COLORS)
                if not color: fig.update_traces(line_color=accent, line_width=2)
            else:
                return None, "Line chart needs X and Y columns."

        elif ct == "scatter":
            if x and y:
                fig = px.scatter(plot_df, x=x, y=y, color=color, title=title,
                                 opacity=0.72, color_discrete_sequence=COLORS,
                                 trendline="ols" if not color else None)
                if not color: fig.update_traces(marker=dict(color=accent, size=6))
            else:
                return None, "Scatter plot needs X and Y columns."

        elif ct == "histogram":
            col = x or y
            if not col: return None, "Histogram needs a column."
            fig = px.histogram(plot_df, x=col, color=color, title=title,
                               nbins=30, barmode="overlay", opacity=0.85,
                               color_discrete_sequence=COLORS)
            if not color: fig.update_traces(marker_color=accent)

        elif ct == "box":
            col = y or x
            if not col: return None, "Box plot needs a column."
            fig = px.box(plot_df, y=col, x=color, color=color, title=title,
                         color_discrete_sequence=COLORS, points="outliers")
            if not color: fig.update_traces(marker_color=accent, line_color=T["blue"])

        elif ct == "violin":
            col = y or x
            if not col: return None, "Violin plot needs a column."
            fig = px.violin(plot_df, y=col, x=color, color=color, title=title,
                            box=True, color_discrete_sequence=COLORS)
            if not color: fig.update_traces(fillcolor=T["accent_glow"], line_color=accent)

        elif ct == "pie":
            if x:
                vc = plot_df[x].value_counts().reset_index()
                vc.columns = [x, "count"]
                vals = y if (y and y in plot_df.columns) else "count"
                fig = px.pie(vc if vals == "count" else plot_df, names=x, values=vals,
                             title=title, color_discrete_sequence=COLORS, hole=0.3)
            else:
                return None, "Pie chart needs a category column."

        elif ct == "area":
            if x and y:
                fig = px.area(plot_df, x=x, y=y, color=color, title=title,
                              color_discrete_sequence=COLORS)
                if not color: fig.update_traces(line_color=accent, fillcolor=T["accent_glow"])
            else:
                return None, "Area chart needs X and Y columns."
        else:
            return None, f"Unknown chart type: {ct}"

        return style_fig(add_annotations_to_fig(fig, anns)), None

    except Exception as e:
        return None, f"Could not render chart: {e}"

def col_health(s):
    null_pct = s.isnull().mean() * 100
    unique_pct = s.nunique() / max(len(s),1) * 100
    score = max(0, 100 - null_pct - (20 if unique_pct > 95 and pd.api.types.is_object_dtype(s) else 0))
    return {"null_pct": round(null_pct,1), "unique": s.nunique(), "score": round(score)}

def hcolor(score):
    if score >= 80: return T["green"]
    if score >= 50: return T["yellow"]
    return T["accent"]

def to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
        if hasattr(writer, 'sheets'):
            ws = writer.sheets["Data"]
            for col_cells in ws.columns:
                max_len = max(len(str(c.value or "")) for c in col_cells)
                ws.column_dimensions[col_cells[0].column_letter].width = min(max_len + 2, 40)
    buf.seek(0)
    return buf.read()

def generate_pdf_report(df, filename, ai_text, clean_report):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
        from reportlab.lib.styles import ParagraphStyle
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm)
        BG=colors.HexColor("#0a0a0f"); CARD=colors.HexColor("#0f0f18"); ACCENT=colors.HexColor("#ff5a32")
        TEXT=colors.HexColor("#f0ece4"); MUTED=colors.HexColor("#6b6760"); LINE=colors.HexColor("#1e1e2a"); BLUE=colors.HexColor("#50b4ff")
        def sty(name, **kw):
            base = dict(fontName="Helvetica", fontSize=10, textColor=TEXT, leading=14, spaceAfter=4)
            base.update(kw); return ParagraphStyle(name, **base)
        S_EY=sty("ey",fontSize=7,textColor=ACCENT,fontName="Helvetica-Bold",leading=10)
        S_TI=sty("ti",fontSize=28,textColor=TEXT,fontName="Helvetica-Bold",leading=30)
        S_MO=sty("mo",fontSize=8,textColor=BLUE,fontName="Courier",leading=12)
        S_SE=sty("se",fontSize=7,textColor=ACCENT,fontName="Helvetica-Bold",leading=10,spaceAfter=6)
        S_AI=sty("ai",fontSize=9,textColor=colors.HexColor("#c8c4bc"),leading=15)
        def HR(): return HRFlowable(width="100%",thickness=0.5,color=LINE,spaceAfter=10,spaceBefore=10)
        def SP(h=6): return Spacer(1,h)
        tbl_style = TableStyle([
            ("BACKGROUND",(0,0),(-1,0),ACCENT),("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
            ("BACKGROUND",(0,1),(-1,-1),CARD),("TEXTCOLOR",(0,1),(-1,-1),TEXT),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[CARD,colors.HexColor("#111120")]),
            ("GRID",(0,0),(-1,-1),0.3,LINE),
            ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ])
        nc=df.select_dtypes(include="number").columns.tolist(); cc=df.select_dtypes(include="object").columns.tolist()
        miss=int(df.isnull().sum().sum()); comp=round((1-miss/max(df.size,1))*100,1)
        story=[SP(20),Paragraph("◈ SMART DATA EXPLORER",S_EY),SP(4),Paragraph("DataLens",S_TI),
               Paragraph("Analysis Report",sty("sub",fontSize=13,textColor=MUTED,leading=16)),
               SP(10),HR(),Paragraph(f"File: {filename}",S_MO),
               Paragraph(f"Generated: {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}",S_MO),
               Paragraph(f"Rows: {df.shape[0]:,}   Columns: {df.shape[1]}",S_MO),HR(),SP(10)]
        story.append(Paragraph("DATASET OVERVIEW",S_SE))
        ov=Table([["Metric","Value"],["Total rows",f"{df.shape[0]:,}"],["Total columns",str(df.shape[1])],
                  ["Numeric cols",str(len(nc))],["Categorical cols",str(len(cc))],
                  ["Missing values",f"{miss:,}"],["Completeness",f"{comp}%"],
                  ["Duplicate rows",str(int(df.duplicated().sum()))]],colWidths=[80*mm,80*mm])
        ov.setStyle(tbl_style); story+=[ov,SP(16)]
        story.append(Paragraph("COLUMNS",S_SE))
        cd2=[["Column Name","Type","Nulls","Unique"]]
        for col in df.columns: cd2.append([col[:35],str(df[col].dtype),str(int(df[col].isnull().sum())),str(df[col].nunique())])
        ct=Table(cd2,colWidths=[75*mm,35*mm,25*mm,25*mm]); ct.setStyle(tbl_style); story+=[ct,SP(16)]
        if nc:
            story+=[PageBreak(),Paragraph("NUMERIC STATISTICS",S_SE)]
            stats=df[nc].describe().T.round(3); stats["median"]=df[nc].median().round(3); stats["skew"]=df[nc].skew().round(3)
            keep=["count","mean","median","std","min","max","skew"]; stats=stats[[c for c in keep if c in stats.columns]]
            hdr=["Column"]+list(stats.columns)
            sd=[hdr]+[[str(rn)[:20]]+[f"{v:,.3f}" if isinstance(v,float) else str(int(v)) for v in row] for rn,row in stats.iterrows()]
            st2=Table(sd,colWidths=[50*mm]+[18*mm]*(len(hdr)-1)); st2.setStyle(tbl_style); story+=[st2,SP(16)]
        if clean_report:
            story+=[HR(),Paragraph("CLEANING APPLIED",S_SE)]
            for note in clean_report: story.append(Paragraph(f"✓  {note}",S_AI))
        story+=[PageBreak(),Paragraph("AI INSIGHTS",S_SE),Paragraph("Powered by Llama 3.3 70B via Groq (free)",S_MO),SP(8)]
        for line in ai_text.split("\n"):
            line=line.strip()
            if line: story.append(Paragraph(line,S_AI)); story.append(SP(3))
        story+=[SP(20),HR(),Paragraph("Generated by DataLens · Smart Data Explorer",S_MO),
                Paragraph(f"Report date: {datetime.datetime.now().strftime('%d %B %Y')}",S_MO)]
        doc.build(story); buf.seek(0); return buf.read()
    except ImportError: return None
    except Exception as e: st.error(f"PDF error: {e}"); return None

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">Data<span>Lens</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">◈ Smart Explorer</div>', unsafe_allow_html=True)
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
                           file_name="datalens_export.csv", mime="text/csv", use_container_width=True)
        if st.button("← Start over", use_container_width=True):
            for k in ["working_df","filtered_df","raw_df","cleaned_df","clean_report",
                      "show_app","annotations","type_overrides"]:
                st.session_state.pop(k, None)
            st.rerun()
    else:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;color:{T["text_faint"]};text-transform:uppercase;padding:0.5rem 0;">Upload a CSV on the main page to unlock filters & export.</div>', unsafe_allow_html=True)

# ── Theme toggle ──────────────────────────────────────────
_icon = "☀️ Day" if st.session_state.dark_mode else "🌙 Night"
st.markdown('<div class="theme-pill-wrap">', unsafe_allow_html=True)
_gap, _pill = st.columns([30, 1])
with _pill:
    if st.button(_icon, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── Welcome ───────────────────────────────────────────────
if not st.session_state.show_app:
    st.markdown(f"""
    <div class="welcome-wrap">
        <div class="welcome-eyebrow">◈ Smart Data Explorer</div>
        <div class="welcome-title">Data<span>Lens</span></div>
        <div class="welcome-sub">Upload any CSV and get instant charts, statistics, AI-powered insights, and a beautiful PDF report — all free.</div>
        <div class="feature-grid">
            <div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Auto Clean</div><div class="feature-desc">Nulls filled · Dupes removed · Types inferred</div></div>
            <div class="feature-card"><div class="feature-icon">◈</div><div class="feature-title">8 Chart Modes</div><div class="feature-desc">Histogram · Heatmap · Scatter Matrix · Trend</div></div>
            <div class="feature-card"><div class="feature-icon">🤖</div><div class="feature-title">Free AI</div><div class="feature-desc">Llama 3.3 70B via Groq · No cost · Instant insights</div></div>
            <div class="feature-card"><div class="feature-icon">📄</div><div class="feature-title">Export</div><div class="feature-desc">PDF report · CSV · Excel · Stats table</div></div>
        </div>
    </div>""", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("◈ Get started — Upload a CSV", use_container_width=True):
            st.session_state.show_app = True; st.rerun()
    st.stop()

# ── Main app ──────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Your Data</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown(f'<div class="empty-state" style="margin-top:1rem;"><div class="empty-state-icon">📂</div><div class="empty-state-title">Drop a CSV file above</div><div class="empty-state-sub">Any CSV · Auto-cleaned · Free AI · PDF report</div></div>', unsafe_allow_html=True)
    st.stop()

with st.spinner("Reading file…"):
    raw_df, load_err = safe_read_csv(uploaded_file)

if load_err or raw_df is None:
    st.markdown(f'<div class="error-box"><strong>Could not load file</strong><br>{load_err}</div>', unsafe_allow_html=True); st.stop()
if raw_df.empty:
    st.markdown(f'<div class="error-box"><strong>Empty file</strong><br>The CSV has no data rows.</div>', unsafe_allow_html=True); st.stop()

st.session_state.raw_df = raw_df
try: cleaned_df, clean_report = smart_clean(raw_df)
except Exception as e: cleaned_df, clean_report = raw_df.copy(), [f"Cleaning failed: {e}"]
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
    filtered_df = base_df.copy(); st.session_state.filtered_df = filtered_df

numeric_cols = base_df.select_dtypes(include="number").columns.tolist()
cat_cols     = base_df.select_dtypes(include="object").columns.tolist()

if clean_report and use_cleaned:
    with st.expander(f"✦ Cleaning applied — {len(clean_report)} action{'s' if len(clean_report)!=1 else ''}"):
        for n in clean_report:
            st.markdown(f'<span class="clean-badge">✓ {n}</span>', unsafe_allow_html=True)

fn = uploaded_file.name if uploaded_file else "dataset.csv"

st.markdown(f"""<div class="hero">
    <div class="hero-eyebrow">◈ Smart Data Explorer</div>
    <div class="hero-title">Data<span>Lens</span></div>
    <div class="hero-file">◈ {fn} · {filtered_df.shape[0]:,} rows · {filtered_df.shape[1]} cols</div>
</div>""", unsafe_allow_html=True)

missing_count = int(filtered_df.isnull().sum().sum())
dupe_count    = int(filtered_df.duplicated().sum())
completeness  = round((1 - missing_count / max(filtered_df.size,1)) * 100, 1)
mem_kb        = filtered_df.memory_usage(deep=True).sum() / 1024

st.markdown(f"""<div class="metrics-row">
  <div class="metric-card"><div class="metric-label">Rows</div><div class="metric-value">{filtered_df.shape[0]:,}<span>r</span></div><div class="metric-sub">of {base_df.shape[0]:,} total</div></div>
  <div class="metric-card"><div class="metric-label">Columns</div><div class="metric-value">{filtered_df.shape[1]}<span>c</span></div><div class="metric-sub">{len(numeric_cols)} num · {len(cat_cols)} cat</div></div>
  <div class="metric-card"><div class="metric-label">Complete</div><div class="metric-value">{completeness}<span>%</span></div><div class="metric-sub">{missing_count:,} nulls</div></div>
  <div class="metric-card"><div class="metric-label">Duplicates</div><div class="metric-value">{dupe_count}<span>r</span></div><div class="metric-sub">{"✓ none" if dupe_count == 0 else "⚠ detected"}</div></div>
  <div class="metric-card"><div class="metric-label">Memory</div><div class="metric-value">{mem_kb:.0f}<span>kb</span></div><div class="metric-sub">in memory</div></div>
</div>""", unsafe_allow_html=True)

dot_color = T["green"] if completeness >= 80 else (T["yellow"] if completeness >= 50 else T["accent"])
clean_txt = f"{len(clean_report)} cleanings applied" if (use_cleaned and clean_report) else "raw data"
filter_txt = f"{filtered_df.shape[0]:,} of {base_df.shape[0]:,} rows" if filtered_df.shape[0] != base_df.shape[0] else "no active filters"
st.markdown(f"""<div class="status-bar">
    <div class="status-item"><span class="status-dot" style="background:{dot_color};"></span><span>Completeness <strong>{completeness}%</strong></span></div>
    <div class="status-item">◈ {clean_txt}</div>
    <div class="status-item">◈ {filter_txt}</div>
    <div class="status-item">◈ {'Day' if not st.session_state.dark_mode else 'Night'} mode</div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Analysis Mode</div>', unsafe_allow_html=True)
analysis_type = st.selectbox("Mode", [
    "Dashboard Overview", "Distribution Analysis", "Category Comparison",
    "Correlation Analysis", "Trend Over Time", "Scatter Explorer",
    "Heatmap", "Box Plot Comparison", "Scatter Matrix",
], label_visibility="collapsed")

tab_explore, tab_nl, tab_quality, tab_types, tab_stats, tab_ai, tab_report = st.tabs([
    "◈  Explore", "◈  AI Chart", "◈  Data Quality", "◈  Column Types",
    "◈  Statistics", "◈  AI Insights", "◈  PDF Report"
])
accent = T["accent"]

# ═══ EXPLORE ═══════════════════════════════════════════════
with tab_explore:
    st.markdown('<div class="section-label">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(filtered_df.head(10), use_container_width=True, hide_index=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-label">{analysis_type}</div>', unsafe_allow_html=True)

    with st.expander("◈ Chart Annotations", expanded=False):
        ann_text = st.text_input("Annotation text", placeholder="e.g. Sharp spike in Q3", key="ann_text")
        c1,c2,c3 = st.columns(3)
        with c1: ann_x = st.number_input("X (0–1)", 0.0, 1.0, 0.5, 0.05, key="ann_x")
        with c2: ann_y = st.number_input("Y (0–1)", 0.0, 1.0, 0.9, 0.05, key="ann_y")
        with c3: ann_arrow = st.toggle("Arrow", value=True, key="ann_arrow")
        if st.button("◈ Add annotation", key="add_ann"):
            if ann_text.strip():
                st.session_state.annotations.append({"text": ann_text.strip(), "x": ann_x, "y": ann_y, "xref":"paper","yref":"paper","arrow": ann_arrow})
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
                col_sel = st.selectbox("Numeric column", numeric_cols, key="dash_num")
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
            if not numeric_cols: st.markdown(empty_state("📈","No numeric columns","Need numeric data"), unsafe_allow_html=True)
            else:
                column   = st.selectbox("Numeric Column", numeric_cols, key="dist_col")
                color_by = st.selectbox("Color by (optional)", ["None"]+cat_cols, key="dist_color")
                ca = None if color_by == "None" else color_by
                fig = px.histogram(filtered_df, x=column, color=ca, nbins=30,
                                   title=f"Histogram · {column}", barmode="overlay", opacity=0.8)
                if not ca: fig.update_traces(marker_color=accent, marker_line_color="rgba(0,0,0,0.12)", marker_line_width=1)
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)
                fig2 = px.violin(filtered_df, y=column, color=ca, title=f"Violin · {column}", box=True)
                if not ca: fig2.update_traces(fillcolor=T["accent_glow"], line_color=accent)
                st.plotly_chart(style_fig(add_annotations_to_fig(fig2, anns)), use_container_width=True)

        elif analysis_type == "Category Comparison":
            if not cat_cols or not numeric_cols: st.markdown(empty_state("🗂️","Need categorical + numeric columns","Upload data with both types"), unsafe_allow_html=True)
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
                                 color_discrete_sequence=COLORS, hole=0.3)
                    fig.update_traces(textfont=dict(family="DM Mono", size=10))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        elif analysis_type == "Correlation Analysis":
            if len(numeric_cols) < 2: st.markdown(empty_state("🔗","Need 2+ numeric columns","Correlation needs at least two numeric columns"), unsafe_allow_html=True)
            else:
                method = st.selectbox("Method", ["pearson","spearman","kendall"], key="corr_method")
                corr   = filtered_df[numeric_cols].corr(method=method)
                fig    = px.imshow(corr, text_auto=".2f", title=f"Correlation Matrix ({method.title()})",
                                   color_continuous_scale=[[0,T["blue"]],[0.5,T["card"]],[1,accent]], zmin=-1, zmax=1)
                fig.update_traces(textfont=dict(family="DM Mono", size=10, color=T["text_head"]))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)
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
                fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df[num_col], mode="lines", name="Raw",
                                          line=dict(color=T["accent_glow"], width=1)))
                if smooth != "None":
                    w = 7 if "7" in smooth else 30
                    plot_df = plot_df.copy(); plot_df["_ma"] = plot_df[num_col].rolling(w, min_periods=1).mean()
                    fig.add_trace(go.Scatter(x=plot_df[date_col], y=plot_df["_ma"], mode="lines", name=smooth,
                                              line=dict(color=accent, width=2.5)))
                fig.update_layout(title=f"{num_col} over Time")
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        elif analysis_type == "Scatter Explorer":
            if len(numeric_cols) < 2: st.markdown(empty_state("🔵","Need 2+ numeric columns","Scatter needs at least two numeric columns"), unsafe_allow_html=True)
            else:
                x_col = st.selectbox("X Axis", numeric_cols, key="sc_x")
                y_col = st.selectbox("Y Axis", numeric_cols, index=min(1,len(numeric_cols)-1), key="sc_y")
                color_col = st.selectbox("Color by (optional)", ["None"]+cat_cols+numeric_cols, key="sc_col")
                size_col  = st.selectbox("Size by (optional)", ["None"]+numeric_cols, key="sc_sz")
                ca = None if color_col=="None" else color_col; sa = None if size_col=="None" else size_col
                fig = px.scatter(filtered_df, x=x_col, y=y_col, color=ca, size=sa, title=f"{y_col} vs {x_col}",
                                 opacity=0.72, trendline="ols" if ca is None else None,
                                 color_discrete_sequence=COLORS, color_continuous_scale=[[0,T["card"]],[1,accent]])
                if ca is None and sa is None:
                    fig.update_traces(marker=dict(color=accent, size=6, line=dict(color="rgba(0,0,0,0.12)", width=1)))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        # ── NEW: Heatmap ────────────────────────────────────
        elif analysis_type == "Heatmap":
            if not cat_cols or not numeric_cols:
                st.markdown(empty_state("🟥","Need categorical + numeric columns","Heatmap requires both column types"), unsafe_allow_html=True)
            else:
                row_col  = st.selectbox("Row", cat_cols, key="hm_row")
                col_col  = st.selectbox("Column", [c for c in cat_cols if c != row_col] or cat_cols, key="hm_col")
                val_col  = st.selectbox("Value (aggregated)", numeric_cols, key="hm_val")
                agg_fn   = st.selectbox("Aggregation", ["Mean","Sum","Count","Median"], key="hm_agg")
                fn_map   = {"Mean":"mean","Sum":"sum","Count":"count","Median":"median"}
                pivot_df = filtered_df.groupby([row_col, col_col])[val_col].agg(fn_map[agg_fn]).reset_index()
                pivot    = pivot_df.pivot(index=row_col, columns=col_col, values=val_col).fillna(0)
                fig = px.imshow(pivot, text_auto=".1f", title=f"{agg_fn} of {val_col} · {row_col} vs {col_col}",
                                color_continuous_scale=[[0,T["plot_bg"]],[0.5,T["blue"]],[1,accent]],
                                aspect="auto")
                fig.update_traces(textfont=dict(family="DM Mono", size=9))
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        # ── NEW: Box Plot Comparison ────────────────────────
        elif analysis_type == "Box Plot Comparison":
            if not numeric_cols:
                st.markdown(empty_state("📦","No numeric columns","Need numeric data for box plots"), unsafe_allow_html=True)
            else:
                mode = st.radio("Mode", ["Multi-column", "Split by category"], horizontal=True, key="bp_mode")
                if mode == "Multi-column":
                    cols_sel = st.multiselect("Columns to compare", numeric_cols, default=numeric_cols[:min(4, len(numeric_cols))], key="bp_cols")
                    if cols_sel:
                        melt_df = filtered_df[cols_sel].melt(var_name="Column", value_name="Value")
                        fig = px.box(melt_df, x="Column", y="Value", title="Box Plot Comparison",
                                     color="Column", color_discrete_sequence=COLORS)
                        fig.update_traces(marker=dict(size=4, opacity=0.5))
                        st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)
                else:
                    if not cat_cols:
                        st.markdown(empty_state("🗂️","No categorical columns","Need a category column to split by"), unsafe_allow_html=True)
                    else:
                        num_sel = st.selectbox("Numeric column", numeric_cols, key="bp_num")
                        cat_sel = st.selectbox("Split by", cat_cols, key="bp_cat")
                        fig = px.box(filtered_df, x=cat_sel, y=num_sel, color=cat_sel,
                                     title=f"{num_sel} by {cat_sel}", color_discrete_sequence=COLORS,
                                     points="outliers")
                        fig.update_traces(marker=dict(size=4, opacity=0.6))
                        st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

        # ── NEW: Scatter Matrix ─────────────────────────────
        elif analysis_type == "Scatter Matrix":
            if len(numeric_cols) < 2:
                st.markdown(empty_state("🔶","Need 2+ numeric columns","Scatter matrix needs at least two numeric columns"), unsafe_allow_html=True)
            else:
                max_cols = st.slider("Number of columns to include", 2, min(8, len(numeric_cols)), min(4, len(numeric_cols)), key="sm_n")
                cols_sel = numeric_cols[:max_cols]
                color_by = st.selectbox("Color by (optional)", ["None"]+cat_cols, key="sm_color")
                ca = None if color_by == "None" else color_by
                fig = px.scatter_matrix(filtered_df, dimensions=cols_sel, color=ca,
                                         title=f"Scatter Matrix · {len(cols_sel)} columns",
                                         color_discrete_sequence=COLORS, opacity=0.65)
                fig.update_traces(diagonal_visible=False,
                                  marker=dict(size=3, line=dict(width=0)))
                fig.update_layout(height=600)
                st.plotly_chart(style_fig(add_annotations_to_fig(fig, anns)), use_container_width=True)

    except Exception as e:
        st.markdown(f'<div class="error-box"><strong>Chart error</strong><br>Try a different column or mode.<br><small style="opacity:0.4;font-family:DM Mono,monospace;font-size:11px;">{e}</small></div>', unsafe_allow_html=True)

# ═══ AI CHART ══════════════════════════════════════════════
with tab_nl:
    st.markdown('<div class="section-label">Natural Language Chart Builder</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.8;">Describe any chart in plain English and AI will build it instantly. No need to pick axes or chart types — just say what you want to see.</div>', unsafe_allow_html=True)

    # Example prompts
    examples = [
        "bar chart of count by category",
        "scatter plot of the two most correlated columns",
        "histogram of the main numeric column",
        "pie chart showing top categories",
        "line chart of values over time",
        "box plot comparing a numeric column by category",
    ]
    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:2px;text-transform:uppercase;color:{T["text_dim"]};margin-bottom:0.6rem;">Try an example</div>', unsafe_allow_html=True)
    ex_cols = st.columns(3)
    for i, ex in enumerate(examples):
        with ex_cols[i % 3]:
            if st.button(ex, key=f"nl_ex_{i}"):
                st.session_state["nl_prompt"] = ex
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    nl_prompt = st.text_input(
        "Describe your chart",
        value=st.session_state.get("nl_prompt", ""),
        placeholder='e.g. "bar chart of average sales by region" or "scatter plot of age vs income"',
        key="nl_input"
    )
    nl_go = st.button("◈ Generate Chart", use_container_width=True, key="nl_go")

    if nl_go and nl_prompt.strip():
        st.session_state["nl_prompt"] = nl_prompt.strip()
        with st.spinner("Reading your request…"):
            spec = nl_to_chart_spec(
                nl_prompt.strip(),
                list(filtered_df.columns),
                numeric_cols, cat_cols
            )

        if spec.get("error") == "no_key":
            st.markdown(f"""<div class="error-box"><strong>Groq API key needed for AI Chart</strong><br><br>
                1. Sign up free at <strong>console.groq.com</strong><br>
                2. Create an API key<br>
                3. Streamlit Cloud → Settings → Secrets → add:<br><br>
                <code style="background:{T['accent_bg']};padding:4px 10px;font-family:DM Mono,monospace;font-size:12px;">GROQ_API_KEY = "gsk_xxxx"</code>
            </div>""", unsafe_allow_html=True)
        elif spec.get("error"):
            st.markdown(f'<div class="error-box"><strong>Could not generate chart</strong><br>{spec["error"]}<br><br>Try rephrasing — e.g. mention a specific column name from your dataset.</div>', unsafe_allow_html=True)
        else:
            # Show what AI decided
            x_lbl  = spec.get("x") or "—"
            y_lbl  = spec.get("y") or "—"
            ct_lbl = spec.get("chart_type", "—").title()
            ag_lbl = spec.get("aggregation", "none")
            co_lbl = spec.get("color") or "—"
            st.markdown(f"""<div class="status-bar" style="margin-bottom:1.25rem;">
                <div class="status-item">◈ Type <strong style="color:{T['text_head']}">{ct_lbl}</strong></div>
                <div class="status-item">◈ X <strong style="color:{T['text_head']}">{x_lbl}</strong></div>
                <div class="status-item">◈ Y <strong style="color:{T['text_head']}">{y_lbl}</strong></div>
                <div class="status-item">◈ Agg <strong style="color:{T['text_head']}">{ag_lbl}</strong></div>
                <div class="status-item">◈ Color <strong style="color:{T['text_head']}">{co_lbl}</strong></div>
            </div>""", unsafe_allow_html=True)

            fig, err = render_nl_chart(spec, filtered_df, style_fig, add_annotations_to_fig, anns, COLORS, accent, T)
            if err:
                st.markdown(f'<div class="error-box"><strong>Render error</strong><br>{err}</div>', unsafe_allow_html=True)
            else:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:{T["text_faint"]};margin-top:0.5rem;">Generated from: "{nl_prompt.strip()}"</div>', unsafe_allow_html=True)

    elif not nl_prompt.strip() and not nl_go:
        # Show available columns as inspiration
        st.markdown(f'<div class="section-label">Your columns</div>', unsafe_allow_html=True)
        cols_html = "".join([
            f'<span style="display:inline-block;background:{T["accent_bg"]};border:1px solid {T["accent_bdr"]};color:{T["accent"]};font-family:DM Mono,monospace;font-size:9px;padding:3px 10px;margin:3px;border-radius:2px;">{c}</span>'
            for c in filtered_df.columns
        ])
        st.markdown(f'<div style="margin-bottom:1rem;">{cols_html}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{T["text_faint"]};letter-spacing:1px;">Mention these column names in your request for best results.</div>', unsafe_allow_html=True)

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
            iqr = q3 - q1; lo, hi = q1-1.5*iqr, q3+1.5*iqr
            outliers = filtered_df[(filtered_df[oc] < lo) | (filtered_df[oc] > hi)]
            pct = round(len(outliers)/max(len(filtered_df),1)*100, 1)
            flag = T["accent"] if pct > 5 else T["green"]
            st.markdown(f"""<div class="insight-card" style="border-left-color:{flag};">
                <div class="insight-icon">◈ {oc}</div>
                Normal range: <strong>{lo:,.2f}</strong> → <strong>{hi:,.2f}</strong> &nbsp;·&nbsp;
                <strong style="color:{flag}">{len(outliers):,} rows ({pct}%)</strong> outside bounds.
                {'⚠ Significant — worth investigating.' if pct > 5 else '✓ Small proportion — likely fine.'}
            </div>""", unsafe_allow_html=True)
            fig = px.box(filtered_df, y=oc, title=f"Box Plot · {oc}", points="outliers")
            fig.update_traces(marker_color=accent, line_color=T["blue"], marker=dict(color=accent, size=5, opacity=0.7))
            st.plotly_chart(style_fig(fig), use_container_width=True)
            if len(outliers) > 0:
                with st.expander(f"View {min(len(outliers),50)} outlier rows"):
                    st.dataframe(outliers.head(50), use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Outlier error: {e}")

# ═══ COLUMN TYPES ══════════════════════════════════════════
with tab_types:
    st.markdown('<div class="section-label">Column Type Editor</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.7;">Override auto-detected column types. Changes apply immediately across all tabs.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="table-wrap"><table class="type-table"><thead><tr>{"".join(f"<th>{h}</th>" for h in ["Column","Detected Type","Active Override"])}</tr></thead><tbody>', unsafe_allow_html=True)
    for col in base_df.columns:
        override_note = st.session_state.type_overrides.get(col, "—")
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
            dc2 = ["count","mean","median","std","min","25%","75%","max","skew","nulls"]
            stats = stats[[c for c in dc2 if c in stats.columns]].round(3)

            # Build table with sparklines
            rows_html = ""
            for cn2, row in stats.iterrows():
                col_vals = filtered_df[cn2].dropna().sample(min(80, len(filtered_df)), random_state=42).values
                spark = make_sparkline_svg(col_vals, T["sparkline"])
                cells = "".join(f"<td>{v:,.3f}</td>" if isinstance(v,float) else f"<td>{int(v)}</td>" for v in row.values)
                rows_html += f"<tr><td class='col-name'>{cn2}</td>{cells}<td class='sparkline-cell'>{spark}</td></tr>"
            headers = "".join(f"<th>{c}</th>" for c in ["Column"]+list(stats.columns)+["Trend"])
            st.markdown(f'<div class="table-wrap"><table class="stats-table"><thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # Export options
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button("↓ Export stats CSV", data=stats.to_csv().encode("utf-8"),
                                   file_name="datalens_stats.csv", mime="text/csv")
            with dl2:
                try:
                    xl = to_excel_bytes(filtered_df)
                    st.download_button("↓ Export full data XLSX", data=xl,
                                       file_name=f"datalens_{fn.replace('.csv','')}.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
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
            vc.columns = [cat_sel, "count"]; vc["percent"] = (vc["count"] / vc["count"].sum() * 100).round(1)
            st.dataframe(vc.head(15), use_container_width=True, hide_index=True)
            fig = px.bar(vc.head(15), x="count", y=cat_sel, orientation="h", title=f"Value Counts · {cat_sel}")
            fig.update_traces(marker_color=accent, marker_line_width=0)
            st.plotly_chart(style_fig(fig), use_container_width=True)
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
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.25rem;line-height:1.7;">Ask anything about your data, or let AI generate automatic insights below.</div>', unsafe_allow_html=True)
    question = st.text_input("Ask a question", placeholder="e.g. What are the main trends? Any outliers?", key="ai_q")
    run_ai   = st.button("◈ Analyse with AI", use_container_width=True)
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
                corr=ndf.corr().abs(); cu=corr.unstack(); cu=cu[cu < 1].drop_duplicates()
                if not cu.empty:
                    strongest=cu.idxmax(); rc=ndf.corr().loc[strongest[0], strongest[1]]
                    d="positively" if rc > 0 else "negatively"; strength="Strong" if cu.max() > 0.7 else "Moderate"
                    st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Strongest Correlation</div><strong>{strongest[0]}</strong> and <strong>{strongest[1]}</strong> are {d} correlated (r = <strong>{cu.max():.3f}</strong>). {strength} relationship.</div>', unsafe_allow_html=True)
            skews=ndf.skew().abs().sort_values(ascending=False)
            if len(skews) > 0 and skews.iloc[0] > 1:
                st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Skewed Distribution</div><strong>{skews.index[0]}</strong> is heavily skewed (skew = {skews.iloc[0]:.2f}). Consider log-transforming before modelling.</div>', unsafe_allow_html=True)
        if missing_count > 0:
            pct=round(missing_count/max(filtered_df.size,1)*100,1); flag=T["accent"] if pct > 5 else T["yellow"]
            st.markdown(f'<div class="insight-card" style="border-left-color:{flag};"><div class="insight-icon">◈ Data Quality</div><strong>{missing_count:,}</strong> missing values ({pct}%). {"Significant — consider further imputation." if pct > 5 else "Manageable."}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Quick insights error: {e}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Export Filtered Data</div>', unsafe_allow_html=True)
    dl_c1, dl_c2 = st.columns(2)
    with dl_c1:
        st.download_button("↓ Export as CSV", data=filtered_df.to_csv(index=False).encode("utf-8"),
                           file_name="datalens_export.csv", mime="text/csv")
    with dl_c2:
        try:
            xl = to_excel_bytes(filtered_df)
            st.download_button("↓ Export as XLSX", data=xl,
                               file_name=f"datalens_{fn.replace('.csv','')}.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            st.caption("Install openpyxl for XLSX export.")

# ═══ PDF REPORT ════════════════════════════════════════════
with tab_report:
    st.markdown('<div class="section-label">Download PDF Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-family:DM Sans,sans-serif;font-size:14px;color:{T["text_muted"]};margin-bottom:1.5rem;line-height:1.8;">Generate a professionally formatted PDF with your dataset overview, column health, numeric statistics, cleaning summary, and AI insights.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card"><div class="insight-icon">◈ Report includes</div>Cover page &nbsp;·&nbsp; Dataset overview &nbsp;·&nbsp; Column health &nbsp;·&nbsp; Numeric statistics &nbsp;·&nbsp; Cleaning report &nbsp;·&nbsp; AI insights</div>', unsafe_allow_html=True)
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

# ── Footer ────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <div><span class="footer-brand">DataLens</span> &nbsp;◈&nbsp; Smart Data Explorer</div>
    <div class="footer-right">
        <span>{filtered_df.shape[0]:,} rows · {filtered_df.shape[1]} cols</span>
        <span>Groq · Llama 3.3 70B</span>
        <span><span class="kbd">T</span> theme</span>
        <span>{datetime.datetime.now().strftime('%d %b %Y')}</span>
    </div>
</div>
""", unsafe_allow_html=True)
