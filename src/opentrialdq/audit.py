"""Audit summary helpers for OpenTrialDQ."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build_audit_summary(
    source_df: DataFrame,
    failed_records: DataFrame,
    table_name: str,
    run_id: str,
) -> DataFrame:
    """Create a compact run-level audit summary."""
    spark = source_df.sparkSession
    input_count = source_df.count()
    failed_count = failed_records.select("record_id").distinct().count()
    passed_count = input_count - failed_count

    return spark.createDataFrame(
        [
            {
                "run_id": run_id,
                "table_name": table_name,
                "input_record_count": input_count,
                "passed_record_count": passed_count,
                "failed_record_count": failed_count,
            }
        ]
    ).withColumn("created_timestamp", F.current_timestamp())
