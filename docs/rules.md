# Validation Rules

OpenTrialDQ uses a CSV rule configuration to describe validation behavior.

## Rule Columns

| Column | Description |
| --- | --- |
| `rule_id` | Stable ID for the rule. |
| `table_name` | Logical table or dataset name. |
| `column_name` | Column being validated. |
| `rule_type` | Type of check to apply. |
| `rule_value` | Optional parameter, such as allowed values. |
| `severity` | Business severity, such as `critical`, `high`, or `medium`. |

## Supported Rule Types

### `not_null`

Fails when the configured column is null or blank.

### `allowed_values`

Fails when the configured column is null or not included in the pipe-delimited `rule_value` list.

Example:

```csv
R003,clinical_study,study_status,allowed_values,"Recruiting|Completed|Terminated|Withdrawn|Not yet recruiting",high
```

### `date_not_future`

Fails when the configured date column is later than the current date.

### `unique`

Fails all rows whose configured column value appears more than once.

## Planned Rule Types

- numeric range checks
- regular expression checks
- reference table checks
- cross-field date checks
- schema drift checks
