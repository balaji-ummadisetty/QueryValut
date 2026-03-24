"""
models/user.py
"""
from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    password_hash: str
    is_active: bool
    created_at: str

    @staticmethod
    def from_row(row) -> "User":
        created_at = row["created_at"]
        if hasattr(created_at, "isoformat"):
            created_at = created_at.isoformat(sep=" ")
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            is_active=bool(row["is_active"]),
            created_at=str(created_at),
        )
