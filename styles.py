"""
styles.py
─────────
Injects all CSS (responsive, mobile-first) and JavaScript
into the Streamlit app via st.markdown.

Call inject(T, COLORS, AI_CARD_BG, AI_CARD_SH, BADGE_BG, BADGE_BDR, PILL_BG, PILL_BDR)
once at the top of app.py, after the theme has been resolved.
"""

import streamlit as st


def inject(T, COLORS, AI_CARD_BG, AI_CARD_SH, BADGE_BG, BADGE_BDR, PILL_BG, PILL_BDR):
    """Inject themed CSS + JS into the Streamlit page."""
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

/* ── Layout ── */
.block-container{{padding:1rem 0.75rem 5rem !important;max-width:1400px !important;}}
@media(min-width:480px){{.block-container{{padding:1.25rem 1rem 5rem !important;}}}}
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
.welcome-wrap{{min-height:70vh;display:flex;flex-direction:column;justify-content:center;padding:2rem 0 1.5rem;}}
@media(min-width:768px){{.welcome-wrap{{min-height:80vh;padding:3rem 0 2rem;}}}}
.welcome-eyebrow{{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:4px;text-transform:uppercase;color:{T['accent']};margin-bottom:0.75rem;}}
@media(min-width:768px){{.welcome-eyebrow{{font-size:10px;letter-spacing:5px;}}}}
.welcome-title{{font-family:'Syne',sans-serif;font-size:clamp(40px,13vw,96px);font-weight:800;line-height:0.88;letter-spacing:-2px;color:{T['text_head']};margin:0 0 1rem;}}
@media(min-width:768px){{.welcome-title{{letter-spacing:-4px;margin-bottom:1.5rem;}}}}
.welcome-title span{{color:{T['accent']};}}
.welcome-sub{{font-family:'DM Sans',sans-serif;font-size:14px;color:{T['text_muted']};font-weight:300;max-width:520px;line-height:1.7;margin-bottom:2rem;}}
@media(min-width:768px){{.welcome-sub{{font-size:16px;line-height:1.8;margin-bottom:3rem;}}}}
.feature-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:{T['divider']};border:1px solid {T['divider']};margin-bottom:2rem;max-width:700px;overflow:hidden;}}
@media(min-width:600px){{.feature-grid{{grid-template-columns:repeat(4,1fr);}}}}
.feature-card{{background:{T['card']};padding:1rem 0.9rem;transition:background 0.2s;}}
@media(min-width:768px){{.feature-card{{padding:1.5rem 1.25rem;}}}}
.feature-card:hover{{background:{T['card2']};}}
.feature-icon{{font-size:18px;margin-bottom:0.4rem;}}
.feature-title{{font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:{T['text_head']};margin-bottom:0.25rem;}}
@media(min-width:768px){{.feature-title{{font-size:14px;}}}}
.feature-desc{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;color:{T['text_dim']};text-transform:uppercase;line-height:1.5;}}

/* ── Hero ── */
.hero{{padding:1rem 0;border-bottom:1px solid {T['divider']};margin-bottom:1rem;}}
@media(min-width:768px){{.hero{{padding:1.5rem 0 1.25rem;margin-bottom:1.25rem;}}}}
.hero-eyebrow{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T['accent']};margin-bottom:0.25rem;}}
.hero-title{{font-family:'Syne',sans-serif;font-size:clamp(22px,6vw,52px);font-weight:800;line-height:0.92;letter-spacing:-1px;color:{T['text_head']};margin:0;}}
@media(min-width:768px){{.hero-title{{letter-spacing:-1.5px;}}}}
.hero-title span{{color:{T['accent']};}}
.hero-file{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1.5px;color:{T['text_dim']};margin-top:0.4rem;text-transform:uppercase;word-break:break-all;}}
@media(min-width:768px){{.hero-file{{font-size:10px;letter-spacing:2px;}}}}

/* ── Status bar ── */
.status-bar{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:0.45rem 0.65rem;margin-bottom:1rem;background:{T['card']};border:1px solid {T['divider']};border-left:2px solid {T['accent']};font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;box-shadow:{T['card_shadow']};}}
@media(min-width:768px){{.status-bar{{gap:18px;padding:0.55rem 0.9rem;font-size:9px;letter-spacing:1.5px;margin-bottom:1.5rem;}}}}
.status-dot{{width:5px;height:5px;border-radius:50%;display:inline-block;flex-shrink:0;}}
@media(min-width:768px){{.status-dot{{width:6px;height:6px;}}}}
.status-item{{display:flex;align-items:center;gap:4px;color:{T['text_dim']};}}
@media(min-width:768px){{.status-item{{gap:6px;}}}}
.status-item strong{{color:{T['text_head']};font-weight:500;}}

/* ── Metrics ── */
.metrics-row{{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:{T['divider']};border:1px solid {T['divider']};margin-bottom:1rem;overflow:hidden;}}
@media(min-width:480px){{.metrics-row{{grid-template-columns:repeat(3,1fr);}}}}
@media(min-width:900px){{.metrics-row{{grid-template-columns:repeat(5,1fr);}}}}
.metric-card{{background:{T['card']};padding:0.85rem 0.9rem;position:relative;overflow:hidden;transition:background 0.2s;}}
@media(min-width:768px){{.metric-card{{padding:1.2rem 1.25rem;}}}}
.metric-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,{T['accent']},transparent);opacity:0;transition:opacity 0.3s;}}
.metric-card:hover::before{{opacity:1;}}
.metric-label{{font-family:'DM Mono',monospace;font-size:7px;letter-spacing:1.5px;text-transform:uppercase;color:{T['text_dim']};margin-bottom:0.25rem;}}
@media(min-width:768px){{.metric-label{{font-size:9px;letter-spacing:2px;margin-bottom:0.4rem;}}}}
.metric-value{{font-family:'Syne',sans-serif;font-size:clamp(16px,4vw,32px);font-weight:800;color:{T['text_head']};line-height:1;letter-spacing:-1px;}}
.metric-value span{{font-size:8px;font-weight:400;color:{T['text_dim']};font-family:'DM Mono',monospace;margin-left:1px;}}
@media(min-width:768px){{.metric-value span{{font-size:10px;margin-left:2px;}}}}
.metric-sub{{font-family:'DM Mono',monospace;font-size:7px;color:{T['accent']};margin-top:2px;}}
@media(min-width:768px){{.metric-sub{{font-size:9px;margin-top:3px;}}}}

/* ── Section label ── */
.section-label{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:3px;text-transform:uppercase;color:{T['accent']};margin-bottom:0.75rem;display:flex;align-items:center;gap:8px;}}
@media(min-width:768px){{.section-label{{font-size:9px;letter-spacing:4px;margin-bottom:1rem;gap:10px;}}}}
.section-label::after{{content:'';flex:1;height:1px;background:{T['divider']};}}

/* ── Inputs ── */
.stSelectbox>div>div,.stMultiSelect>div>div{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;}}
.stSelectbox>div>div:focus-within,.stMultiSelect>div>div:focus-within{{border-color:{T['accent']} !important;box-shadow:0 0 0 1px {T['accent']} !important;}}
.stSelectbox label,.stMultiSelect label,.stTextInput label,.stTextArea label{{font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;}}
@media(min-width:768px){{.stSelectbox label,.stMultiSelect label,.stTextInput label,.stTextArea label{{font-size:10px !important;letter-spacing:2px !important;}}}}
.stTextInput input{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;font-size:14px !important;}}
@media(min-width:768px){{.stTextInput input{{font-size:15px !important;}}}}
.stTextInput input:focus{{border-color:{T['accent']} !important;box-shadow:0 0 0 1px {T['accent']} !important;}}
.stTextArea textarea{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;font-size:13px !important;}}
.stTextArea textarea:focus{{border-color:{T['accent']} !important;box-shadow:0 0 0 1px {T['accent']} !important;}}
.stNumberInput input{{background:{T['input_bg']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;}}

/* ── Buttons ── */
.stButton>button{{background:transparent !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;padding:0.6rem 1rem !important;transition:all 0.2s !important;width:100% !important;border-radius:2px !important;}}
@media(min-width:768px){{.stButton>button{{font-size:10px !important;letter-spacing:2px !important;padding:0.7rem 1.4rem !important;}}}}
.stButton>button:hover{{background:{T['accent']} !important;border-color:{T['accent']} !important;color:white !important;}}
.stButton>button:active{{transform:scale(0.98) !important;}}
.stDownloadButton>button{{background:{T['accent_bg']} !important;border:1px solid {T['accent_bdr']} !important;color:{T['accent']} !important;font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;padding:0.6rem 1rem !important;width:100% !important;border-radius:2px !important;}}
@media(min-width:768px){{.stDownloadButton>button{{font-size:10px !important;letter-spacing:2px !important;padding:0.7rem 1.4rem !important;}}}}
.stDownloadButton>button:hover{{background:{T['accent']} !important;color:white !important;border-color:{T['accent']} !important;}}

/* ── File uploader ── */
[data-testid="stFileUploader"]{{background:{T['card']} !important;border:1px dashed {T['accent_bdr']} !important;padding:0.75rem !important;transition:border-color 0.2s !important;}}
@media(min-width:768px){{[data-testid="stFileUploader"]{{padding:1rem !important;}}}}
[data-testid="stFileUploader"]:hover{{border-color:{T['accent']} !important;}}
[data-testid="stFileUploader"] *{{color:{T['text']} !important;}}
[data-testid="stFileUploaderDropzone"]{{background:transparent !important;padding:1rem !important;}}
@media(min-width:768px){{[data-testid="stFileUploaderDropzone"]{{padding:1.5rem !important;}}}}
[data-testid="stFileUploader"] button,[data-testid="stFileUploaderDropzone"] button{{background:{T['accent_bg']} !important;border:1px solid {T['accent_bdr']} !important;color:{T['accent']} !important;font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;padding:0.45rem 1rem !important;border-radius:2px !important;width:auto !important;transition:all 0.2s !important;}}
[data-testid="stFileUploader"] button:hover,[data-testid="stFileUploaderDropzone"] button:hover{{background:{T['accent']} !important;color:#fff !important;border-color:{T['accent']} !important;}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{{background:transparent !important;border-bottom:1px solid {T['divider']} !important;gap:0 !important;overflow-x:auto !important;-webkit-overflow-scrolling:touch !important;scrollbar-width:none !important;}}
.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar{{display:none !important;}}
.stTabs [data-baseweb="tab"]{{background:transparent !important;color:{T['text_dim']} !important;font-family:'DM Mono',monospace !important;font-size:8px !important;letter-spacing:1px !important;text-transform:uppercase !important;border:none !important;padding:0.6rem 0.65rem !important;white-space:nowrap !important;transition:color 0.15s !important;}}
@media(min-width:768px){{.stTabs [data-baseweb="tab"]{{font-size:10px !important;letter-spacing:1.5px !important;padding:0.75rem 1rem !important;}}}}
.stTabs [aria-selected="true"]{{color:{T['accent']} !important;border-bottom:2px solid {T['accent']} !important;}}
.stTabs [data-baseweb="tab-panel"]{{padding-top:1rem !important;}}

/* ── Cards ── */
.insight-card{{background:{T['card']};border:1px solid {T['divider']};border-left:3px solid {T['accent']};padding:0.85rem 1rem;margin-bottom:0.6rem;font-family:'DM Sans',sans-serif;font-size:13px;color:{T['text_muted']};line-height:1.6;box-shadow:{T['card_shadow']};}}
@media(min-width:768px){{.insight-card{{padding:1.1rem 1.25rem;font-size:14px;line-height:1.7;margin-bottom:0.75rem;}}}}
.insight-card strong{{color:{T['text_head']};font-weight:500;}}
.insight-icon{{font-family:'DM Mono',monospace;font-size:8px;color:{T['accent']};letter-spacing:2px;text-transform:uppercase;margin-bottom:0.35rem;}}
@media(min-width:768px){{.insight-icon{{font-size:9px;letter-spacing:3px;margin-bottom:0.5rem;}}}}

/* ── AI card ── */
.ai-card{{background:{AI_CARD_BG};border:1px solid {T['accent_glow']};padding:1rem;margin-top:0.75rem;position:relative;box-shadow:{AI_CARD_SH};}}
@media(min-width:768px){{.ai-card{{padding:1.5rem;margin-top:1rem;}}}}
.ai-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,{T['accent']},transparent 60%);}}
.ai-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:0.75rem;}}
@media(min-width:768px){{.ai-card-header{{margin-bottom:1rem;}}}}
.ai-card-label{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:2px;text-transform:uppercase;color:{T['accent']};}}
@media(min-width:768px){{.ai-card-label{{font-size:9px;letter-spacing:3px;}}}}
.ai-copy-btn{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;color:{T['text_dim']};background:{T['input_bg']};border:1px solid {T['divider']};padding:3px 8px;cursor:pointer;border-radius:2px;transition:all 0.15s;user-select:none;}}
.ai-copy-btn:hover{{color:{T['accent']};border-color:{T['accent_bdr']};}}
.ai-card-text{{font-family:'DM Sans',sans-serif;font-size:13px;color:{T['text_muted']};line-height:1.7;white-space:pre-wrap;}}
@media(min-width:768px){{.ai-card-text{{font-size:14px;line-height:1.8;}}}}

/* ── Empty state ── */
.empty-state{{text-align:center;padding:2rem 0.75rem;border:1px dashed {T['divider']};background:{T['card']};}}
@media(min-width:768px){{.empty-state{{padding:3rem 1rem;}}}}
.empty-state-icon{{font-size:26px;margin-bottom:0.6rem;opacity:0.45;}}
@media(min-width:768px){{.empty-state-icon{{font-size:32px;margin-bottom:0.75rem;}}}}
.empty-state-title{{font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:{T['text_head']};margin-bottom:0.3rem;}}
@media(min-width:768px){{.empty-state-title{{font-size:16px;margin-bottom:0.4rem;}}}}
.empty-state-sub{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;color:{T['text_faint']};text-transform:uppercase;}}

/* ── Annotations ── */
.annotation-panel{{background:{T['card']};border:1px solid {T['divider']};padding:1rem;margin-top:0.75rem;box-shadow:{T['card_shadow']};}}
.annotation-item{{border-bottom:1px solid {T['divider_faint']};padding:0.65rem 0;font-family:'DM Sans',sans-serif;font-size:12px;color:{T['text_muted']};line-height:1.5;}}
.annotation-item:last-child{{border-bottom:none;}}
.annotation-tag{{font-family:'DM Mono',monospace;font-size:8px;color:{T['accent']};letter-spacing:2px;text-transform:uppercase;margin-bottom:2px;}}

/* ── Quality ── */
.quality-bar-wrap{{background:{T['divider']};height:4px;border-radius:3px;margin-top:4px;overflow:hidden;}}
.quality-bar{{height:100%;border-radius:3px;}}
.quality-row{{display:flex;justify-content:space-between;align-items:flex-start;padding:8px 0;border-bottom:1px solid {T['divider_faint']};gap:8px;}}
.quality-col-name{{font-family:'DM Sans',sans-serif;font-size:12px;color:{T['text_head']};}}
@media(min-width:768px){{.quality-col-name{{font-size:13px;}}}}
.quality-col-type{{font-family:'DM Mono',monospace;font-size:8px;color:{T['accent']};background:{T['accent_bg']};padding:2px 6px;border-radius:2px;white-space:nowrap;flex-shrink:0;}}
.quality-col-stats{{font-family:'DM Mono',monospace;font-size:8px;color:{T['text_dim']};text-align:right;min-width:65px;flex-shrink:0;line-height:1.5;}}
@media(min-width:768px){{.quality-col-stats{{font-size:10px;min-width:80px;}}}}

/* ── Badges / errors ── */
.clean-badge{{display:inline-block;background:{BADGE_BG};border:1px solid {BADGE_BDR};color:{T['green']};font-family:'DM Mono',monospace;font-size:8px;letter-spacing:1px;text-transform:uppercase;padding:2px 6px;margin:2px;}}
@media(min-width:768px){{.clean-badge{{font-size:9px;padding:3px 8px;margin:3px;}}}}
.error-box{{background:{T['accent_bg']};border:1px solid {T['accent_bdr']};padding:0.9rem 1rem;font-family:'DM Sans',sans-serif;font-size:13px;color:{T['text_muted']};line-height:1.6;margin:0.75rem 0;}}
@media(min-width:768px){{.error-box{{padding:1.2rem 1.5rem;font-size:14px;line-height:1.7;margin:1rem 0;}}}}
.error-box strong{{color:{T['accent']};}}

/* ── Tables ── */
.table-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid {T['divider']};box-shadow:{T['card_shadow']};}}
.stats-table{{width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;font-size:10px;min-width:480px;}}
@media(min-width:768px){{.stats-table{{font-size:11px;min-width:600px;}}}}
.stats-table th{{background:{T['accent_bg']};color:{T['accent']};letter-spacing:1.5px;text-transform:uppercase;padding:7px 10px;text-align:left;border-bottom:1px solid {T['divider']};font-size:8px;white-space:nowrap;}}
@media(min-width:768px){{.stats-table th{{letter-spacing:2px;padding:10px 14px;font-size:9px;}}}}
.stats-table td{{padding:5px 10px;border-bottom:1px solid {T['divider_faint']};color:{T['text_muted']};white-space:nowrap;vertical-align:middle;}}
@media(min-width:768px){{.stats-table td{{padding:7px 14px;}}}}
.stats-table tr:nth-child(even) td{{background:{T['hover_bg']};}}
.stats-table tr:hover td{{color:{T['text']};}}
.stats-table .col-name{{color:{T['text_head']};font-weight:500;}}
.sparkline-cell{{padding:4px 10px !important;}}
@media(min-width:768px){{.sparkline-cell{{padding:6px 14px !important;}}}}
.type-table{{width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;font-size:10px;}}
@media(min-width:768px){{.type-table{{font-size:11px;}}}}
.type-table th{{background:{T['accent_bg']};color:{T['accent']};letter-spacing:1.5px;text-transform:uppercase;padding:7px 10px;text-align:left;border-bottom:1px solid {T['divider']};font-size:8px;}}
@media(min-width:768px){{.type-table th{{letter-spacing:2px;padding:10px 14px;font-size:9px;}}}}
.type-table td{{padding:5px 10px;border-bottom:1px solid {T['divider_faint']};color:{T['text_muted']};vertical-align:middle;}}
@media(min-width:768px){{.type-table td{{padding:7px 14px;}}}}
.type-table tr:nth-child(even) td{{background:{T['hover_bg']};}}
.type-table .col-name{{color:{T['text_head']};}}
.type-pill{{display:inline-block;background:{PILL_BG};border:1px solid {PILL_BDR};color:{T['blue']};font-family:'DM Mono',monospace;font-size:8px;padding:2px 6px;border-radius:2px;}}
@media(min-width:768px){{.type-pill{{font-size:9px;padding:2px 8px;}}}}

/* ── Sidebar ── */
.sidebar-brand{{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:{T['text_head']};letter-spacing:-0.5px;padding:1.25rem 0 0.15rem;}}
@media(min-width:768px){{.sidebar-brand{{font-size:22px;padding:1.5rem 0 0.2rem;}}}}
.sidebar-brand span{{color:{T['accent']};}}
.sidebar-tagline{{font-family:'DM Mono',monospace;font-size:8px;letter-spacing:3px;color:{T['text_faint']};text-transform:uppercase;margin-bottom:1.25rem;}}

/* ── Theme pill ── */
.theme-pill-wrap{{position:fixed;top:0.5rem;right:0.5rem;z-index:999;}}
@media(min-width:768px){{.theme-pill-wrap{{top:0.75rem;right:1rem;}}}}
.theme-pill-wrap .stButton>button{{border-radius:20px !important;padding:4px 10px !important;font-size:8px !important;letter-spacing:1px !important;box-shadow:{T['pill_shadow']} !important;white-space:nowrap !important;background:{T['card']} !important;border:1px solid {T['input_bdr']} !important;color:{T['text']} !important;width:auto !important;}}
@media(min-width:768px){{.theme-pill-wrap .stButton>button{{padding:5px 16px 5px 12px !important;font-size:10px !important;}}}}
.theme-pill-wrap .stButton>button:hover{{background:{T['accent']} !important;border-color:{T['accent']} !important;color:#fff !important;}}

/* ── Scroll to top ── */
#scroll-top-btn{{position:fixed;bottom:3.2rem;right:0.5rem;z-index:200;width:28px;height:28px;border-radius:50%;background:{T['card']};border:1px solid {T['divider']};color:{T['text_dim']};font-size:12px;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.3s,background 0.2s;box-shadow:{T['pill_shadow']};}}
@media(min-width:768px){{#scroll-top-btn{{width:32px;height:32px;bottom:3.5rem;right:1rem;font-size:14px;}}}}
#scroll-top-btn:hover{{background:{T['accent']};color:#fff;border-color:{T['accent']};}}
#scroll-top-btn.visible{{opacity:1;}}

/* ── Footer ── */
.footer{{position:fixed;bottom:0;left:0;right:0;z-index:100;background:{T['footer_bg']};border-top:1px solid {T['divider']};padding:5px 0.75rem;display:flex;align-items:center;justify-content:space-between;font-family:'DM Mono',monospace;font-size:7px;letter-spacing:1px;text-transform:uppercase;color:{T['text_faint']};}}
@media(min-width:768px){{.footer{{padding:7px 2rem;font-size:9px;letter-spacing:1.5px;}}}}
.footer-brand{{color:{T['accent']};font-weight:500;}}
.footer-right{{display:flex;align-items:center;gap:8px;}}
@media(min-width:768px){{.footer-right{{gap:18px;}}}}
.footer-hide-mobile{{display:none;}}
@media(min-width:600px){{.footer-hide-mobile{{display:inline;}}}}
.kbd{{display:inline-block;background:{T['card']};border:1px solid {T['divider']};border-radius:2px;padding:1px 4px;font-family:'DM Mono',monospace;font-size:7px;color:{T['text_faint']};}}

/* ── Misc ── */
hr{{border-color:{T['divider']} !important;margin:1.25rem 0 !important;}}
@media(min-width:768px){{hr{{margin:1.5rem 0 !important;}}}}
.stAlert{{background:{T['accent_bg']} !important;border:1px solid {T['accent_bdr']} !important;color:{T['text']} !important;}}
.stToggle label{{font-family:'DM Mono',monospace !important;font-size:9px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;letter-spacing:1px !important;}}
[data-testid="stExpander"]{{border:1px solid {T['divider']} !important;background:{T['card']} !important;}}
[data-testid="stExpander"] summary{{font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;}}
[data-testid="stDataFrame"]{{border:1px solid {T['divider']} !important;box-shadow:{T['card_shadow']};}}
.stRadio label{{font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;}}
[data-testid="stSlider"] label{{font-family:'DM Mono',monospace !important;font-size:9px !important;letter-spacing:1px !important;text-transform:uppercase !important;color:{T['text_dim']} !important;}}
[data-testid="stMarkdownContainer"] p{{color:{T['text_muted']};line-height:1.6;font-size:13px;}}
@media(min-width:768px){{[data-testid="stMarkdownContainer"] p{{line-height:1.7;font-size:14px;}}}}
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
