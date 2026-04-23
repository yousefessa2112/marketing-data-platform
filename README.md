# Marketing Data Platform

This project is built as a practical, interview-ready analytics story: take messy multi-channel marketing data and turn it into trusted, decision-ready outputs through a repeatable pipeline. It starts with raw daily campaign metrics, applies cleaning and enrichment, loads data into SQL, runs advanced analytical queries, and ships both dashboard and BI-ready outputs.

The dataset covers five channels (`Search_Google`, `Social_FB`, `Social_IG`, `Display_Programmatic`, `Email_Newsletter`) with impressions, clicks, cost, and conversions. From there, the pipeline computes CTR, CPC, and CPA, validates quality, and supports both pandas and PySpark processing to demonstrate local and scalable data engineering patterns.

## What this now demonstrates

- **Advanced SQL**: CTEs, window functions (`LAG`, `RANK`, rolling averages, cumulative sums), `CASE`, and subqueries in `sql/advanced_analysis.sql`.
- **Data modeling & schema design**: star schema with `fact_campaign_daily`, `dim_campaign`, `dim_channel`, `dim_date` in `sql/data_models.sql`.
- **Python ETL/ELT**: modular scripts for generation, cleaning, loading, analysis, quality checks, and exports.
- **Databricks/PySpark readiness**: Spark pipeline in `scripts/pyspark_processing.py` with schema definition, null handling, transformations, aggregations, and windows.
- **Testing and data quality**: quality checks logged to `data/quality_report.txt` and pytest coverage in `scripts/test_pipeline.py`.
- **Monitoring/logging**: pipeline run tracking (status, timings, rows, errors) in `data/pipeline_log.csv`.
- **Cloud awareness (Azure)**: deployment blueprint in `docs/cloud_architecture.md` (Blob Storage, Databricks/ADF, Azure SQL/Synapse, Power BI).
- **Power BI readiness**: curated CSV/Excel exports in `data/powerbi_export/`.
- **Communication layer**: interactive Plotly dashboard and updated presentation deck.

## Project structure

- `scripts/run_pipeline.py`: orchestrates the full flow.
- `scripts/pyspark_processing.py`: Spark-based transformation path (optional via config).
- `scripts/data_quality.py`: post-cleaning validation checks.
- `scripts/pipeline_logger.py`: centralized step-level logging.
- `scripts/export_for_powerbi.py`: BI-optimized outputs.
- `scripts/test_pipeline.py`: end-to-end unit/integration-style tests.
- `sql/analysis.sql`: core business analysis with CTEs/windows.
- `sql/advanced_analysis.sql`: advanced analyst SQL showcase.
- `sql/data_models.sql`: dimensional model DDL + load SQL.
- `config/pipeline_config.yaml`: central config (paths, settings, cloud placeholders).
- `docs/cloud_architecture.md`: Azure deployment concept.

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 scripts/run_pipeline.py
```

The pipeline runs:

`generate_data -> clean_data -> data_quality -> load_data -> SQL analysis/modeling -> optional PySpark -> dashboard -> Power BI export -> presentation`

Note: PySpark requires a local Java runtime (Java 11+). If Java is missing, the pipeline safely skips Spark execution and writes a marker file in `data/output/campaign_daily_parquet/`.

## Tests

```bash
pytest -q scripts/test_pipeline.py
```

## Why this aligns with a Senior Data Analyst role

The stack mirrors real-world expectations: complex SQL and modeling, production-minded Python pipelines, PySpark scalability, data quality controls, testability, cloud deployment awareness (Azure), BI integration (Power BI), and clear stakeholder communication through dashboard + presentation artifacts.
