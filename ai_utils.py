"""
ai_utils.py
───────────
All Groq / LLM API calls:
  - get_ai_insights   → free-text dataset analysis
  - build_summary     → compact JSON summary fed to the LLM
  - nl_to_chart_spec  → natural-language → chart spec JSON
"""

import json
import requests
import streamlit as st

GROQ_MODEL  = "llama-3.3-70b-versatile"
GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"


# ── Dataset summary ──────────────────────────────────────────────────────────

def build_summary(df) -> str:
    """Return a compact JSON string describing the dataset for the LLM."""
    nd = df.select_dtypes(include="number")
    cd = df.select_dtypes(include="object")
    return json.dumps({
        "shape":            list(df.shape),
        "columns":          list(df.columns),
        "numeric_stats":    nd.describe().round(2).to_dict() if len(nd.columns) > 0 else {},
        "categorical_top":  {c: df[c].value_counts().head(3).to_dict() for c in cd.columns[:4]},
        "missing":          df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
    }, default=str)


# ── AI insights (text) ───────────────────────────────────────────────────────

@st.cache_data(show_spinner=False, ttl=300)
def get_ai_insights(data_json: str, question: str = "") -> str:
    """
    Call the Groq LLM to analyse a dataset summary.
    Returns a plain-text analysis string (or an error/setup message).
    """
    prompt = (
        "You are a senior data analyst. Analyze this dataset concisely and professionally.\n"
        f"Dataset: {data_json}\n"
        f"{'Question: ' + question if question else 'Give 4-5 key insights: patterns, outliers, distributions, findings. Use specific numbers. Be direct.'}\n"
        "Format: numbered points, plain language, no filler."
    )
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return (
            "⚠️ No Groq API key found.\n\nSetup (free, 2 mins):\n"
            "1. Sign up at console.groq.com\n"
            "2. Create API key\n"
            "3. Streamlit Cloud → Settings → Secrets:\n"
            '   GROQ_API_KEY = "your-key"'
        )
    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model":       GROQ_MODEL,
                "messages":    [{"role": "user", "content": prompt}],
                "max_tokens":  800,
                "temperature": 0.3,
            },
            timeout=20,
        )
        d = r.json()
        if "choices" in d:
            return d["choices"][0]["message"]["content"]
        return f"Groq error: {d.get('error', {}).get('message', str(d))}"
    except requests.exceptions.Timeout:
        return "Request timed out. Try again."
    except Exception as e:
        return f"Could not reach Groq: {e}"


# ── Natural-language → chart spec ────────────────────────────────────────────

def nl_to_chart_spec(
    user_request: str,
    df_columns:   list,
    numeric_cols: list,
    cat_cols:     list,
) -> dict:
    """
    Ask the LLM to convert a natural-language chart request into a structured
    chart spec dict with keys: chart_type, x, y, color, aggregation, title, error.

    Includes post-processing to auto-correct common LLM mistakes (swapped axes,
    wrong column types, hallucinated column names).
    """
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return {"error": "no_key"}

    col_info = (
        f"Categorical columns (text/labels, use for slices/groups/x-axis): {cat_cols}\n"
        f"Numeric columns (numbers, use for sizes/values/y-axis): {numeric_cols}\n"
        f"All columns: {df_columns}"
    )

    prompt = f"""You are a data visualization assistant. Return ONLY a valid JSON object — no explanation, no markdown, no backticks.

{col_info}

User request: "{user_request}"

STRICT RULES — follow exactly:
- "chart_type": one of: bar, line, scatter, histogram, box, pie, violin, area
- "x": MUST be a categorical column name for bar/pie/box/violin, or numeric for scatter/histogram. null if not needed.
- "y": MUST always be a numeric column name, or null.
- "color": optional categorical column for grouping, or null.
- "aggregation": one of: sum, mean, median, count, none. Use "count" when no numeric value column exists. Use "none" only for scatter or pre-aggregated data.
- "title": short descriptive title
- "error": null, or brief message if request cannot be fulfilled

FOR PIE CHARTS specifically:
- "x" MUST be a categorical column (the slices)
- "y" MUST be a numeric column (slice size) or null if counting
- NEVER put a categorical column in "y"

Only use column names that exist exactly in the lists above. Return ONLY the JSON."""

    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model":       GROQ_MODEL,
                "messages":    [{"role": "user", "content": prompt}],
                "max_tokens":  300,
                "temperature": 0.1,
            },
            timeout=15,
        )
        d = r.json()
        if "choices" not in d:
            return {"error": d.get("error", {}).get("message", "API error")}

        raw = d["choices"][0]["message"]["content"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        spec = json.loads(raw)

        # ── Post-process: validate and auto-correct ──────────────────────
        ct = spec.get("chart_type", "bar")

        def valid_col(c):
            return c if c and c in df_columns else None

        spec["x"]     = valid_col(spec.get("x"))
        spec["y"]     = valid_col(spec.get("y"))
        spec["color"] = valid_col(spec.get("color"))

        # Pie: x must be categorical, y must be numeric or null
        if ct == "pie":
            x, y = spec.get("x"), spec.get("y")
            if x in numeric_cols and y in cat_cols:
                spec["x"], spec["y"] = y, x
            elif x in numeric_cols and not y:
                spec["y"] = spec["x"]
                spec["x"] = cat_cols[0] if cat_cols else None
            elif not x:
                for candidate in [spec.get("color"), spec.get("y")]:
                    if candidate and candidate in cat_cols:
                        spec["x"] = candidate
                        if candidate == spec.get("y"):    spec["y"]     = None
                        if candidate == spec.get("color"): spec["color"] = None
                        break

        # Bar / box / violin: x should be categorical
        if ct in ("bar", "box", "violin"):
            x, y = spec.get("x"), spec.get("y")
            if x in numeric_cols and y in cat_cols:
                spec["x"], spec["y"] = y, x

        # Scatter / line: both axes should ideally be numeric
        if ct in ("scatter", "line"):
            if spec.get("x") in cat_cols and not spec.get("y"):
                spec["y"] = numeric_cols[0] if numeric_cols else None

        return spec

    except json.JSONDecodeError:
        return {"error": "Could not parse AI response. Try rephrasing your request."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Try again."}
    except Exception as e:
        return {"error": str(e)}
