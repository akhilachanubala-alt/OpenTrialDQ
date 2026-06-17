# Clinical Trial Data Quality Observatory: Baseline Snapshot

Generated: 2026-06-17T17:49:56+00:00

Source: ClinicalTrials.gov API v2

Data boundary: Public ClinicalTrials.gov data only; no employer, patient-level, proprietary, or confidential data.

## Why This Report Exists

OpenTrialLens is being expanded from a dashboard into a repeatable public clinical data quality resource. This baseline snapshot applies the same explainable validation checks across several public ClinicalTrials.gov condition searches so users can compare data readiness before analytics.

This report is not a clinical, scientific, regulatory, or medical conclusion. It is a data engineering quality snapshot for public records returned by the API at generation time.

## Summary

- Conditions analyzed: 5
- Records analyzed: 250
- Weighted quality score: 97%
- Failed checks: 90

| Condition | Records | Quality score | Failed checks | Total enrollment | Recruiting | Completed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| diabetes | 50 | 97% | 16 | 47056 | 6 | 30 |
| breast cancer | 50 | 97% | 19 | 14565 | 9 | 21 |
| cardiovascular disease | 50 | 96% | 20 | 37829 | 7 | 24 |
| asthma | 50 | 96% | 21 | 173109 | 4 | 33 |
| alzheimer disease | 50 | 97% | 14 | 78366 | 13 | 25 |

## Common Quality Issues

### Diabetes

- Top rule failures: required: 16
- Top field failures: phases: 13, countries: 3
- Sponsor class mix: Other: 35, Industry: 12, Other Gov: 3
- Status mix: Completed: 30, Recruiting: 6, Unknown: 6, Terminated: 4, Not Yet Recruiting: 2

### Breast Cancer

- Top rule failures: required: 16, numeric_positive: 3
- Top field failures: phases: 13, countries: 3, enrollment_count: 3
- Sponsor class mix: Other: 32, Industry: 15, Nih: 2, Other Gov: 1
- Status mix: Completed: 21, Recruiting: 9, Unknown: 7, Active Not Recruiting: 4, Terminated: 4

### Cardiovascular Disease

- Top rule failures: required: 20
- Top field failures: phases: 13, countries: 7
- Sponsor class mix: Other: 37, Industry: 10, Other Gov: 2, Fed: 1
- Status mix: Completed: 24, Unknown: 9, Recruiting: 7, Terminated: 5, Active Not Recruiting: 2

### Asthma

- Top rule failures: required: 19, date_not_future: 1, numeric_positive: 1
- Top field failures: countries: 10, phases: 8, enrollment_count: 2, start_date: 1
- Sponsor class mix: Other: 27, Industry: 20, Network: 1, Nih: 1, Other Gov: 1
- Status mix: Completed: 33, Unknown: 6, Recruiting: 4, Terminated: 3, Not Yet Recruiting: 2

### Alzheimer Disease

- Top rule failures: required: 14
- Top field failures: phases: 12, countries: 2
- Sponsor class mix: Other: 36, Industry: 12, Fed: 1, Other Gov: 1
- Status mix: Completed: 25, Recruiting: 13, Unknown: 6, Terminated: 3, Active Not Recruiting: 1

## Methodology

The generator retrieves the first 50 API records for each configured condition search. It flattens selected study-level fields and applies checks for required values, positive enrollment, start-date sanity, date ordering, and duplicate NCT IDs.

The score is calculated as passed checks divided by total checks. A higher score means fewer quality failures were detected by these rules; it does not mean the studies are clinically better or more important.

## Reproduce This Snapshot

```bash
python tools/generate_observatory_report.py --out-dir docs/observatory --period 2026-06-baseline
```

JSON output: [2026-06-baseline.json](2026-06-baseline.json)
