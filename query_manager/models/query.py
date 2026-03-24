"""
models/query.py
"""
from dataclasses import dataclass, field
from typing import Optional, List
import json


@dataclass
class Query:
    id: int
    folder_id: int
    name: str
    description: Optional[str]
    tags: List[str]
    created_by: str
    created_at: str

    @staticmethod
    def from_row(row) -> "Query":
        try:
            tags = json.loads(row["tags"] or "[]")
        except Exception:
            tags = []
        return Query(
            id=row["id"],
            folder_id=row["folder_id"],
            name=row["name"],
            description=row["description"],
            tags=tags,
            created_by=row["created_by"],
            created_at=row["created_at"],
        )
