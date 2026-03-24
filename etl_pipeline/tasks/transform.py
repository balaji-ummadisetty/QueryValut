"""
tasks/transform.py
Converts raw PostgreSQL rows into Document dicts ready for embedding.
"""
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def transform_to_documents(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert extracted rows into a list of document dicts:
        {
            "id":       "<unique chroma doc id>",
            "text":     "<rich text to embed>",
            "metadata": { ... searchable fields ... }
        }

    The document ID is `query_{query_id}` (not version-specific) so that
    re-embedding an updated query simply overwrites the previous vector in
    ChromaDB rather than creating a duplicate.
    """
    documents = []

    for row in rows:
        tags = _parse_tags(row.get("tags", "[]"))

        text = _build_text(row, tags)

        doc = {
            "id": f"query_{row['query_id']}",
            "text": text,
            "metadata": {
                "query_id":    str(row["query_id"]),
                "query_name":  row["query_name"],
                "folder_id":   str(row["folder_id"]),
                "folder_name": row["folder_name"],
                "version":     str(row["version"]),
                "changed_by":  str(row["changed_by"]),
                "changed_at":  str(row["changed_at"]),
                "tags":        json.dumps(tags),
                "created_by":  str(row["created_by"]),
            },
        }
        documents.append(doc)

    logger.info("Transformed %d rows into embeddable documents", len(documents))
    return documents


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _parse_tags(raw: Any) -> List[str]:
    if isinstance(raw, list):
        return raw
    try:
        parsed = json.loads(raw or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _build_text(row: Dict[str, Any], tags: List[str]) -> str:
    """
    Build a rich natural-language representation of the query so the
    embedding captures intent, context, and SQL structure.
    """
    parts = [
        f"Query Name: {row['query_name']}",
        f"Folder: {row['folder_name']}",
    ]

    if row.get("query_description"):
        parts.append(f"Description: {row['query_description']}")

    if tags:
        parts.append(f"Tags: {', '.join(tags)}")

    if row.get("change_summary"):
        parts.append(f"Change Summary: {row['change_summary']}")

    if row.get("version_description") and row["version_description"] != row.get("query_description"):
        parts.append(f"Version Note: {row['version_description']}")

    parts.append(f"SQL:\n{row['sql_content']}")

    return "\n".join(parts)
