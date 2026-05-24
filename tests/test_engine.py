from pyspark.sql import SparkSession

from opentrialdq.engine import validate_dataset


def test_validate_dataset_identifies_failed_records():
    spark = (
        SparkSession.builder.master("local[1]")
        .appName("OpenTrialDQTest")
        .getOrCreate()
    )

    source_df = spark.createDataFrame(
        [
            {"nct_id": "NCT00000001", "study_status": "Completed", "start_date": "2021-01-01", "sponsor_name": "Example University"},
            {"nct_id": None, "study_status": "Paused", "start_date": "2099-01-01", "sponsor_name": ""},
            {"nct_id": "NCT00000001", "study_status": "Recruiting", "start_date": "2024-01-01", "sponsor_name": "Example University"},
        ]
    )

    rules_df = spark.createDataFrame(
        [
            {"rule_id": "R001", "table_name": "clinical_study", "column_name": "nct_id", "rule_type": "not_null", "rule_value": None, "severity": "critical"},
            {"rule_id": "R002", "table_name": "clinical_study", "column_name": "nct_id", "rule_type": "unique", "rule_value": None, "severity": "critical"},
            {"rule_id": "R003", "table_name": "clinical_study", "column_name": "study_status", "rule_type": "allowed_values", "rule_value": "Recruiting|Completed|Terminated|Withdrawn|Not yet recruiting", "severity": "high"},
            {"rule_id": "R004", "table_name": "clinical_study", "column_name": "start_date", "rule_type": "date_not_future", "rule_value": None, "severity": "medium"},
            {"rule_id": "R005", "table_name": "clinical_study", "column_name": "sponsor_name", "rule_type": "not_null", "rule_value": None, "severity": "high"},
        ]
    )

    result = validate_dataset(
        df=source_df,
        rules_df=rules_df,
        table_name="clinical_study",
        run_id="test-run-001",
    )

    failed_rule_ids = {row["rule_id"] for row in result.failed_records.select("rule_id").collect()}
    assert failed_rule_ids == {"R001", "R002", "R003", "R004", "R005"}
    assert result.audit_summary.collect()[0]["input_record_count"] == 3
    assert result.audit_summary.collect()[0]["failed_record_count"] == 3
