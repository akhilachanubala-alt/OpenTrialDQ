# GitHub Release Draft: v0.1.0

## Tag

```text
v0.1.0
```

## Release Title

```text
OpenTrialDQ v0.1.0 - Initial Public Scaffold
```

## Release Description

OpenTrialDQ v0.1.0 is the first public project milestone. It introduces a reusable PySpark pattern for validating public clinical trial datasets using configurable data quality rules.

## Included In This Release

- Metadata-driven validation engine.
- Rule types: not-null, allowed-values, date-not-future, and uniqueness checks.
- Passed-record and failed-record outputs.
- Audit summary output.
- Synthetic clinical study sample data.
- ClinicalTrials.gov API response flattener.
- Public ClinicalTrials.gov fixture for repeatable testing.
- Plain-English use case documentation.
- Documentation for rules, architecture, Windows setup, recognition tracking, citation, and publication.
- GitHub Actions workflow.
- Citation metadata through `CITATION.cff`.

## Validation

Local tests passed:

```text
3 passed
```

## Safe-Use Statement

This project is for data engineering demonstrations using public or synthetic data. It does not make medical, clinical, regulatory, or treatment claims. It does not use employer data, proprietary schemas, confidential business logic, or internal systems.

## Project Links

- Repository: https://github.com/akhilachanubala-alt/OpenTrialDQ
- Use case: https://github.com/akhilachanubala-alt/OpenTrialDQ/blob/main/docs/use_case.md
- ClinicalTrials.gov API docs: https://github.com/akhilachanubala-alt/OpenTrialDQ/blob/main/docs/clinicaltrials_api.md
- Publication package: https://github.com/akhilachanubala-alt/OpenTrialDQ/tree/main/publication