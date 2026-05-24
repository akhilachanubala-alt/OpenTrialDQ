# OpenTrialDQ

OpenTrialDQ is an open-source PySpark toolkit for validating public clinical trial datasets using configurable data quality rules.

The project is designed for data engineers who need reusable, auditable validation patterns for life sciences analytics pipelines. It uses public or synthetic data only and is not connected to any employer system or proprietary dataset.

## What It Does

OpenTrialDQ reads a dataset and a rule configuration file, applies validation checks, and produces three outputs:

- Passed records
- Failed records with rule-level failure reasons
- Audit summaries for pipeline review

## Why This Matters

Life sciences analytics depends on data that is complete, consistent, and traceable. Public clinical trial data often arrives as nested or inconsistent records, and teams need repeatable quality checks before using it for reporting, research operations, analytics, or downstream data products.

OpenTrialDQ provides a lightweight starting point for metadata-driven validation using PySpark.

## Current Features

- Rule-driven validation from CSV configuration
- Not-null checks
- Allowed-value checks
- Date-not-future checks
- Uniqueness checks
- Failed-record output with rule IDs and failure reasons
- Audit summary with pass/fail counts
- Synthetic clinical study sample data
- Unit tests for core rule behavior

## Project Structure

```text
OpenTrialDQ/
  src/opentrialdq/
    audit.py
    engine.py
    rules.py
  examples/
    data/clinical_studies_sample.csv
    rules/clinical_study_rules.csv
    notebooks/databricks_example.py
  tests/
    test_engine.py
  docs/
    architecture.md
  articles/
    metadata_driven_data_quality.md
```

## Example Rule Configuration

```csv
rule_id,table_name,column_name,rule_type,rule_value,severity
R001,clinical_study,nct_id,not_null,,critical
R002,clinical_study,nct_id,unique,,critical
R003,clinical_study,study_status,allowed_values,"Recruiting|Completed|Terminated|Withdrawn|Not yet recruiting",high
R004,clinical_study,start_date,date_not_future,,medium
R005,clinical_study,sponsor_name,not_null,,high
```

## Quick Start

Install dependencies in a Python environment with PySpark available:

```bash
pip install -e .
pip install pytest
```

Run tests:

```bash
pytest
```

Use the validation engine:

```python
from pyspark.sql import SparkSession
from opentrialdq.engine import validate_dataset

spark = SparkSession.builder.appName("OpenTrialDQExample").getOrCreate()

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
)

result.passed_records.show(truncate=False)
result.failed_records.show(truncate=False)
result.audit_summary.show(truncate=False)
```

## Roadmap

- ClinicalTrials.gov API ingestion
- JSON flattening into bronze/silver/gold analytics tables
- Schema drift detection
- Reference checks
- Documentation site
- GitHub Actions test workflow
- Zenodo DOI release after v1.0

## Data And Confidentiality

This repository uses only public or synthetic data. Do not commit employer data, confidential schemas, internal project names, proprietary code, screenshots, or credentials.

## License

Apache License 2.0
