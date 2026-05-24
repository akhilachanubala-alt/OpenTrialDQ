# Designing Reusable Data Quality Checks for Public Clinical Trial Data with PySpark

## Subtitle

A practical open-source pattern for validating ClinicalTrials.gov records before analytics.

## Introduction

Public clinical trial data is extremely valuable for researchers, analysts, students, and data engineers. ClinicalTrials.gov provides public access to study records, and its modern API makes it possible to retrieve study metadata programmatically.

But raw public data is not automatically analytics-ready.

Clinical trial records can be nested, incomplete, inconsistent, or difficult to validate at scale. Before analysts use this data for dashboards, research operations, reporting, or exploratory analysis, data engineers need a repeatable way to answer basic quality questions.

For example:

- Does every study have an NCT ID?
- Is the study status valid?
- Is the sponsor name populated?
- Are important dates available?
- Are identifiers duplicated?
- Which records failed quality checks?
- Can we produce an audit summary for the pipeline run?

I built OpenTrialDQ as an open-source PySpark project to demonstrate a reusable approach to this problem.

Repository:

https://github.com/akhilachanubala-alt/OpenTrialDQ

## The Problem

A common pattern in data engineering is to write one-off validation logic for each dataset. That works for a small proof of concept, but it becomes difficult to maintain as the number of sources, rules, and downstream users grows.

Life sciences data pipelines especially benefit from validation that is:

- repeatable,
- auditable,
- configurable,
- easy to extend,
- clear enough for engineers and analysts to review.

The core idea behind OpenTrialDQ is simple: separate data quality rules from pipeline code.

Instead of hard-coding every check, rules are defined in a configuration file. The validation engine reads those rules and applies them consistently to the dataset.

## The OpenTrialDQ Flow

The project follows this flow:

1. A user provides a search term, such as cardiovascular.
2. OpenTrialDQ builds a ClinicalTrials.gov API URL.
3. The API returns public clinical trial records in nested JSON.
4. OpenTrialDQ flattens selected study fields into table-like rows.
5. PySpark loads the flattened data.
6. A rule file defines the quality checks.
7. The validation engine applies the rules.
8. Records are split into passed and failed outputs.
9. Failed records receive rule IDs and failure reasons.
10. An audit summary is created for review.

## Example Rules

The current version supports rules such as:

- NCT ID is required.
- NCT ID must be unique.
- Study status must be one of the allowed values.
- Start date must be populated.
- Sponsor name is required.

The rules are stored in a CSV configuration file, which makes the framework easier to extend without rewriting the validation engine.

## Outputs

OpenTrialDQ produces three main outputs.

### Passed Records

Records that satisfy the configured validation rules.

### Failed Records

Records that fail one or more rules. Each failed record includes the rule ID, failed column, failed value, severity, and failure reason.

### Audit Summary

A compact summary showing input count, passed count, and failed count for the validation run.

## Why ClinicalTrials.gov Is A Good Public Data Source

ClinicalTrials.gov is a recognizable public life sciences data source. Its API gives data engineers a safe way to work with realistic clinical study metadata without using private, employer-owned, or patient-level datasets.

OpenTrialDQ does not make medical or clinical claims. It focuses only on data engineering quality checks for public study metadata.

## Why This Matters For Data Engineering

This project is small by design, but the pattern is practical. The same architecture can be expanded to support additional public healthcare datasets, more rule types, schema drift detection, and production-style audit reporting.

For data engineers, the useful lesson is not only how to validate one dataset. The useful lesson is how to build validation logic that is reusable, explainable, and easier to operate over time.

## Next Steps

The next planned improvements are:

- ClinicalTrials.gov pagination support,
- bronze/silver/gold example outputs,
- schema drift detection,
- additional validation rule types,
- a versioned GitHub Release,
- future Zenodo DOI support.

## Project Link

OpenTrialDQ is available on GitHub:

https://github.com/akhilachanubala-alt/OpenTrialDQ

Feedback and suggestions are welcome, especially around new data quality rules and additional public healthcare datasets to support.