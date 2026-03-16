"""
chart_utils.py
──────────────
Plotly chart helpers:
  - style_fig              → applies the DataLens theme to any Plotly figure
  - add_annotations_to_fig → overlays user annotations
  - make_sparkline_svg     → tiny inline SVG sparklines for the stats table
  - render_nl_chart        → renders a chart from an AI-generated spec dict
  - empty_state            → returns HTML for an empty-state placeholder
  - ai_card_html           → returns HTML for the AI response card
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ── Plotly theme ─────────────────────────────────────────────────────────────

def style_fig(fig, T, COLORS):
    """Apply the DataLens visual theme to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=T["plot_bg"],
        font=dict(family="DM Sans", color=T["text"], size=11),
        title_font=dict(family="Syne", size=15, color=T["text_head"]),
        colorway=COLORS,
        xaxis=dict(
            gridcolor=T["grid"], linecolor=T["line"], zeroline=False,
            tickfont=dict(family="DM Mono", size=9, color=T["tick"]),
            title_font=dict(family="DM Mono", size=9, color=T["tick"]),
        ),
        yaxis=dict(
            gridcolor=T["grid"], linecolor=T["line"], zeroline=False,
            tickfont=dict(family="DM Mono", size=9, color=T["tick"]),
            title_font=dict(family="DM Mono", size=9, color=T["tick"]),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Mono", size=9, color=T["tick"]),
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        ),
        margin=dict(l=8, r=8, t=48, b=8),
        hoverlabel=dict(
            bgcolor=T["card"], font_family="DM Mono",
            font_size=11, bordercolor=T["accent_glow"],
        ),
    )
    return fig


# ── Annotations ──────────────────────────────────────────────────────────────

def add_annotations_to_fig(fig, annotations, T):
    """Overlay user-defined annotations on a Plotly figure."""
    for ann in annotations:
        fig.add_annotation(
            x=ann.get("x", 0.5), y=ann.get("y", 0.5),
            xref=ann.get("xref", "paper"), yref=ann.get("yref", "paper"),
            text=f"◈ {ann['text']}",
            showarrow=ann.get("arrow", True),
            arrowhead=2, arrowcolor=T["accent"], arrowwidth=1.5,
            font=dict(family="DM Sans", size=11, color=T["text_head"]),
            bgcolor=T["card"], bordercolor=T["accent"], borderwidth=1, borderpad=6,
        )
    return fig


# ── Sparklines ───────────────────────────────────────────────────────────────

def make_sparkline_svg(values, color, w: int = 80, h: int = 24) -> str:
    """Generate a tiny inline SVG polyline sparkline from a list of numeric values."""
    try:
        vals = [float(v) for v in values if pd.notna(v)]
        if len(vals) < 2:
            return ""
        mn, mx = min(vals), max(vals)
        rng = mx - mn or 1
        pts = []
        for i, v in enumerate(vals):
            x = round(i / (len(vals) - 1) * w, 1)
            y = round(h - (v - mn) / rng * (h - 4) - 2, 1)
            pts.append(f"{x},{y}")
        return (
            f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'style="display:block;overflow:visible;">'
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
            f'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
            f'</svg>'
        )
    except Exception:
        return ""


# ── HTML helpers ─────────────────────────────────────────────────────────────

def empty_state(icon: str, title: str, sub: str) -> str:
    return (
        f'<div class="empty-state">'
        f'<div class="empty-state-icon">{icon}</div>'
        f'<div class="empty-state-title">{title}</div>'
        f'<div class="empty-state-sub">{sub}</div>'
        f'</div>'
    )


def ai_card_html(label: str, text: str) -> str:
    escaped   = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_text = text.replace("`", "'").replace('"', "'")
    return (
        f'<div class="ai-card">'
        f'<div class="ai-card-header">'
        f'<div class="ai-card-label">◈ {label}</div>'
        f'<span class="ai-copy-btn" onclick="navigator.clipboard.writeText(`{safe_text}`);\
this.innerText=\'Copied ✓\';setTimeout(()=>this.innerText=\'Copy\',1500)">Copy</span>'
        f'</div>'
        f'<div class="ai-card-text">{escaped}</div>'
        f'</div>'
    )


# ── Natural-language chart renderer ──────────────────────────────────────────

def render_nl_chart(spec: dict, df, T, COLORS, accent, annotations):
    """
    Render a Plotly figure from an AI-generated chart spec dict.
    Returns (fig, None) on success or (None, error_string) on failure.
    """
    ct    = spec.get("chart_type", "bar")
    x     = spec.get("x")
    y     = spec.get("y")
    color = spec.get("color")
    agg   = spec.get("aggregation", "none")
    title = spec.get("title", "Chart")

    # Validate that all column references actually exist
    all_cols = list(df.columns)
    if x     and x     not in all_cols: x     = None
    if y     and y     not in all_cols: y     = None
    if color and color not in all_cols: color = None

    plot_df = df.copy()

    # Aggregate when explicitly requested
    if agg != "none" and x and y:
        fn_map = {"mean": "mean", "sum": "sum", "count": "count", "median": "median"}
        fn = fn_map.get(agg, "mean")
        group_cols = [x] + ([color] if color else [])
        try:
            plot_df = df.groupby(group_cols)[y].agg(fn).reset_index()
        except Exception:
            plot_df = df.copy()
    # agg=none + raw data → auto-sum to avoid overplotting
    elif agg == "none" and x and y and x in df.columns and y in df.columns:
        x_unique = df[x].nunique()
        n_rows   = len(df)
        if x_unique < n_rows and pd.api.types.is_numeric_dtype(df[y]):
            try:
                group_cols = [x] + ([color] if color else [])
                plot_df = df.groupby(group_cols)[y].sum().reset_index()
            except Exception:
                plot_df = df.copy()

    try:
        if ct == "bar":
            if x and y:
                fig = px.bar(plot_df, x=x, y=y, color=color, title=title,
                             color_discrete_sequence=COLORS)
                if not color:
                    fig.update_traces(marker_color=accent, marker_line_width=0)
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
                if not color:
                    fig.update_traces(line_color=accent, line_width=2)
            else:
                return None, "Line chart needs X and Y columns."

        elif ct == "scatter":
            if x and y:
                fig = px.scatter(
                    plot_df, x=x, y=y, color=color, title=title,
                    opacity=0.72, color_discrete_sequence=COLORS,
                    trendline="ols" if not color else None,
                )
                if not color:
                    fig.update_traces(marker=dict(color=accent, size=6))
            else:
                return None, "Scatter plot needs X and Y columns."

        elif ct == "histogram":
            col = x or y
            if not col:
                return None, "Histogram needs a column."
            fig = px.histogram(plot_df, x=col, color=color, title=title,
                               nbins=30, barmode="overlay", opacity=0.85,
                               color_discrete_sequence=COLORS)
            if not color:
                fig.update_traces(marker_color=accent)

        elif ct == "box":
            col = y or x
            if not col:
                return None, "Box plot needs a column."
            fig = px.box(plot_df, y=col, x=color, color=color, title=title,
                         color_discrete_sequence=COLORS, points="outliers")
            if not color:
                fig.update_traces(marker_color=accent, line_color=T["blue"])

        elif ct == "violin":
            col = y or x
            if not col:
                return None, "Violin plot needs a column."
            fig = px.violin(plot_df, y=col, x=color, color=color, title=title,
                            box=True, color_discrete_sequence=COLORS)
            if not color:
                fig.update_traces(fillcolor=T["accent_glow"], line_color=accent)

        elif ct == "pie":
            # AI can return the category in x, y, or color — find it by dtype
            candidates = [c for c in [x, y, color] if c and c in plot_df.columns]
            name_col   = None
            value_col  = None
            for c in candidates:
                if not pd.api.types.is_numeric_dtype(plot_df[c]):
                    name_col = name_col or c
                elif value_col is None:
                    value_col = c
            if not name_col and candidates:
                name_col  = candidates[0]
                value_col = candidates[1] if len(candidates) > 1 else None

            if name_col:
                if value_col and value_col in plot_df.columns:
                    agg_df = plot_df.groupby(name_col)[value_col].sum().reset_index()
                    fig = px.pie(agg_df, names=name_col, values=value_col,
                                 title=title, color_discrete_sequence=COLORS, hole=0.3)
                else:
                    vc = plot_df[name_col].value_counts().reset_index()
                    vc.columns = [name_col, "count"]
                    fig = px.pie(vc, names=name_col, values="count",
                                 title=title, color_discrete_sequence=COLORS, hole=0.3)
                fig.update_traces(textfont=dict(family="DM Mono", size=10))
            else:
                return None, "Pie chart needs a category column. Try mentioning a specific column name."

        elif ct == "area":
            if x and y:
                fig = px.area(plot_df, x=x, y=y, color=color, title=title,
                              color_discrete_sequence=COLORS)
                if not color:
                    fig.update_traces(line_color=accent, fillcolor=T["accent_glow"])
            else:
                return None, "Area chart needs X and Y columns."

        else:
            return None, f"Unknown chart type: {ct}"

        return style_fig(add_annotations_to_fig(fig, annotations, T), T, COLORS), None

    except Exception as e:
        return None, f"Could not render chart: {e}"
