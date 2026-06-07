# Sample Upload: ClinicalTrials.gov Diabetes Trials

This folder contains an upload-ready public clinical trial CSV generated from the ClinicalTrials.gov API v2.

## Source

- Source system: ClinicalTrials.gov public API v2
- Query term: diabetes
- Records pulled: 50
- Generated for OpenTrialLens dashboard testing
- Data boundary: public ClinicalTrials.gov data only; no employer data or proprietary schema

## Files

- `clinicaltrials_diabetes_50.csv`: Upload-ready clinical trial CSV
- `clinicaltrials_diabetes_50_results.json`: OpenTrialLens-style audit and chart summary

## Result Summary

- Records processed: 50
- Data quality score: 97%
- Failed checks: 14
- Total enrollment across records: 13,494
- Recruiting trials: 7

## Top Study Status Counts

- Completed: 31
- Recruiting: 7
- Unknown: 7
- Active Not Recruiting: 2
- Terminated: 2
- Not Yet Recruiting: 1

## Top Phase Counts

- Not applicable: 21
- Missing: 10
- Phase 2: 8
- Phase 4: 5
- Phase 3: 5
- Phase 1: 4

## Top Sponsor Class Counts

- Other: 37
- Industry: 10
- Fed: 2
- Nih: 1

## Main Data Quality Findings

- 13 required-field failures
- 1 numeric-positive enrollment check failure
- Most missing required-field issues were missing trial phase or country coverage

## How To Reproduce

Open `docs/opentriallens/index.html`, click `Upload CSV`, and select `clinicaltrials_diabetes_50.csv`.