"""
tasks/extract.py
Pulls queries and their latest versions from PostgreSQL
where something changed since the given watermark timestamp.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


def extract_changed_queries(
    source_db_url: str,
    since: datetime,
) -> List[Dict[str, Any]]:
    """
    Return all queries whose latest version was created/changed after `since`.

    Each row contains:
        query_id, query_name, query_description, tags (raw JSON string),
        folder_id, folder_name, created_by,
        version_id, version, sql_content, change_summary, changed_by, changed_at
    """
    conn = psycopg2.connect(
        source_db_url,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                q.id            AS query_id,
                q.name          AS query_name,
                q.description   AS query_description,
                q.tags,
                q.folder_id,
                q.created_by,
                f.name          AS folder_name,
                qv.id           AS version_id,
                qv.version,
                qv.sql_content,
                qv.description  AS version_description,
                qv.change_summary,
                qv.changed_by,
                qv.changed_at
            FROM queries q
            JOIN folders f ON q.folder_id = f.id
            JOIN query_versions qv ON qv.query_id = q.id
            WHERE qv.version = (
                SELECT MAX(v2.version)
                FROM query_versions v2
                WHERE v2.query_id = q.id
            )
            AND (
                qv.changed_at  > %s
                OR q.created_at > %s
            )
            ORDER BY qv.changed_at DESC
            """,
            (since, since),
        )
        rows = cur.fetchall()
        result = [dict(r) for r in rows]
        logger.info("Extracted %d changed queries since %s", len(result), since)
        return result
    finally:
        conn.close()


def extract_deleted_query_ids(
    source_db_url: str,
    known_ids: List[int],
) -> List[int]:
    """
    Given a list of query IDs that exist in the vector store,
    return those that no longer exist in PostgreSQL (i.e. were deleted).
    """
    if not known_ids:
        return []

    conn = psycopg2.connect(
        source_db_url,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM queries WHERE id = ANY(%s)",
            (known_ids,),
        )
        existing = {r["id"] for r in cur.fetchall()}
        deleted = [qid for qid in known_ids if qid not in existing]
        logger.info("Found %d deleted queries to remove from vector store", len(deleted))
        return deleted
    finally:
        conn.close()
