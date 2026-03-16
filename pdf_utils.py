"""
pdf_utils.py
────────────
PDF report generation using ReportLab.
Exports a formatted report with dataset overview, column health,
numeric statistics, cleaning log, and AI insights.
"""

import io
import datetime
import streamlit as st


def generate_pdf_report(
    df,
    filename:     str,
    ai_text:      str,
    clean_report: list,
) -> bytes | None:
    """
    Build a PDF report for the given DataFrame.

    Returns the PDF as bytes on success, or None if ReportLab is not installed.
    Displays a Streamlit error on unexpected failures.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units    import mm
        from reportlab.lib          import colors
        from reportlab.platypus     import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable, PageBreak,
        )
        from reportlab.lib.styles import ParagraphStyle

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=20 * mm, rightMargin=20 * mm,
            topMargin=18 * mm, bottomMargin=18 * mm,
        )

        # ── Colour palette ──────────────────────────────────────────────
        BG     = colors.HexColor("#0a0a0f")
        CARD   = colors.HexColor("#0f0f18")
        ACCENT = colors.HexColor("#ff5a32")
        TEXT   = colors.HexColor("#f0ece4")
        MUTED  = colors.HexColor("#6b6760")
        LINE   = colors.HexColor("#1e1e2a")
        BLUE   = colors.HexColor("#50b4ff")

        # ── Paragraph style factory ────────────────────────────────────
        def sty(name, **kw):
            base = dict(fontName="Helvetica", fontSize=10, textColor=TEXT, leading=14, spaceAfter=4)
            base.update(kw)
            return ParagraphStyle(name, **base)

        S_EY = sty("ey", fontSize=7,  textColor=ACCENT, fontName="Helvetica-Bold", leading=10)
        S_TI = sty("ti", fontSize=28, textColor=TEXT,   fontName="Helvetica-Bold", leading=30)
        S_MO = sty("mo", fontSize=8,  textColor=BLUE,   fontName="Courier",        leading=12)
        S_SE = sty("se", fontSize=7,  textColor=ACCENT, fontName="Helvetica-Bold", leading=10, spaceAfter=6)
        S_AI = sty("ai", fontSize=9,  textColor=colors.HexColor("#c8c4bc"),         leading=15)

        def HR():   return HRFlowable(width="100%", thickness=0.5, color=LINE, spaceAfter=10, spaceBefore=10)
        def SP(h=6): return Spacer(1, h)

        # ── Shared table style ─────────────────────────────────────────
        tbl_style = TableStyle([
            ("BACKGROUND",   (0, 0), (-1,  0), ACCENT),
            ("TEXTCOLOR",    (0, 0), (-1,  0), colors.white),
            ("FONTNAME",     (0, 0), (-1,  0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 8),
            ("BACKGROUND",   (0, 1), (-1, -1), CARD),
            ("TEXTCOLOR",    (0, 1), (-1, -1), TEXT),
            ("ROWBACKGROUNDS",(0,1), (-1, -1), [CARD, colors.HexColor("#111120")]),
            ("GRID",         (0, 0), (-1, -1), 0.3, LINE),
            ("LEFTPADDING",  (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ])

        nc   = df.select_dtypes(include="number").columns.tolist()
        cc   = df.select_dtypes(include="object").columns.tolist()
        miss = int(df.isnull().sum().sum())
        comp = round((1 - miss / max(df.size, 1)) * 100, 1)
        now  = datetime.datetime.now()

        # ── Cover page ─────────────────────────────────────────────────
        story = [
            SP(20),
            Paragraph("◈ SMART DATA EXPLORER", S_EY),
            SP(4),
            Paragraph("DataLens", S_TI),
            Paragraph("Analysis Report", sty("sub", fontSize=13, textColor=MUTED, leading=16)),
            SP(10), HR(),
            Paragraph(f"File: {filename}", S_MO),
            Paragraph(f"Generated: {now.strftime('%d %b %Y, %H:%M')}", S_MO),
            Paragraph(f"Rows: {df.shape[0]:,}   Columns: {df.shape[1]}", S_MO),
            HR(), SP(10),
        ]

        # ── Dataset overview table ─────────────────────────────────────
        story.append(Paragraph("DATASET OVERVIEW", S_SE))
        overview = Table(
            [
                ["Metric",            "Value"],
                ["Total rows",        f"{df.shape[0]:,}"],
                ["Total columns",     str(df.shape[1])],
                ["Numeric cols",      str(len(nc))],
                ["Categorical cols",  str(len(cc))],
                ["Missing values",    f"{miss:,}"],
                ["Completeness",      f"{comp}%"],
                ["Duplicate rows",    str(int(df.duplicated().sum()))],
            ],
            colWidths=[80 * mm, 80 * mm],
        )
        overview.setStyle(tbl_style)
        story += [overview, SP(16)]

        # ── Columns table ──────────────────────────────────────────────
        story.append(Paragraph("COLUMNS", S_SE))
        col_data = [["Column Name", "Type", "Nulls", "Unique"]]
        for col in df.columns:
            col_data.append([
                col[:35],
                str(df[col].dtype),
                str(int(df[col].isnull().sum())),
                str(df[col].nunique()),
            ])
        col_tbl = Table(col_data, colWidths=[75 * mm, 35 * mm, 25 * mm, 25 * mm])
        col_tbl.setStyle(tbl_style)
        story += [col_tbl, SP(16)]

        # ── Numeric statistics ─────────────────────────────────────────
        if nc:
            story += [PageBreak(), Paragraph("NUMERIC STATISTICS", S_SE)]
            stats = df[nc].describe().T.round(3)
            stats["median"] = df[nc].median().round(3)
            stats["skew"]   = df[nc].skew().round(3)
            keep  = ["count", "mean", "median", "std", "min", "max", "skew"]
            stats = stats[[c for c in keep if c in stats.columns]]
            hdr   = ["Column"] + list(stats.columns)
            sd    = [hdr] + [
                [str(rn)[:20]] + [
                    f"{v:,.3f}" if isinstance(v, float) else str(int(v))
                    for v in row
                ]
                for rn, row in stats.iterrows()
            ]
            st2 = Table(sd, colWidths=[50 * mm] + [18 * mm] * (len(hdr) - 1))
            st2.setStyle(tbl_style)
            story += [st2, SP(16)]

        # ── Cleaning log ───────────────────────────────────────────────
        if clean_report:
            story += [HR(), Paragraph("CLEANING APPLIED", S_SE)]
            for note in clean_report:
                story.append(Paragraph(f"✓  {note}", S_AI))

        # ── AI insights ────────────────────────────────────────────────
        story += [
            PageBreak(),
            Paragraph("AI INSIGHTS", S_SE),
            Paragraph("Powered by Llama 3.3 70B via Groq (free)", S_MO),
            SP(8),
        ]
        for line in ai_text.split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, S_AI))
                story.append(SP(3))

        # ── Footer ────────────────────────────────────────────────────
        story += [
            SP(20), HR(),
            Paragraph("Generated by DataLens · Smart Data Explorer", S_MO),
            Paragraph(f"Report date: {now.strftime('%d %B %Y')}", S_MO),
        ]

        doc.build(story)
        buf.seek(0)
        return buf.read()

    except ImportError:
        return None
    except Exception as e:
        st.error(f"PDF error: {e}")
        return None
