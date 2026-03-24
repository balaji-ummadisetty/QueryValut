"""
models/version.py
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryVersion:
    id: int
    query_id: int
    version: int
    sql_content: str
    description: Optional[str]
    change_summary: Optional[str]
    changed_by: str
    changed_at: str  # stored as string for display

    @staticmethod
    def from_row(row) -> "QueryVersion":
        # psycopg2 returns datetime objects; convert to string
        changed_at = row["changed_at"]
        if hasattr(changed_at, "isoformat"):
            changed_at = changed_at.isoformat(sep=" ")
        return QueryVersion(
            id=row["id"],
            query_id=row["query_id"],
            version=row["version"],
            sql_content=row["sql_content"],
            description=row["description"],
            change_summary=row["change_summary"],
            changed_by=row["changed_by"],
            changed_at=str(changed_at),
        )

    @property
    def changed_at_short(self) -> str:
        return self.changed_at[:16] if self.changed_at else ""
