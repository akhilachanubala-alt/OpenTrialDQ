# OpenTrialDQ Architecture

OpenTrialDQ uses a metadata-driven validation pattern.

## Flow

1. Read source clinical trial dataset.
2. Read validation rules from a configuration file or table.
3. Apply rules through a reusable PySpark validation engine.
4. Write passed records for downstream analytics.
5. Write failed records with rule-level reasons.
6. Write audit summaries for monitoring and review.

## Core Components

- `rules.py`: rule object and parsing helpers
- `engine.py`: validation orchestration and rule execution
- `audit.py`: run-level audit summary generation

## Planned Extensions

- ClinicalTrials.gov API ingestion
- JSON flattening
- Schema drift detection
- Rule-level metrics by severity
- Databricks workflow examples
- Zenodo DOI release after a stable version
