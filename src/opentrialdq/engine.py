"""Validation engine for OpenTrialDQ."""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from opentrialdq.audit import build_audit_summary
from opentrialdq.rules import DataQualityRule


@dataclass(frozen=True)
class ValidationResult:
    """Outputs from one validation run."""

    passed_records: DataFrame
    failed_records: DataFrame
    audit_summary: DataFrame


def validate_dataset(
    df: DataFrame,
    rules_df: DataFrame,
    table_name: str,
    run_id: str,
    record_id_column: str | None = None,
) -> ValidationResult:
    """Validate a DataFrame using rules from a configuration DataFrame.

    Supported rule types:
    - not_null
    - allowed_values
    - date_not_future
    - unique
    """
    rules = _load_rules(rules_df, table_name)
    working_df = _with_record_id(df, record_id_column)
    working_df = _add_unique_rule_helpers(working_df, rules)

    failed_parts = []
    for rule in rules:
        failed_parts.append(_failed_records_for_rule(working_df, rule, run_id))

    failed_records = _union_or_empty(working_df, failed_parts)
    failed_record_ids = failed_records.select("record_id").distinct()

    passed_records = working_df.join(failed_record_ids, on="record_id", how="left_anti")
    passed_records = _drop_internal_columns(passed_records)
    audit_summary = build_audit_summary(working_df, failed_records, table_name, run_id)

    return ValidationResult(
        passed_records=passed_records,
        failed_records=failed_records,
        audit_summary=audit_summary,
    )


def _load_rules(rules_df: DataFrame, table_name: str) -> list[DataQualityRule]:
    rows = rules_df.filter(F.col("table_name") == table_name).collect()
    return [DataQualityRule.from_row(row.asDict()) for row in rows]


def _with_record_id(df: DataFrame, record_id_column: str | None) -> DataFrame:
    generated_id = F.monotonically_increasing_id().cast("string")
    if record_id_column:
        return df.withColumn("record_id", F.coalesce(F.col(record_id_column).cast("string"), generated_id))
    return df.withColumn("record_id", generated_id)


def _add_unique_rule_helpers(df: DataFrame, rules: list[DataQualityRule]) -> DataFrame:
    result = df
    unique_columns = sorted({rule.column_name for rule in rules if rule.rule_type == "unique"})
    for column_name in unique_columns:
        window = Window.partitionBy(F.col(column_name))
        result = result.withColumn(f"__duplicate_{column_name}", F.count(F.lit(1)).over(window))
    return result


def _failed_records_for_rule(df: DataFrame, rule: DataQualityRule, run_id: str) -> DataFrame:
    failure_condition = _failure_condition(rule)
    return (
        df.filter(failure_condition)
        .select(
            "record_id",
            F.lit(run_id).alias("run_id"),
            F.lit(rule.table_name).alias("table_name"),
            F.lit(rule.rule_id).alias("rule_id"),
            F.lit(rule.rule_type).alias("rule_type"),
            F.lit(rule.severity).alias("severity"),
            F.lit(rule.column_name).alias("failed_column"),
            F.col(rule.column_name).cast("string").alias("failed_value"),
            _failure_reason(rule).alias("failure_reason"),
            F.current_timestamp().alias("created_timestamp"),
        )
    )


def _failure_condition(rule: DataQualityRule):
    column = F.col(rule.column_name)

    if rule.rule_type == "not_null":
        return column.isNull() | (F.trim(column.cast("string")) == "")

    if rule.rule_type == "allowed_values":
        allowed_values = _split_rule_values(rule.rule_value)
        return column.isNull() | ~column.cast("string").isin(allowed_values)

    if rule.rule_type == "date_not_future":
        return F.to_date(column) > F.current_date()

    if rule.rule_type == "unique":
        return F.col(f"__duplicate_{rule.column_name}") > 1

    raise ValueError(f"Unsupported rule type: {rule.rule_type}")


def _failure_reason(rule: DataQualityRule):
    if rule.rule_type == "not_null":
        return F.lit(f"{rule.column_name} is required")
    if rule.rule_type == "allowed_values":
        return F.lit(f"{rule.column_name} must be one of: {rule.rule_value}")
    if rule.rule_type == "date_not_future":
        return F.lit(f"{rule.column_name} cannot be in the future")
    if rule.rule_type == "unique":
        return F.lit(f"{rule.column_name} must be unique")
    return F.lit("Validation rule failed")


def _split_rule_values(rule_value: str | None) -> list[str]:
    if not rule_value:
        return []
    return [value.strip() for value in rule_value.split("|")]


def _drop_internal_columns(df: DataFrame) -> DataFrame:
    internal_columns = [column for column in df.columns if column.startswith("__duplicate_")]
    if not internal_columns:
        return df
    return df.drop(*internal_columns)


def _union_or_empty(source_df: DataFrame, failed_parts: Iterable[DataFrame]) -> DataFrame:
    failed_parts = list(failed_parts)
    if failed_parts:
        return reduce(lambda left, right: left.unionByName(right), failed_parts)

    spark = source_df.sparkSession
    return spark.createDataFrame(
        [],
        "record_id string, run_id string, table_name string, rule_id string, rule_type string, severity string, failed_column string, failed_value string, failure_reason string, created_timestamp timestamp",
    )
