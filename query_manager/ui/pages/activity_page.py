"""
ui/pages/activity_page.py
Global activity feed — all recent changes across all queries and users.
"""
import streamlit as st
from services.version_service import version_service
from ui.components import page_header, activity_row, empty_state


def render():
    page_header("Activity Feed", "All recent changes across every query and user")

    rows = version_service.get_activity_feed()

    if not rows:
        empty_state("📋", "No activity yet. Start creating and editing queries!")
        return

    # Summary metrics
    m1, m2, m3 = st.columns(3)
    users = {r["changed_by"] for r in rows}
    folders = {r["folder_name"] for r in rows}
    m1.metric("Total Changes", len(rows))
    m2.metric("Contributors", len(users))
    m3.metric("Folders Active", len(folders))

    st.markdown("---")

    # Filter bar
    fcol, ucol = st.columns(2)
    with fcol:
        filter_folder = st.selectbox(
            "Filter by folder",
            options=["All"] + sorted(folders),
            key="activity_folder_filter",
        )
    with ucol:
        filter_user = st.selectbox(
            "Filter by user",
            options=["All"] + sorted(users),
            key="activity_user_filter",
        )

    st.markdown("---")

    visible = [
        r for r in rows
        if (filter_folder == "All" or r["folder_name"] == filter_folder)
        and (filter_user == "All" or r["changed_by"] == filter_user)
    ]

    if not visible:
        empty_state("🔍", "No results match your filters.")
        return

    for row in visible:
        activity_row(
            query_name=row["query_name"],
            folder_name=row["folder_name"],
            version=row["version"],
            changed_by=row["changed_by"],
            changed_at=row["changed_at"],
            change_summary=row["change_summary"],
        )
