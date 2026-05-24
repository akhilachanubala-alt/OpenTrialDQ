# Databricks notebook source
# OpenTrialDQ example notebook

from opentrialdq.engine import validate_dataset

source_df = spark.read.csv(
    "examples/data/clinical_studies_sample.csv",
    header=True,
    inferSchema=True,
)

rules_df = spark.read.csv(
    "examples/rules/clinical_study_rules.csv",
    header=True,
    inferSchema=True,
)

result = validate_dataset(
    df=source_df,
    rules_df=rules_df,
    table_name="clinical_study",
    run_id="demo-run-001",
    record_id_column="nct_id",
)

result.passed_records.display()
result.failed_records.display()
result.audit_summary.display()
