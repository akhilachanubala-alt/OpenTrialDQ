# ClinicalTrials.gov API Integration

OpenTrialDQ includes a small ClinicalTrials.gov API helper module for public-data examples.

## Source

ClinicalTrials.gov is a public website and online database of clinical research studies and information about their results. The site is maintained by the National Library of Medicine at the National Institutes of Health.

OpenTrialDQ uses the public ClinicalTrials.gov API v2 studies endpoint for example ingestion workflows.

Official documentation:

- https://clinicaltrials.gov/data-api/api
- https://www.nlm.nih.gov/pubs/techbull/ma24/ma24_clinicaltrials_api.html

## What OpenTrialDQ Extracts

The current helper flattens selected study-level fields:

- NCT ID
- brief title
- official title
- overall status
- start date
- completion date
- study type
- phase list
- lead sponsor name and class
- enrollment count and type
- conditions
- countries
- source system

## Why This Is Useful

ClinicalTrials.gov data is public, nested, and life-sciences-specific. It is useful for demonstrating ingestion, flattening, validation, and audit patterns without using confidential employer data.

## Caution

OpenTrialDQ does not make medical, clinical, regulatory, or outcome claims. The integration is for data engineering demonstrations only.