"""
services/version_service.py
Business logic for query versioning and activity feed.
Uses psycopg2 (%s placeholders).
"""
from typing import List, Optional, Tuple

from database.connection import get_conn
from models.version import QueryVersion
from config.settings import settings


class VersionService:

    def get_latest(self, query_id: int) -> Optional[QueryVersion]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """SELECT * FROM query_versions
                   WHERE query_id = %s
                   ORDER BY version DESC LIMIT 1""",
                (query_id,),
            )
            row = cur.fetchone()
            return QueryVersion.from_row(row) if row else None
        finally:
            conn.close()

    def get_all(self, query_id: int) -> List[QueryVersion]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM query_versions WHERE query_id = %s ORDER BY version DESC",
                (query_id,),
            )
            return [QueryVersion.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_version(self, query_id: int, version: int) -> Optional[QueryVersion]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM query_versions WHERE query_id = %s AND version = %s",
                (query_id, version),
            )
            row = cur.fetchone()
            return QueryVersion.from_row(row) if row else None
        finally:
            conn.close()

    def save_new_version(
        self,
        query_id: int,
        sql_content: str,
        description: str,
        change_summary: str,
        changed_by: str,
    ) -> Tuple[bool, int]:
        """
        Saves a new version. Returns (True, version_number) or (False, 0).
        Only saves if content actually changed.
        """
        latest = self.get_latest(query_id)
        if latest and latest.sql_content.strip() == sql_content.strip() \
                and (latest.description or "") == description:
            return False, 0  # No changes

        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT MAX(version) AS mv FROM query_versions WHERE query_id = %s",
                (query_id,),
            )
            row = cur.fetchone()
            new_version = (row["mv"] or 0) + 1

            cur.execute(
                """INSERT INTO query_versions
                   (query_id, version, sql_content, description, change_summary, changed_by)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (query_id, new_version, sql_content, description,
                 change_summary or "Updated", changed_by),
            )
            cur.execute(
                "UPDATE queries SET description = %s WHERE id = %s",
                (description, query_id),
            )
            conn.commit()
            return True, new_version
        except Exception:
            conn.rollback()
            return False, 0
        finally:
            conn.close()

    def get_activity_feed(self, limit: Optional[int] = None) -> list:
        """Return recent changes across all queries, with folder & query name."""
        limit = limit or settings.ACTIVITY_FEED_LIMIT
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT qv.*,
                       q.name  AS query_name,
                       f.name  AS folder_name,
                       f.id    AS folder_id
                FROM query_versions qv
                JOIN queries q ON qv.query_id = q.id
                JOIN folders f ON q.folder_id  = f.id
                ORDER BY qv.changed_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()
        finally:
            conn.close()


version_service = VersionService()
