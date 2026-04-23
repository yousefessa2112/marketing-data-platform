# Marketing Data Platform

## What this project is

This repository is a complete end-to-end marketing analytics project built to answer a very practical business question: *where is budget working, and where is it leaking?* It takes campaign-level performance data from multiple channels and turns it into outputs that are actually useful for decision-making, not just raw tables.

At a business level, this project is about creating trust in performance reporting. Instead of disconnected spreadsheets, it provides one consistent flow from daily raw records to cleaned metrics, modeled data, SQL analysis, interactive dashboards, and stakeholder-ready presentation material.

## What it does

The flow is straightforward: raw marketing data comes in first, gets cleaned and validated, then lands in SQLite for analysis. From there, SQL and Python transformations produce channel and campaign insights, and the final outputs are pushed into Plotly dashboards and Power BI-ready exports.

So the full path is: **raw marketing data -> cleaning and quality checks -> database load -> SQL/Python analysis -> dashboards and reporting artifacts**.

## The data

The project tracks **5 marketing channels** across a **6-month-style campaign window** with **900 total records**. Each record captures the core paid-performance metrics:

- `impressions`
- `clicks`
- `cost`
- `conversions`
- derived efficiency metrics: `ctr`, `cpc`, `cpa`

Channels included:
- `Search_Google`
- `Social_FB`
- `Social_IG`
- `Display_Programmatic`
- `Email_Newsletter`

## Key findings from the analysis

- **Search_Google** is the top spender at about **$164K** total spend (`$164,215.96`).
- The **highest CTR** is **3.96%**, led by **Search_Google**.
- **Email_Newsletter** is the most cost-efficient conversion channel, with best overall **CPA of $7.56** (weighted CPA).

## Dashboards

The project ships four interactive dashboards plus a hub page:

- `dashboard/marketing_dashboard.html`: executive overview of spend, conversion, and core KPIs.
- `dashboard/channel_performance.html`: side-by-side channel deep dive for efficiency and volume comparisons.
- `dashboard/trends_analysis.html`: trend and pattern view across time (daily/weekly/monthly behavior).
- `dashboard/efficiency_report.html`: CPA/CPC-focused performance and optimization lens.
- `dashboard/index.html`: central hub page that links everything together.

## Tech stack used

- **Python** for orchestration and automation
- **pandas** for core transformations and metric engineering
- **PySpark** for scalable processing patterns
- **SQL** for analytical querying and modeling logic
- **SQLite** as the local analytical warehouse
- **Plotly** for interactive dashboard outputs
- **python-pptx** for presentation generation

## How to run it

```bash
python3 -m pip install -r requirements.txt
python3 scripts/run_pipeline.py
```

Then open the dashboard hub at `dashboard/index.html`.

## Project structure

- `README.md` - project overview and business narrative.
- `requirements.txt` - Python dependency list for the pipeline and outputs.
- `.gitignore` - excludes local/cache and regenerated pipeline artifacts.

- `config/pipeline_config.yaml` - runtime configuration, paths, and environment toggles.

- `scripts/generate_data.py` - builds synthetic multi-channel campaign data.
- `scripts/clean_data.py` - cleans raw data and computes CTR/CPC/CPA fields.
- `scripts/data_quality.py` - runs quality checks and writes a QA report.
- `scripts/load_data.py` - loads cleaned data into SQLite tables.
- `scripts/run_analysis.py` - executes SQL analysis/modeling scripts and prints sample results.
- `scripts/pyspark_processing.py` - Spark-based transformation path and parquet output.
- `scripts/generate_dashboard.py` - creates all Plotly dashboard HTML pages plus the hub.
- `scripts/export_for_powerbi.py` - creates Power BI-friendly CSV and Excel export tables.
- `scripts/generate_presentation.py` - builds the final stakeholder presentation deck.
- `scripts/pipeline_logger.py` - logs per-step run status, duration, and row counts.
- `scripts/run_pipeline.py` - end-to-end orchestrator for the full project flow.
- `scripts/test_pipeline.py` - test suite for core pipeline behavior and outputs.

- `sql/analysis.sql` - core campaign and performance analysis queries.
- `sql/advanced_analysis.sql` - advanced SQL patterns (CTEs, windows, ranking, rolling metrics).
- `sql/data_models.sql` - star-schema-style data model and load statements.

- `data/raw_campaign_data.csv` - raw campaign input data.
- `data/clean_campaign_data.csv` - cleaned and enriched analytical dataset.
- `data/powerbi_export/campaign_daily_detail.csv` - detailed table for BI exploration.
- `data/powerbi_export/campaign_summary.csv` - campaign-level aggregated summary.
- `data/powerbi_export/monthly_trends.csv` - month-level trends and growth indicators.
- `data/powerbi_export/powerbi_ready_tables.xlsx` - multi-sheet workbook for easy BI import.

- `dashboard/index.html` - dashboard hub/landing page.
- `dashboard/marketing_dashboard.html` - executive KPI dashboard.
- `dashboard/channel_performance.html` - channel-level comparison dashboard.
- `dashboard/trends_analysis.html` - time-based trends dashboard.
- `dashboard/efficiency_report.html` - efficiency-focused dashboard.
- `dashboard/Marketing_Data_Pipeline_Presentation.pptx` - stakeholder presentation deck.

- `docs/cloud_architecture.md` - cloud deployment concept and architecture mapping.
