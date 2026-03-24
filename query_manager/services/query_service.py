"""
services/query_service.py
Business logic for query CRUD and search.
Uses psycopg2 (%s placeholders).
"""
import json
from typing import List, Optional, Tuple

from database.connection import get_conn
from models.query import Query
from config.settings import settings


class QueryService:

    def get_by_folder(self, folder_id: int) -> List[Query]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM queries WHERE folder_id = %s ORDER BY name",
                (folder_id,)
            )
            return [Query.from_row(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, query_id: int) -> Optional[Query]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM queries WHERE id = %s", (query_id,))
            row = cur.fetchone()
            return Query.from_row(row) if row else None
        finally:
            conn.close()

    def create(
        self,
        folder_id: int,
        name: str,
        description: str,
        sql_content: str,
        tags: List[str],
        created_by: str,
    ) -> Tuple[bool, str]:
        if not name.strip():
            return False, "Query name cannot be empty."
        if not sql_content.strip():
            return False, "SQL content cannot be empty."

        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO queries (folder_id, name, description, tags, created_by) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (folder_id, name.strip(), description, json.dumps(tags), created_by),
            )
            query_id = cur.fetchone()["id"]
            cur.execute(
                """INSERT INTO query_versions
                   (query_id, version, sql_content, description, change_summary, changed_by)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (query_id, 1, sql_content, description, "Initial version", created_by),
            )
            conn.commit()
            return True, str(query_id)
        except Exception:
            conn.rollback()
            return False, "A query with that name already exists in this folder."
        finally:
            conn.close()

    def update_meta(
        self,
        query_id: int,
        name: str,
        description: str,
        tags: List[str],
    ) -> Tuple[bool, str]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE queries SET name = %s, description = %s, tags = %s WHERE id = %s",
                (name.strip(), description, json.dumps(tags), query_id),
            )
            conn.commit()
            return True, "Query updated."
        except Exception:
            conn.rollback()
            return False, "A query with that name already exists in this folder."
        finally:
            conn.close()

    def delete(self, query_id: int) -> Tuple[bool, str]:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM queries WHERE id = %s", (query_id,))
            conn.commit()
            return True, "Query deleted."
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def search(self, term: str) -> list:
        """Search queries by name, description, or SQL content."""
        if not term.strip():
            return []
        like = f"%{term.strip()}%"
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT q.*,
                       f.name      AS folder_name,
                       qv.sql_content,
                       qv.version,
                       qv.changed_by,
                       qv.changed_at
                FROM queries q
                JOIN folders f ON q.folder_id = f.id
                JOIN query_versions qv ON qv.query_id = q.id
                WHERE qv.version = (
                    SELECT MAX(version) FROM query_versions WHERE query_id = q.id
                )
                AND (q.name ILIKE %s OR q.description ILIKE %s OR qv.sql_content ILIKE %s)
                ORDER BY q.name
                LIMIT %s
                """,
                (like, like, like, settings.SEARCH_RESULTS_LIMIT),
            )
            return cur.fetchall()
        finally:
            conn.close()


query_service = QueryService()
