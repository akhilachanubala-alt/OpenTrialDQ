# Contributing to OpenTrialDQ

Thank you for your interest in OpenTrialDQ.

This project focuses on reusable data quality patterns for public clinical trial and life sciences datasets. Contributions should use only public, synthetic, or clearly redistributable data.

## Contribution Guidelines

- Do not include employer data, confidential data, proprietary schemas, internal screenshots, credentials, or private business logic.
- Keep examples small enough to run locally or in a basic CI job.
- Prefer configurable rules over one-off validation logic.
- Add tests for new rule types or engine behavior.
- Update documentation when behavior changes.

## Good First Contribution Ideas

- Add a new validation rule type.
- Improve sample clinical trial data.
- Add a ClinicalTrials.gov API ingestion example.
- Add more audit summary fields.
- Improve Databricks notebook examples.
- Add documentation for deployment patterns.

## Development Setup

```bash
pip install -e .[dev]
pytest
```

OpenTrialDQ is early-stage software. The goal is to keep the core small, readable, and useful for data engineers learning practical validation patterns.
