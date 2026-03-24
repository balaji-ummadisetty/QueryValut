"""
models/folder.py
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Folder:
    id: int
    parent_id: Optional[int]
    name: str
    description: Optional[str]
    created_by: str
    created_at: str

    @staticmethod
    def from_row(row) -> "Folder":
        created_at = row["created_at"]
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat(sep=" ")
        return Folder(
            id=row["id"],
            parent_id=row["parent_id"],
            name=row["name"],
            description=row["description"],
            created_by=row["created_by"],
            created_at=str(created_at),
        )
