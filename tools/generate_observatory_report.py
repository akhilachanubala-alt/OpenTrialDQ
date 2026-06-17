"""Generate public ClinicalTrials.gov data quality observatory snapshots.

This script uses the ClinicalTrials.gov API v2 and local, explainable quality
checks. It writes a JSON report and a Markdown summary that can be published in
this repository. It uses public data only.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

API_URL = "https://clinicaltrials.gov/api/v2/studies"
DEFAULT_CONDITIONS = [
    "diabetes",
    "breast cancer",
    "cardiovascular disease",
    "asthma",
    "alzheimer disease",
]
REQUIRED_FIELDS = [
    ("nct_id", "NCT ID is required", "critical"),
    ("overall_status", "Study status is required", "high"),
    ("phases", "Trial phase is missing", "medium"),
    ("sponsor_name", "Sponsor name is required", "high"),
    ("enrollment_count", "Enrollment count is required", "medium"),
    ("conditions", "Condition list is required", "high"),
    ("countries", "Location country coverage is missing", "medium"),
]


def fetch_studies(query: str, page_size: int) -> dict[str, Any]:
    params = urllib.parse.urlencode({"query.term": query, "pageSize": page_size, "format": "json"})
    request = urllib.request.Request(
        f"{API_URL}?{params}",
        headers={"Accept": "application/json", "User-Agent": "OpenTrialDQ-observatory/0.2"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:  # nosec B310 - public API endpoint
        return json.loads(response.read().decode("utf-8"))


def flatten_study(study: dict[str, Any]) -> dict[str, str]:
    protocol = study.get("protocolSection") or {}
    identification = protocol.get("identificationModule") or {}
    status = protocol.get("statusModule") or {}
    sponsors = protocol.get("sponsorCollaboratorsModule") or {}
    design = protocol.get("designModule") or {}
    conditions = protocol.get("conditionsModule") or {}
    contacts_locations = protocol.get("contactsLocationsModule") or {}
    locations = contacts_locations.get("locations") or []
    lead_sponsor = sponsors.get("leadSponsor") or {}
    enrollment = design.get("enrollmentInfo") or {}

    return {
        "nct_id": text(identification.get("nctId")),
        "overall_status": format_enum(status.get("overallStatus")),
        "start_date": date_value(status.get("startDateStruct")),
        "completion_date": date_value(status.get("completionDateStruct")),
        "phases": join_values(format_phase(value) for value in design.get("phases") or []),
        "sponsor_name": text(lead_sponsor.get("name")),
        "sponsor_class": format_enum(lead_sponsor.get("class")),
        "enrollment_count": text(enrollment.get("count")),
        "conditions": join_values(conditions.get("conditions") or []),
        "countries": join_values(location.get("country") for location in locations if location.get("country")),
        "source_system": "ClinicalTrials.gov",
    }


def evaluate_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    id_counts = Counter(row.get("nct_id") or "Missing" for row in rows)
    total_checks = max(1, len(rows) * (len(REQUIRED_FIELDS) + 4))

    for index, row in enumerate(rows, start=1):
        for field, reason, severity in REQUIRED_FIELDS:
            if not has_value(row.get(field)):
                failures.append(make_failure(row, index, field, "required", severity, reason))
        if has_value(row.get("enrollment_count")) and not is_positive_number(row.get("enrollment_count")):
            failures.append(make_failure(row, index, "enrollment_count", "numeric_positive", "medium", "Enrollment count should be a positive number"))
        if has_value(row.get("start_date")) and is_future_date(row.get("start_date")):
            failures.append(make_failure(row, index, "start_date", "date_not_future", "medium", "Start date is in the future"))
        if has_value(row.get("start_date")) and has_value(row.get("completion_date")) and parse_date(row["completion_date"]) < parse_date(row["start_date"]):
            failures.append(make_failure(row, index, "completion_date", "date_order", "high", "Completion date is before start date"))
        if has_value(row.get("nct_id")) and id_counts[row["nct_id"]] > 1:
            failures.append(make_failure(row, index, "nct_id", "unique", "critical", "Duplicate NCT ID found"))

    issue_counts = Counter(failure["rule"] for failure in failures)
    field_counts = Counter(failure["field"] for failure in failures)
    score = max(0, round(((total_checks - len(failures)) / total_checks) * 100))
    return {
        "records": len(rows),
        "failed_checks": len(failures),
        "total_checks": total_checks,
        "quality_score": score,
        "issue_counts": dict(issue_counts),
        "field_failure_counts": dict(field_counts),
        "failures": failures[:100],
    }


def summarize_condition(condition: str, rows: list[dict[str, str]], page_size: int) -> dict[str, Any]:
    quality = evaluate_rows(rows)
    return {
        "condition": condition,
        "records_requested": page_size,
        "records_returned": len(rows),
        "quality": quality,
        "status_counts": dict(Counter(row.get("overall_status") or "Missing" for row in rows)),
        "phase_counts": dict(split_counter(rows, "phases")),
        "sponsor_class_counts": dict(Counter(row.get("sponsor_class") or "Missing" for row in rows)),
        "country_counts": dict(split_counter(rows, "countries")),
        "total_enrollment": sum(int(float(row["enrollment_count"])) for row in rows if is_positive_number(row.get("enrollment_count"))),
        "recruiting_trials": sum(1 for row in rows if row.get("overall_status") == "Recruiting"),
        "completed_trials": sum(1 for row in rows if row.get("overall_status") == "Completed"),
    }


def build_report(conditions: list[str], page_size: int) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    condition_reports = []
    for condition in conditions:
        payload = fetch_studies(condition, page_size)
        rows = [flatten_study(study) for study in payload.get("studies") or []]
        condition_reports.append(summarize_condition(condition, rows, page_size))

    total_records = sum(item["records_returned"] for item in condition_reports)
    total_failures = sum(item["quality"]["failed_checks"] for item in condition_reports)
    weighted_score = round(sum(item["quality"]["quality_score"] * item["records_returned"] for item in condition_reports) / total_records) if total_records else 0
    return {
        "title": "Clinical Trial Data Quality Observatory Baseline Snapshot",
        "generated_at": generated_at,
        "source": "ClinicalTrials.gov API v2",
        "data_boundary": "Public ClinicalTrials.gov data only; no employer, patient-level, proprietary, or confidential data.",
        "conditions": conditions,
        "page_size_per_condition": page_size,
        "summary": {
            "condition_count": len(condition_reports),
            "total_records": total_records,
            "weighted_quality_score": weighted_score,
            "total_failed_checks": total_failures,
        },
        "condition_reports": condition_reports,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Clinical Trial Data Quality Observatory: Baseline Snapshot",
        "",
        f"Generated: {report['generated_at']}",
        "",
        f"Source: {report['source']}",
        "",
        f"Data boundary: {report['data_boundary']}",
        "",
        "## Why This Report Exists",
        "",
        "OpenTrialLens is being expanded from a dashboard into a repeatable public clinical data quality resource. This baseline snapshot applies the same explainable validation checks across several public ClinicalTrials.gov condition searches so users can compare data readiness before analytics.",
        "",
        "This report is not a clinical, scientific, regulatory, or medical conclusion. It is a data engineering quality snapshot for public records returned by the API at generation time.",
        "",
        "## Summary",
        "",
        f"- Conditions analyzed: {report['summary']['condition_count']}",
        f"- Records analyzed: {report['summary']['total_records']}",
        f"- Weighted quality score: {report['summary']['weighted_quality_score']}%",
        f"- Failed checks: {report['summary']['total_failed_checks']}",
        "",
        "| Condition | Records | Quality score | Failed checks | Total enrollment | Recruiting | Completed |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in report["condition_reports"]:
        lines.append(
            f"| {item['condition']} | {item['records_returned']} | {item['quality']['quality_score']}% | {item['quality']['failed_checks']} | {item['total_enrollment']} | {item['recruiting_trials']} | {item['completed_trials']} |"
        )

    lines.extend(["", "## Common Quality Issues", ""])
    for item in report["condition_reports"]:
        issue_counts = item["quality"].get("issue_counts") or {}
        field_counts = item["quality"].get("field_failure_counts") or {}
        top_issues = ", ".join(f"{key}: {value}" for key, value in sorted(issue_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:4]) or "No failed checks"
        top_fields = ", ".join(f"{key}: {value}" for key, value in sorted(field_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:4]) or "No field failures"
        lines.extend([
            f"### {item['condition'].title()}",
            "",
            f"- Top rule failures: {top_issues}",
            f"- Top field failures: {top_fields}",
            f"- Sponsor class mix: {format_counts(item['sponsor_class_counts'])}",
            f"- Status mix: {format_counts(item['status_counts'])}",
            "",
        ])

    lines.extend([
        "## Methodology",
        "",
        f"The generator retrieves the first {report['page_size_per_condition']} API records for each configured condition search. It flattens selected study-level fields and applies checks for required values, positive enrollment, start-date sanity, date ordering, and duplicate NCT IDs.",
        "",
        "The score is calculated as passed checks divided by total checks. A higher score means fewer quality failures were detected by these rules; it does not mean the studies are clinically better or more important.",
        "",
        "## Reproduce This Snapshot",
        "",
        "```bash",
        "python tools/generate_observatory_report.py --out-dir docs/observatory --period 2026-06-baseline",
        "```",
        "",
        "JSON output: [2026-06-baseline.json](2026-06-baseline.json)",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(report: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def format_counts(counts: dict[str, int], limit: int = 5) -> str:
    if not counts:
        return "None"
    return ", ".join(f"{key}: {value}" for key, value in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit])


def split_counter(rows: list[dict[str, str]], field: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        values = [item.strip() for item in (row.get(field) or "").split("|") if item.strip()]
        if not values:
            counts["Missing"] += 1
        else:
            counts.update(values)
    return counts


def make_failure(row: dict[str, str], index: int, field: str, rule: str, severity: str, reason: str) -> dict[str, Any]:
    return {"record_index": index, "nct_id": row.get("nct_id", ""), "field": field, "rule": rule, "severity": severity, "reason": reason}


def text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def has_value(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def is_positive_number(value: Any) -> bool:
    try:
        return float(str(value)) > 0
    except (TypeError, ValueError):
        return False


def parse_date(value: str) -> date:
    match = re.match(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", value or "")
    if not match:
        return date.min
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    day = int(match.group(3) or 1)
    return date(year, month, day)


def is_future_date(value: str) -> bool:
    parsed = parse_date(value)
    return parsed != date.min and parsed > date.today()


def date_value(value: Any) -> str:
    if isinstance(value, dict):
        return text(value.get("date"))
    return text(value)


def join_values(values: Any) -> str:
    seen: list[str] = []
    for value in values:
        item = text(value)
        if item and item not in seen:
            seen.append(item)
    return "|".join(seen)


def format_enum(value: Any) -> str:
    item = text(value)
    return item.replace("_", " ").title() if item else ""


def format_phase(value: Any) -> str:
    item = text(value).upper()
    if item in {"NA", "N/A"}:
        return "Not applicable"
    match = re.match(r"^PHASE(\d)$", item)
    if match:
        return f"Phase {match.group(1)}"
    return format_enum(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an OpenTrialDQ public data quality observatory report.")
    parser.add_argument("--condition", action="append", dest="conditions", help="Condition search term. Repeat for multiple conditions.")
    parser.add_argument("--page-size", type=int, default=50, help="ClinicalTrials.gov records per condition.")
    parser.add_argument("--out-dir", default="docs/observatory", help="Directory for report outputs.")
    parser.add_argument("--period", default="2026-06-baseline", help="Output filename prefix.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(args.conditions or DEFAULT_CONDITIONS, args.page_size)
    write_json(report, out_dir / f"{args.period}.json")
    write_markdown(report, out_dir / f"{args.period}.md")
    print(f"Wrote {out_dir / f'{args.period}.json'}")
    print(f"Wrote {out_dir / f'{args.period}.md'}")


if __name__ == "__main__":
    main()
