"""
utils/diff.py
SQL diff computation utilities.
"""
import difflib
from typing import List


def compute_unified_diff(old_sql: str, new_sql: str) -> str:
    """Return unified diff string between two SQL strings."""
    old_lines = old_sql.splitlines(keepends=True)
    new_lines = new_sql.splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="Previous Version",
            tofile="Current Version",
            lineterm="",
        )
    )
    return "\n".join(diff) if diff else ""


def render_diff_html(diff_text: str) -> str:
    """Convert unified diff text into styled HTML."""
    if not diff_text:
        return '<p style="color:#4ade80">✓ No SQL changes in this version.</p>'

    lines_html = []
    for line in diff_text.split("\n"):
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith("+") and not line.startswith("+++"):
            lines_html.append(
                f'<div style="background:#052e16;color:#4ade80;padding:1px 8px;'
                f'font-family:monospace;font-size:0.82rem;white-space:pre">{escaped}</div>'
            )
        elif line.startswith("-") and not line.startswith("---"):
            lines_html.append(
                f'<div style="background:#2d0a0a;color:#f87171;padding:1px 8px;'
                f'font-family:monospace;font-size:0.82rem;white-space:pre">{escaped}</div>'
            )
        elif line.startswith("@@"):
            lines_html.append(
                f'<div style="background:#1e1b4b;color:#a78bfa;padding:1px 8px;'
                f'font-family:monospace;font-size:0.82rem;white-space:pre">{escaped}</div>'
            )
        elif line.startswith("---") or line.startswith("+++"):
            lines_html.append(
                f'<div style="color:#64748b;padding:1px 8px;'
                f'font-family:monospace;font-size:0.82rem;white-space:pre">{escaped}</div>'
            )
        else:
            lines_html.append(
                f'<div style="color:#94a3b8;padding:1px 8px;'
                f'font-family:monospace;font-size:0.82rem;white-space:pre">{escaped}</div>'
            )

    body = "\n".join(lines_html)
    return (
        f'<div style="background:#0d1117;border:1px solid #2d3748;'
        f'border-radius:6px;overflow:auto;max-height:400px">{body}</div>'
    )
