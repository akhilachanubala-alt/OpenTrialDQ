# Release Notes: v0.1.0

## Summary

OpenTrialDQ v0.1.0 is the first public project milestone. It introduces a reusable PySpark pattern for validating public clinical trial datasets using configurable data quality rules.

## Included In This Release

- Metadata-driven validation engine.
- Rule types: not-null, allowed-values, date-not-future, and uniqueness checks.
- Passed-record and failed-record outputs.
- Audit summary output.
- Synthetic clinical study sample data.
- ClinicalTrials.gov API response flattener.
- Public ClinicalTrials.gov fixture for repeatable testing.
- Documentation for use case, rules, architecture, local setup, and recognition tracking.
- GitHub Actions workflow.
- Citation metadata.

## Validation

Local tests passed:

```text
3 passed
```

## Safe-Use Statement

This project is for data engineering demonstrations using public or synthetic data. It does not make medical, clinical, regulatory, or treatment claims.