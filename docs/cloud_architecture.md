# Cloud-Ready Architecture (Azure-Oriented)

This project currently runs locally with Python, pandas, SQLite, SQL, and Plotly, but the same pattern can be deployed in Azure with production-grade orchestration, storage, and BI access.

## Target Azure Architecture

```text
[Marketing APIs / CSV Exports]
              |
              v
   [Azure Blob Storage: raw zone]
              |
              v
[Azure Data Factory pipelines OR Databricks Jobs]
              |
              v
 [Databricks/PySpark transform + data quality]
              |
      +-------+--------+
      |                |
      v                v
[Curated Parquet]   [Quality Logs/Alerts]
  (Blob/Data Lake)   (Log Analytics / Monitor)
      |
      v
[Azure SQL Database or Synapse DW]
      |
      v
    [Power BI]
```

## Component Mapping

- **Raw ingestion**: Azure Blob Storage stores incoming campaign extracts (CSV/JSON) by ingestion date.
- **Transformation**: Databricks (PySpark notebooks/jobs) runs scalable ETL/ELT logic and writes curated datasets.
- **Orchestration**: Azure Data Factory schedules and monitors the end-to-end pipeline.
- **Warehouse**: Azure SQL Database or Synapse hosts dimensional tables and analytical query workloads.
- **Visualization**: Power BI imports curated tables or connects live to the warehouse.
- **Security**: Secrets and connection strings should move to Azure Key Vault and Managed Identity.

## Deployment Notes

- Keep logic config-driven (`config/pipeline_config.yaml`) so local vs cloud paths are environment-specific.
- Replace SQLite table creation with warehouse DDL migrations.
- Add partitioning by `date` and `campaign_id` for performance at scale.
- Add data quality alerting to Azure Monitor (or ADF/Databricks failure notifications).
- Use CI/CD (GitHub Actions or Azure DevOps) for packaging, tests, and deployment.

## BI and Consumption Layer

- Exported Power BI-ready files (`data/powerbi_export/`) mirror curated semantic tables.
- In Azure, these exports can be replaced by direct warehouse tables/views consumed by Power BI.
- Recommended model in Power BI:
  - Fact: `fact_campaign_daily`
  - Dimensions: `dim_date`, `dim_campaign`, `dim_channel`