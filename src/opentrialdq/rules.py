"""Rule helpers for OpenTrialDQ."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DataQualityRule:
    """Configuration for one data quality rule."""

    rule_id: str
    table_name: str
    column_name: str
    rule_type: str
    rule_value: Optional[str]
    severity: str

    @classmethod
    def from_row(cls, row) -> "DataQualityRule":
        """Build a rule from a Spark Row or dict-like object."""
        value = row["rule_value"] if "rule_value" in row and row["rule_value"] != "" else None
        return cls(
            rule_id=row["rule_id"],
            table_name=row["table_name"],
            column_name=row["column_name"],
            rule_type=row["rule_type"],
            rule_value=value,
            severity=row["severity"],
        )
