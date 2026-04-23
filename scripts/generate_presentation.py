from __future__ import annotations

import sqlite3
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "marketing.db"
OUTPUT_PATH = PROJECT_ROOT / "dashboard" / "Marketing_Data_Pipeline_Presentation.pptx"

NAVY = RGBColor(13, 27, 62)
TEAL = RGBColor(0, 134, 173)
LIGHT_BG = RGBColor(245, 248, 252)
ACCENT = RGBColor(255, 166, 43)
TEXT_DARK = RGBColor(36, 46, 66)
WHITE = RGBColor(255, 255, 255)


def query_data() -> dict[str, object]:
    with sqlite3.connect(DB_PATH) as conn:
        total_cost = conn.execute("SELECT ROUND(SUM(cost), 2) FROM campaign_performance;").fetchone()[0]
        total_clicks = conn.execute("SELECT SUM(clicks) FROM campaign_performance;").fetchone()[0]
        total_conversions = conn.execute("SELECT SUM(conversions) FROM campaign_performance;").fetchone()[0]
        total_impressions = conn.execute("SELECT SUM(impressions) FROM campaign_performance;").fetchone()[0]

        highest_cost = conn.execute(
            """
            SELECT campaign_id, ROUND(SUM(cost), 2) AS total_cost
            FROM campaign_performance
            GROUP BY campaign_id
            ORDER BY total_cost DESC
            LIMIT 1;
            """
        ).fetchone()

        highest_ctr = conn.execute(
            """
            SELECT campaign_id, ROUND(AVG(ctr) * 100, 2) AS avg_ctr_percent
            FROM campaign_performance
            GROUP BY campaign_id
            ORDER BY avg_ctr_percent DESC
            LIMIT 1;
            """
        ).fetchone()

        lowest_cpa = conn.execute(
            """
            SELECT campaign_id, ROUND(AVG(cpa), 2) AS avg_cpa
            FROM campaign_performance
            GROUP BY campaign_id
            ORDER BY avg_cpa ASC
            LIMIT 1;
            """
        ).fetchone()

    return {
        "total_cost": float(total_cost or 0),
        "total_clicks": int(total_clicks or 0),
        "total_conversions": int(total_conversions or 0),
        "total_impressions": int(total_impressions or 0),
        "highest_cost": highest_cost,
        "highest_ctr": highest_ctr,
        "lowest_cpa": lowest_cpa,
    }


def add_title(slide, title: str, subtitle: str | None = None) -> None:
    title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.35), Inches(12.0), Inches(0.9))
    tf = title_box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.font.name = "Calibri"
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.1), Inches(11.7), Inches(0.6))
        stf = sub_box.text_frame
        stf.clear()
        sp = stf.paragraphs[0]
        sp.text = subtitle
        sp.font.size = Pt(18)
        sp.font.color.rgb = TEAL
        sp.font.name = "Calibri"


def add_bg(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_bullets(slide, items: list[str], x: float, y: float, w: float, h: float, font_size: int = 18) -> None:
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.font.size = Pt(font_size)
        p.font.name = "Calibri"
        p.font.color.rgb = TEXT_DARK


def add_code_box(slide, code: str, x: float, y: float, w: float, h: float) -> None:
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(26, 35, 52)
    shape.line.color.rgb = TEAL
    tf = shape.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = code
    p.font.name = "Consolas"
    p.font.size = Pt(12)
    p.font.color.rgb = WHITE


def make_presentation() -> None:
    stats = query_data()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    layout = prs.slide_layouts[6]

    # 1) Title
    s1 = prs.slides.add_slide(layout)
    add_bg(s1, NAVY)
    tbox = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.8), Inches(1.4))
    tf = tbox.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Multi-Channel Marketing Data Pipeline"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Calibri"
    p.alignment = PP_ALIGN.CENTER
    sbox = s1.shapes.add_textbox(Inches(1.6), Inches(3.7), Inches(10.3), Inches(0.9))
    stf = sbox.text_frame
    sp = stf.paragraphs[0]
    sp.text = "From raw campaign data to SQL insights and an interactive dashboard"
    sp.font.size = Pt(22)
    sp.font.color.rgb = ACCENT
    sp.font.name = "Calibri"
    sp.alignment = PP_ALIGN.CENTER

    # 2) Project objective
    s2 = prs.slides.add_slide(layout)
    add_bg(s2, LIGHT_BG)
    add_title(s2, "What this project is about", "Objective and problem solved")
    add_bullets(
        s2,
        [
            "Marketing teams collect campaign metrics from multiple channels, but the data is often fragmented and hard to compare.",
            "This project builds one consistent pipeline that ingests campaign data, cleans it, stores it centrally, and produces analysis-ready outputs.",
            "The goal is fast, repeatable answers to budget, engagement, and efficiency questions without manual spreadsheet work.",
        ],
        0.9,
        1.8,
        12.0,
        4.8,
        20,
    )

    # 3) Tools used
    s3 = prs.slides.add_slide(layout)
    add_bg(s3, WHITE)
    add_title(s3, "Tools used in this pipeline")
    cards = [
        ("Python", "Orchestrates each pipeline step and automation scripts."),
        ("pandas", "Cleans, validates, transforms, and enriches campaign records."),
        ("SQLite", "Stores cleaned data in a lightweight, queryable database."),
        ("SQL", "Answers business questions on cost, CTR trends, and CPA."),
        ("Plotly", "Builds interactive KPI and trend dashboard visuals."),
    ]
    x = 0.8
    for idx, (tool, desc) in enumerate(cards):
        if idx and idx % 3 == 0:
            x = 0.8
        row = idx // 3
        y = 1.7 + (row * 2.5)
        w = 4.1
        h = 2.0
        card = s3.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT_BG
        card.line.color.rgb = TEAL
        ctf = card.text_frame
        ctf.clear()
        p1 = ctf.paragraphs[0]
        p1.text = tool
        p1.font.bold = True
        p1.font.size = Pt(20)
        p1.font.color.rgb = NAVY
        p2 = ctf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(6)
        x += 4.3

    # 4) Data overview
    s4 = prs.slides.add_slide(layout)
    add_bg(s4, LIGHT_BG)
    add_title(s4, "The data we work with")
    add_bullets(
        s4,
        [
            "Daily performance data for 5 campaign channels: Search_Google, Social_FB, Social_IG, Display_Programmatic, Email_Newsletter.",
            "Core fields: impressions, clicks, cost, conversions, and date.",
            f"Dataset scale: {stats['total_impressions']:,} impressions, {stats['total_clicks']:,} clicks, {stats['total_conversions']:,} conversions, ${stats['total_cost']:,.2f} spend.",
            "This gives enough volume to compare channel efficiency and trend behavior over time.",
        ],
        0.9,
        1.8,
        12.0,
        4.8,
    )

    # 5) Pipeline flow
    s5 = prs.slides.add_slide(layout)
    add_bg(s5, WHITE)
    add_title(s5, "Pipeline flow")
    flow = ["Raw Data", "Cleaning", "Database", "Analysis", "Dashboard"]
    x = 0.7
    for i, label in enumerate(flow):
        box = s5.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE, Inches(x), Inches(3.0), Inches(2.2), Inches(1.2))
        box.fill.solid()
        box.fill.fore_color.rgb = NAVY if i % 2 == 0 else TEAL
        box.line.color.rgb = WHITE
        tf = box.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = label
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER
        if i < len(flow) - 1:
            arrow = s5.shapes.add_shape(
                MSO_AUTO_SHAPE_TYPE.RIGHT_ARROW, Inches(x + 2.25), Inches(3.3), Inches(0.55), Inches(0.5)
            )
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = ACCENT
            arrow.line.color.rgb = ACCENT
        x += 2.55
    add_code_box(
        s5,
        "python3 scripts/run_pipeline.py\n# runs: generate -> clean -> load -> analyze -> dashboard",
        2.6,
        4.8,
        8.1,
        1.5,
    )

    # 6) Data cleaning
    s6 = prs.slides.add_slide(layout)
    add_bg(s6, LIGHT_BG)
    add_title(s6, "Data cleaning and feature engineering")
    add_bullets(
        s6,
        [
            "Removed nulls and duplicates to avoid distorted metrics and double counting.",
            "Converted date and numeric fields into consistent types for reliable analysis.",
            "Calculated CTR = clicks/impressions, CPC = cost/clicks, CPA = cost/conversions.",
            "CTR shows engagement, CPC shows traffic acquisition cost, CPA shows conversion efficiency.",
        ],
        0.8,
        1.7,
        6.1,
        4.8,
    )
    add_code_box(
        s6,
        "df['ctr'] = (df['clicks'] / df['impressions']).round(6)\n"
        "df['cpc'] = (df['cost'] / df['clicks']).round(4)\n"
        "df['cpa'] = (df['cost'] / df['conversions']).round(4)",
        7.0,
        2.1,
        5.6,
        2.3,
    )

    # 7) Database
    s7 = prs.slides.add_slide(layout)
    add_bg(s7, WHITE)
    add_title(s7, "SQLite storage design")
    add_bullets(
        s7,
        [
            "Cleaned data is loaded into SQLite table: campaign_performance.",
            "The table acts as the analytical source of truth for SQL reporting.",
        ],
        0.8,
        1.7,
        5.8,
        1.6,
    )
    add_code_box(
        s7,
        "CREATE TABLE campaign_performance (\n"
        "  date TEXT,\n"
        "  campaign_id TEXT,\n"
        "  impressions INTEGER,\n"
        "  clicks INTEGER,\n"
        "  cost REAL,\n"
        "  conversions INTEGER,\n"
        "  ctr REAL,\n"
        "  cpc REAL,\n"
        "  cpa REAL\n);",
        6.2,
        1.8,
        6.4,
        4.4,
    )

    # 8) SQL analysis and results
    s8 = prs.slides.add_slide(layout)
    add_bg(s8, LIGHT_BG)
    add_title(s8, "SQL analysis: key business questions + results")
    rows = [
        "1) Which campaign has the highest total cost?  Search_Google at $164,215.96",
        "2) Which campaign has the highest CTR?  Search_Google at 3.96%",
        "3) How do clicks trend over time?  Daily aggregate query shows a stable, seasonal-like pattern.",
        "4) Which campaign has the lowest average CPA?  Email_Newsletter at $8.11",
    ]
    add_bullets(s8, rows, 0.9, 1.8, 12.0, 3.2, 16)
    add_code_box(
        s8,
        "SELECT campaign_id, ROUND(SUM(cost),2) AS total_cost\nFROM campaign_performance\n"
        "GROUP BY campaign_id\nORDER BY total_cost DESC;",
        0.9,
        5.0,
        6.0,
        1.6,
    )
    add_code_box(
        s8,
        "SELECT campaign_id, ROUND(AVG(cpa),2) AS avg_cpa\nFROM campaign_performance\n"
        "GROUP BY campaign_id\nORDER BY avg_cpa ASC;",
        7.0,
        5.0,
        5.6,
        1.6,
    )

    # 9) Dashboard
    s9 = prs.slides.add_slide(layout)
    add_bg(s9, WHITE)
    add_title(s9, "Interactive dashboard output")
    add_bullets(
        s9,
        [
            "KPI cards: Average CTR and Average CPA for quick executive visibility.",
            "Line chart: total clicks by date to monitor trend movement.",
            "Bar chart: campaign cost comparison to highlight budget concentration.",
            "Delivered as HTML via Plotly for interactive exploration and filtering.",
        ],
        0.9,
        1.8,
        7.4,
        4.8,
    )
    panel = s9.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, Inches(8.1), Inches(2.0), Inches(4.8), Inches(3.9))
    panel.fill.solid()
    panel.fill.fore_color.rgb = LIGHT_BG
    panel.line.color.rgb = TEAL
    ptf = panel.text_frame
    ptf.clear()
    p = ptf.paragraphs[0]
    p.text = "Dashboard\n\n- Avg CTR card\n- Avg CPA card\n- Clicks trend line\n- Campaign cost bar"
    p.font.size = Pt(16)
    p.font.color.rgb = NAVY

    # 10) Automation
    s10 = prs.slides.add_slide(layout)
    add_bg(s10, LIGHT_BG)
    add_title(s10, "Pipeline automation")
    add_bullets(
        s10,
        [
            "One command executes every stage end-to-end, from data generation to dashboard output.",
            "This makes the workflow repeatable, fast to demo, and simple to maintain.",
            "Each step is modular (generate, clean, load, analyze, visualize) for easy extension.",
        ],
        0.9,
        1.8,
        12.0,
        2.8,
    )
    add_code_box(
        s10,
        "python3 scripts/run_pipeline.py\n\n# executes:\n# generate_data.py -> clean_data.py -> load_data.py\n# -> run_analysis.py -> generate_dashboard.py",
        2.0,
        4.0,
        9.3,
        2.3,
    )

    # 11) Insights
    s11 = prs.slides.add_slide(layout)
    add_bg(s11, WHITE)
    add_title(s11, "Key insights from the data")
    add_bullets(
        s11,
        [
            "Search_Google drives the largest spend and strongest CTR, making it a high-volume performance engine.",
            "Email_Newsletter delivers the most efficient acquisition cost (lowest CPA), indicating high conversion efficiency.",
            "Display_Programmatic has the weakest CTR and highest CPA, suggesting creative or targeting optimization is needed.",
            "Cross-channel visibility helps rebalance budget toward both scale (Search) and efficiency (Email).",
        ],
        0.9,
        1.8,
        12.0,
        4.8,
    )

    # 12) Conclusion
    s12 = prs.slides.add_slide(layout)
    add_bg(s12, NAVY)
    add_title(s12, "Summary & conclusion", "Reliable pipeline, clear metrics, actionable insights")
    for shp in s12.shapes:
        if hasattr(shp, "text_frame"):
            for paragraph in shp.text_frame.paragraphs:
                paragraph.font.color.rgb = WHITE
    add_bullets(
        s12,
        [
            "This project demonstrates a complete marketing analytics flow from ingestion to decision-ready dashboarding.",
            "The same architecture can be scaled to real ad platform exports and scheduled production runs.",
            "Outcome: cleaner reporting, faster analysis, and better budget decisions across channels.",
        ],
        0.9,
        2.0,
        12.0,
        3.8,
        19,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_PATH))
    print(f"Presentation generated at: {OUTPUT_PATH}")


if __name__ == "__main__":
    make_presentation()