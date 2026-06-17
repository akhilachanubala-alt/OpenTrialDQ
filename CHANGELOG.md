# Changelog

## v0.2.0 - Clinical Trial Data Quality Observatory

### Added

- Public Clinical Trial Data Quality Observatory documentation.
- Repeatable `tools/generate_observatory_report.py` script using the public ClinicalTrials.gov API v2.
- June 2026 baseline snapshot covering 250 public records across diabetes, breast cancer, cardiovascular disease, asthma, and Alzheimer disease searches.
- JSON and Markdown report outputs with quality scores, failed checks, enrollment totals, recruiting/completed counts, common failed rules, field failures, sponsor mix, and trial status mix.

### Notes

This observatory uses public ClinicalTrials.gov data only. It does not use employer data, proprietary schemas, patient-level records, internal project names, screenshots, or confidential business logic.

## v0.1.0 - Initial Public Scaffold

### Added

- PySpark validation engine for configurable data quality rules.
- Synthetic clinical study sample dataset.
- Rule configuration examples.
- ClinicalTrials.gov API URL builder and response flattener.
- Local ClinicalTrials.gov fixture for repeatable tests.
- Failed-record output with failure reasons.
- Audit summary output.
- Unit tests and GitHub Actions workflow.
- Plain-English use case documentation.
- Contribution, security, and local Windows setup notes.
- Citation metadata through `CITATION.cff`.

### Notes

This release uses only public or synthetic data. It does not use employer data, proprietary schemas, internal project names, or confidential business logic.