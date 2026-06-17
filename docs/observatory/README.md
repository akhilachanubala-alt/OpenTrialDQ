# Clinical Trial Data Quality Observatory

The Clinical Trial Data Quality Observatory is a public reporting layer for OpenTrialDQ and OpenTrialLens. It turns the project from a single dashboard into a repeatable public data quality resource for selected ClinicalTrials.gov condition searches.

## Purpose

Public clinical trial records are valuable, but they are not always immediately analytics-ready. The observatory applies transparent data quality checks to public ClinicalTrials.gov API results and publishes repeatable snapshots that show where data is complete, missing, inconsistent, or ready for downstream analytics.

The goal is to help data engineers, students, health-tech builders, analysts, and researchers understand data readiness before building dashboards, reports, or AI workflows.

## Current Snapshot

- [June 2026 baseline snapshot](2026-06-baseline.md)
- [June 2026 baseline JSON](2026-06-baseline.json)

## What The Snapshot Measures

For each condition search, the generator reports:

- records returned
- quality score
- failed check count
- enrollment total
- recruiting and completed trial counts
- common failed rules
- common failed fields
- sponsor class mix
- trial status mix

## Data Boundary

This observatory uses public ClinicalTrials.gov data only. It does not use employer data, proprietary schemas, restricted business logic, credentials, screenshots, patient-level data, or confidential records.

The output is a data engineering quality snapshot, not a clinical, regulatory, scientific, or medical conclusion.

## Generate A New Snapshot

```bash
python tools/generate_observatory_report.py --out-dir docs/observatory --period 2026-06-baseline
```

Optional custom condition searches:

```bash
python tools/generate_observatory_report.py --condition diabetes --condition oncology --condition asthma --page-size 50
```

## Why This Adds Significance

The observatory creates recurring, public, and reproducible evidence of clinical data quality work. Instead of only showing that a dashboard exists, it publishes measurable public outputs that others can inspect, cite, compare, and build on.
