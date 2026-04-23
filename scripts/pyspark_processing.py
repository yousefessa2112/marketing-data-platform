from __future__ import annotations

import subprocess
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw_campaign_data.csv"
SPARK_OUTPUT_PATH = PROJECT_ROOT / "data" / "output" / "campaign_daily_parquet"


def java_available() -> bool:
    try:
        subprocess.run(["java", "-version"], check=True, capture_output=True)
        return True
    except Exception:
        return False


def run_pyspark_processing(input_path: Path = RAW_DATA_PATH, output_path: Path = SPARK_OUTPUT_PATH) -> int:
    if not java_available():
        output_path.mkdir(parents=True, exist_ok=True)
        marker = output_path / "_SKIPPED_NO_JAVA.txt"
        marker.write_text(
            "PySpark processing skipped because no Java runtime was detected. "
            "Install Java 11+ to execute Spark locally.",
            encoding="utf-8",
        )
        return 0

    # Build local Spark session for interview demo and portability.
    spark = (
        SparkSession.builder.appName("marketing-data-platform-pyspark")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    # Define explicit schema to avoid fragile type inference.
    schema = T.StructType(
        [
            T.StructField("campaign_id", T.StringType(), False),
            T.StructField("date", T.StringType(), False),
            T.StructField("impressions", T.IntegerType(), True),
            T.StructField("clicks", T.IntegerType(), True),
            T.StructField("cost", T.DoubleType(), True),
            T.StructField("conversions", T.IntegerType(), True),
        ]
    )

    # Load raw CSV with schema.
    df = spark.read.option("header", True).schema(schema).csv(str(input_path))

    # Handle nulls and invalid records, then type/date cleanup.
    cleaned = (
        df.dropDuplicates()
        .filter(F.col("campaign_id").isNotNull())
        .filter(F.col("date").isNotNull())
        .fillna({"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0})
        .withColumn("date", F.to_date("date", "yyyy-MM-dd"))
        .filter(F.col("date").isNotNull())
        .filter(F.col("impressions") >= 0)
        .filter(F.col("clicks") >= 0)
        .filter(F.col("cost") >= 0)
        .filter(F.col("conversions") >= 0)
    )

    # Feature engineering in Spark (CTR/CPC/CPA) with safe divisions.
    enriched = (
        cleaned.withColumn(
            "ctr",
            F.when(F.col("impressions") > 0, F.col("clicks") / F.col("impressions")).otherwise(F.lit(0.0)),
        )
        .withColumn("cpc", F.when(F.col("clicks") > 0, F.col("cost") / F.col("clicks")).otherwise(F.lit(0.0)))
        .withColumn(
            "cpa",
            F.when(F.col("conversions") > 0, F.col("cost") / F.col("conversions")).otherwise(F.lit(0.0)),
        )
    )

    # Campaign-date aggregation to mirror an ELT curated table.
    daily = (
        enriched.groupBy("campaign_id", "date")
        .agg(
            F.sum("impressions").alias("impressions"),
            F.sum("clicks").alias("clicks"),
            F.round(F.sum("cost"), 2).alias("cost"),
            F.sum("conversions").alias("conversions"),
        )
        .withColumn("ctr", F.when(F.col("impressions") > 0, F.col("clicks") / F.col("impressions")).otherwise(F.lit(0.0)))
        .withColumn("cpc", F.when(F.col("clicks") > 0, F.col("cost") / F.col("clicks")).otherwise(F.lit(0.0)))
        .withColumn(
            "cpa",
            F.when(F.col("conversions") > 0, F.col("cost") / F.col("conversions")).otherwise(F.lit(0.0)),
        )
    )

    # PySpark window functions: previous-day clicks and rolling 7-day average CTR.
    w = Window.partitionBy("campaign_id").orderBy("date")
    rolling_w = w.rowsBetween(-6, 0)
    with_windows = (
        daily.withColumn("prev_day_clicks", F.lag("clicks", 1).over(w))
        .withColumn("clicks_delta", F.col("clicks") - F.coalesce(F.col("prev_day_clicks"), F.lit(0)))
        .withColumn("rolling_7d_avg_ctr", F.avg("ctr").over(rolling_w))
        .orderBy("date", "campaign_id")
    )

    # Write curated parquet for scalable downstream BI/warehouse loads.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with_windows.write.mode("overwrite").parquet(str(output_path))

    row_count = with_windows.count()
    spark.stop()
    return int(row_count)


def main() -> None:
    rows = run_pyspark_processing()
    print(f"PySpark curated parquet rows: {rows}")
    print(f"Saved PySpark output to: {SPARK_OUTPUT_PATH}")


if __name__ == "__main__":
    main()