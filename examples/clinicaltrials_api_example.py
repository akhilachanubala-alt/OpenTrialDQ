"""Example: fetch and validate public ClinicalTrials.gov data.

This script performs a live API call. It is intended for local exploration, not
for automated tests.
"""

from pyspark.sql import SparkSession

from opentrialdq.clinicaltrials import fetch_studies, studies_response_to_dataframe
from opentrialdq.engine import validate_dataset

spark = SparkSession.builder.appName("OpenTrialDQClinicalTrialsExample").getOrCreate()

response = fetch_studies(query_term="cardiovascular", page_size=5)
studies_df = studies_response_to_dataframe(spark, response)
rules_df = spark.read.csv(
    "examples/rules/clinicaltrials_api_rules.csv",
    header=True,
    inferSchema=True,
)

result = validate_dataset(
    df=studies_df,
    rules_df=rules_df,
    table_name="clinicaltrials_api_study",
    run_id="clinicaltrials-demo-001",
    record_id_column="nct_id",
)

result.passed_records.show(truncate=False)
result.failed_records.show(truncate=False)
result.audit_summary.show(truncate=False)