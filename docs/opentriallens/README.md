# OpenTrialLens

OpenTrialLens is the visual dashboard layer for OpenTrialDQ. It turns public ClinicalTrials.gov records or user-uploaded clinical-study CSV files into data quality metrics, failed-record outputs, and clinical trial summary charts.

## Problem Statement

Public clinical trial data is valuable, but it is often nested, incomplete, inconsistent, and difficult for non-technical users to inspect quickly. Data engineers, analysts, students, and healthcare researchers need a simple way to search public trial data, check quality, visualize trial coverage, and export audit-ready outputs.

## MVP Capabilities

- Search live ClinicalTrials.gov study records by condition.
- Upload a clinical-study-style CSV file.
- Flatten selected trial fields into analytics-ready rows.
- Run browser-side checks for missing required fields, duplicates, dates, enrollment, sponsor, phase, condition, and country coverage.
- Display quality score, failed checks, study status counts, phase mix, sponsor class, country coverage, and start-year trend.
- Export flattened records, failed-record details, and an audit summary.

## NIW Profile Alignment

OpenTrialLens demonstrates reusable, public-facing data engineering for life sciences and healthcare analytics. It extends OpenTrialDQ from a backend PySpark validation toolkit into a visual tool that can be understood by data engineers, analysts, students, patient advocacy teams, and healthcare technology audiences.

## Data Boundary

This dashboard uses public ClinicalTrials.gov data or user-provided sample files only. It does not use employer data, proprietary schemas, restricted business logic, or confidential records.

## Local Use

Open `docs/opentriallens/index.html` in a browser. Live ClinicalTrials.gov search requires internet access. If the live API is unavailable, the dashboard can still load synthetic sample data.

## GitHub Pages

If GitHub Pages is enabled from the `docs` folder on the `main` branch, the dashboard path will be:

`https://akhilachanubala-alt.github.io/OpenTrialDQ/opentriallens/`

## Published Article

[Introducing OpenTrialLens: A Dashboard for Clinical Trial Data Quality and Visual Insights](https://lifesciencesdataengineering.hashnode.dev/introducing-opentriallens-a-dashboard-for-clinical-trial-data-quality-and-visual-insights)

## Sample Upload Dataset

A public ClinicalTrials.gov diabetes-trials CSV is available for dashboard testing:

- [sample-data/clinicaltrials_diabetes_50.csv](sample-data/clinicaltrials_diabetes_50.csv)
- [sample-data/clinicaltrials_diabetes_50_results.json](sample-data/clinicaltrials_diabetes_50_results.json)
- [sample-data/README.md](sample-data/README.md)