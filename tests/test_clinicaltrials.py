import json
from pathlib import Path

from opentrialdq.clinicaltrials import build_studies_url, flatten_studies_response


FIXTURE_PATH = Path("examples/data/clinicaltrials_response_sample.json")


def test_build_studies_url_encodes_query_parameters():
    url = build_studies_url("heart disease", page_size=25, page_token="abc123")

    assert url.startswith("https://clinicaltrials.gov/api/v2/studies?")
    assert "query.term=heart+disease" in url
    assert "pageSize=25" in url
    assert "pageToken=abc123" in url
    assert "format=json" in url


def test_flatten_studies_response_returns_analytics_ready_rows():
    response = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    rows = flatten_studies_response(response)

    assert len(rows) == 2
    assert rows[0]["nct_id"] == "NCT10000001"
    assert rows[0]["overall_status"] == "COMPLETED"
    assert rows[0]["phases"] == "PHASE2"
    assert rows[0]["countries"] == "United States"
    assert rows[1]["conditions"] == "Remote Monitoring|Patient Engagement"
    assert rows[1]["countries"] == "United States|Canada"