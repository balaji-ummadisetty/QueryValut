"""
utils/helpers.py
Date formatting, tag parsing, and misc helpers.
"""
from datetime import datetime
from typing import List


def fmt_datetime(dt_str) -> str:
    """Format a datetime object or ISO string into a readable format."""
    if not dt_str:
        return "—"
    if isinstance(dt_str, datetime):
        return dt_str.strftime("%b %d, %Y  %H:%M")
    try:
        dt = datetime.fromisoformat(str(dt_str))
        return dt.strftime("%b %d, %Y  %H:%M")
    except Exception:
        return str(dt_str)[:16]


def parse_tags(raw: str) -> List[str]:
    """Parse comma-separated tags into a clean list."""
    return [t.strip() for t in raw.split(",") if t.strip()]


def tags_to_html(tags: List[str]) -> str:
    if not tags:
        return ""
    badges = "".join(
        f'<span style="background:#1e2738;color:#7c3aed;border:1px solid #3730a355;'
        f'padding:2px 8px;border-radius:12px;font-size:0.72rem;margin-right:4px">{t}</span>'
        for t in tags
    )
    return f'<div style="margin-top:4px">{badges}</div>'
