"""
config.py
─────────
Theme tokens, color palettes, and app-wide constants.
Imported by app.py after reading st.session_state.dark_mode.
"""

import streamlit as st


def get_theme():
    """Return theme dict T, COLORS, and card/badge variables based on current mode."""
    if st.session_state.dark_mode:
        T = dict(
            bg="#0a0a0f",
            bg_grad=(
                "radial-gradient(ellipse 80% 50% at 20% 10%, rgba(255,90,50,0.07) 0%, transparent 60%), "
                "radial-gradient(ellipse 60% 40% at 80% 80%, rgba(80,180,255,0.05) 0%, transparent 60%), #0a0a0f"
            ),
            sidebar="#0d0d16", sidebar_bdr="rgba(255,255,255,0.06)",
            card="#0f0f18", card2="#12101f",
            text="#e8e4dc", text_head="#f0ece4",
            text_muted="rgba(232,228,220,0.45)",
            text_dim="rgba(232,228,220,0.3)",
            text_faint="rgba(232,228,220,0.18)",
            accent="#ff5a32",
            accent_bg="rgba(255,90,50,0.08)",
            accent_bdr="rgba(255,90,50,0.3)",
            accent_glow="rgba(255,90,50,0.2)",
            blue="#50b4ff", green="#a8e063", yellow="#f7c948",
            divider="rgba(255,255,255,0.07)",
            divider_faint="rgba(255,255,255,0.04)",
            input_bg="#0f0f18", input_bdr="rgba(255,255,255,0.1)",
            plot_bg="#0d0d16", hover_bg="rgba(255,255,255,0.025)",
            grid="rgba(255,255,255,0.04)",
            line="rgba(255,255,255,0.07)",
            tick="rgba(232,228,220,0.35)",
            footer_bg="#08080c",
            pill_shadow="0 2px 14px rgba(0,0,0,0.5)",
            card_shadow="none",
            sparkline="#ff5a32",
        )
        COLORS = ["#ff5a32", "#50b4ff", "#a8e063", "#f7c948",
                  "#c678dd", "#56b6c2", "#e06c75", "#d19a66"]
        AI_CARD_BG = "linear-gradient(135deg, #0f0f18 0%, #12101f 100%)"
        AI_CARD_SH = "none"
        BADGE_BG  = "rgba(168,224,99,0.1)";  BADGE_BDR = "rgba(168,224,99,0.25)"
        PILL_BG   = "rgba(80,180,255,0.1)";  PILL_BDR  = "rgba(80,180,255,0.2)"
    else:
        T = dict(
            bg="#f0f4f8",
            bg_grad=(
                "radial-gradient(ellipse 80% 50% at 20% 10%, rgba(67,97,238,0.06) 0%, transparent 60%), "
                "radial-gradient(ellipse 60% 40% at 80% 80%, rgba(76,201,188,0.05) 0%, transparent 60%), #f0f4f8"
            ),
            sidebar="#e4eaf2", sidebar_bdr="rgba(0,0,0,0.08)",
            card="#ffffff", card2="#f7f9fc",
            text="#1e2433", text_head="#0f1623",
            text_muted="rgba(30,36,51,0.6)",
            text_dim="rgba(30,36,51,0.4)",
            text_faint="rgba(30,36,51,0.22)",
            accent="#4361ee",
            accent_bg="rgba(67,97,238,0.08)",
            accent_bdr="rgba(67,97,238,0.28)",
            accent_glow="rgba(67,97,238,0.15)",
            blue="#0077b6", green="#2d7d46", yellow="#b07d00",
            divider="rgba(0,0,0,0.08)",
            divider_faint="rgba(0,0,0,0.05)",
            input_bg="#ffffff", input_bdr="rgba(0,0,0,0.14)",
            plot_bg="#f7f9fc", hover_bg="rgba(0,0,0,0.025)",
            grid="rgba(0,0,0,0.055)",
            line="rgba(0,0,0,0.09)",
            tick="rgba(30,36,51,0.45)",
            footer_bg="#e4eaf2",
            pill_shadow="0 2px 10px rgba(0,0,0,0.12)",
            card_shadow="0 1px 4px rgba(0,0,0,0.06)",
            sparkline="#4361ee",
        )
        COLORS = ["#4361ee", "#0077b6", "#2d7d46", "#b5500a",
                  "#7b2d8b", "#0e7490", "#9b2335", "#7a5c00"]
        AI_CARD_BG = "linear-gradient(135deg, #f5f7ff 0%, #eef1fd 100%)"
        AI_CARD_SH = "0 2px 12px rgba(67,97,238,0.08)"
        BADGE_BG  = "rgba(45,125,70,0.08)";  BADGE_BDR = "rgba(45,125,70,0.25)"
        PILL_BG   = "rgba(0,119,182,0.08)";  PILL_BDR  = "rgba(0,119,182,0.2)"

    return T, COLORS, AI_CARD_BG, AI_CARD_SH, BADGE_BG, BADGE_BDR, PILL_BG, PILL_BDR


# Column type options for the override editor
TYPE_OPTIONS = [
    "Auto (keep as-is)",
    "Text / String",
    "Integer",
    "Float / Decimal",
    "Date / Time",
    "Boolean",
]

# App metadata
APP_NAME    = "DataLens"
APP_TAGLINE = "Smart Data Explorer"
APP_ICON    = "◈"
GROQ_MODEL  = "llama-3.3-70b-versatile"
