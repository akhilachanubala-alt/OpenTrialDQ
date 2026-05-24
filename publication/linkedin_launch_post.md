# LinkedIn Launch Post

I am starting a new open-source project: OpenTrialDQ.

OpenTrialDQ is a PySpark-based data quality toolkit for public ClinicalTrials.gov datasets. The goal is to demonstrate a reusable pattern for validating life sciences data before analytics.

The project currently supports:

- ClinicalTrials.gov API response flattening
- configurable data quality rules
- not-null, uniqueness, allowed-value, and date checks
- passed-record and failed-record outputs
- audit summaries
- local fixture-based tests
- documentation for use cases, rules, and recognition tracking

Why I built this:

Public clinical trial data is valuable, but raw API records are often nested and not immediately analytics-ready. Data engineers need repeatable ways to check quality, explain failures, and create auditable outputs.

This project is intentionally built with public and synthetic data only. It does not use employer data, proprietary schemas, or confidential business logic.

GitHub repo:
https://github.com/akhilachanubala-alt/OpenTrialDQ

I would appreciate feedback from data engineers, healthcare analytics professionals, and open-source contributors:

- What data quality rules would you add?
- What public healthcare datasets should this support next?
- What would make this more useful for real-world analytics teams?

#DataEngineering #PySpark #LifeSciences #ClinicalTrials #OpenSource #HealthcareData #DataQuality