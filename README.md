# Marketing Data Platform

End-to-end multi-channel marketing data pipeline using synthetic campaign data, Python ETL, SQLite analysis, and a Plotly dashboard.

## Project Overview

This project simulates a complete marketing analytics workflow:
- Generates realistic campaign performance data across social, search, display, and email channels
- Cleans and enriches raw records with performance metrics (CTR, CPC, CPA)
- Loads clean records into SQLite
- Runs SQL analyses for spend, engagement, trend, and efficiency insights
- Produces an interactive dashboard for KPI monitoring

## Tools Used

- Python 3.11
- pandas, numpy
- SQLite (`sqlite3`)
- Plotly
- SQL

## Folder Structure

- `data/` - raw CSV, cleaned CSV, SQLite database
- `scripts/` - data generation, ETL, analysis runner, dashboard generator, full pipeline runner
- `sql/` - analysis queries
- `dashboard/` - generated HTML dashboard

## Data Flow Diagram (Text-Based)

`Synthetic Raw CSV (data/raw_campaign_data.csv)`
-> `Clean + Enrich (scripts/clean_data.py)`
-> `Clean CSV (data/clean_campaign_data.csv)`
-> `Load to SQLite (scripts/load_data.py)`
-> `SQL Analysis (sql/analysis.sql via scripts/run_analysis.py)`
-> `Dashboard HTML (scripts/generate_dashboard.py -> dashboard/marketing_dashboard.html)`

## How to Run

Install dependencies:

```bash
python3 -m pip install pandas numpy plotly
```

Run full pipeline:

```bash
python3 scripts/run_pipeline.py
```

Run steps individually:

```bash
python3 scripts/generate_data.py
python3 scripts/clean_data.py
python3 scripts/load_data.py
python3 scripts/run_analysis.py
python3 scripts/generate_dashboard.py
```

## Insights Produced

- Which campaigns consume the highest total budget
- Which campaigns have the strongest click-through rates
- How click volume trends over time
- Average acquisition efficiency (CPA) by campaign

## Output Artifacts

- `data/raw_campaign_data.csv`
- `data/clean_campaign_data.csv`
- `data/marketing.db`
- `dashboard/marketing_dashboard.html`
