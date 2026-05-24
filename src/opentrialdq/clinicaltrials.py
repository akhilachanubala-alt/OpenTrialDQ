"""ClinicalTrials.gov API helpers for OpenTrialDQ.

The functions in this module use the public ClinicalTrials.gov API v2 and
flatten selected study fields into an analytics-friendly structure. Network
access is intentionally isolated in ``fetch_studies`` so parsing and validation
can be tested with local fixtures.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from pyspark.sql import DataFrame, SparkSession

CLINICALTRIALS_STUDIES_URL = "https://clinicaltrials.gov/api/v2/studies"


def build_studies_url(
    query_term: str,
    page_size: int = 10,
    page_token: str | None = None,
) -> str:
    """Build a ClinicalTrials.gov studies API URL."""
    if not query_term.strip():
        raise ValueError("query_term is required")
    if page_size < 1 or page_size > 1000:
        raise ValueError("page_size must be between 1 and 1000")

    params: dict[str, str | int] = {
        "query.term": query_term,
        "pageSize": page_size,
        "format": "json",
    }
    if page_token:
        params["pageToken"] = page_token

    return f"{CLINICALTRIALS_STUDIES_URL}?{urlencode(params)}"


def fetch_studies(
    query_term: str,
    page_size: int = 10,
    page_token: str | None = None,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Fetch studies from ClinicalTrials.gov API v2.

    This function performs a live network call. Tests should generally use
    local fixtures with ``flatten_studies_response`` instead.
    """
    url = build_studies_url(
        query_term=query_term,
        page_size=page_size,
        page_token=page_token,
    )
    with urlopen(url, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def flatten_studies_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten a ClinicalTrials.gov studies response into row dictionaries."""
    studies = response.get("studies", [])
    return [flatten_study(study) for study in studies]


def studies_response_to_dataframe(
    spark: SparkSession,
    response: dict[str, Any],
) -> DataFrame:
    """Convert a ClinicalTrials.gov response into a Spark DataFrame."""
    rows = flatten_studies_response(response)
    return spark.createDataFrame(rows)


def flatten_study(study: dict[str, Any]) -> dict[str, Any]:
    """Flatten selected fields from one ClinicalTrials.gov study record."""
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
    design = protocol.get("designModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    contacts_locations = protocol.get("contactsLocationsModule", {})

    lead_sponsor = sponsor_module.get("leadSponsor", {})
    enrollment = design.get("enrollmentInfo", {})

    return {
        "nct_id": identification.get("nctId"),
        "brief_title": identification.get("briefTitle"),
        "official_title": identification.get("officialTitle"),
        "overall_status": status.get("overallStatus"),
        "start_date": _date_value(status.get("startDateStruct")),
        "completion_date": _date_value(status.get("completionDateStruct")),
        "study_type": design.get("studyType"),
        "phases": _join_values(design.get("phases")),
        "sponsor_name": lead_sponsor.get("name"),
        "sponsor_class": lead_sponsor.get("class"),
        "enrollment_count": enrollment.get("count"),
        "enrollment_type": enrollment.get("type"),
        "conditions": _join_values(conditions_module.get("conditions")),
        "countries": _join_values(_location_values(contacts_locations.get("locations", []), "country")),
        "source_system": "ClinicalTrials.gov",
    }


def _date_value(date_struct: dict[str, Any] | None) -> str | None:
    if not date_struct:
        return None
    return date_struct.get("date")


def _join_values(values: list[Any] | None) -> str | None:
    if not values:
        return None
    return "|".join(str(value) for value in values if value is not None)


def _location_values(locations: list[dict[str, Any]], field_name: str) -> list[str]:
    values = []
    for location in locations:
        value = location.get(field_name)
        if value and value not in values:
            values.append(value)
    return values