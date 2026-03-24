"""
ui/pages/query_page.py
Renders the expanded query detail panel: View / Edit / Version History tabs.
Called inline from browse_page for the selected query.
"""
import streamlit as st
from models.query import Query
from models.version import QueryVersion
from services.version_service import version_service
from ui.components import version_row
from utils.diff import compute_unified_diff, render_diff_html
from utils.helpers import parse_tags, fmt_datetime


def render_query_detail(query: Query, latest: QueryVersion):
    """Inline expandable panel rendered below the query card."""
    with st.container():
        st.markdown(
            '<div style="background:#0a0f1c;border:1px solid #1a2235;'
            'border-radius:8px;padding:1.2rem;margin:0.3rem 0 1rem">',
            unsafe_allow_html=True,
        )

        tab_view, tab_edit, tab_history = st.tabs(["👁️ View SQL", "✏️ Edit", "📜 Version History"])

        # ── View ──────────────────────────────────────────────────────────
        with tab_view:
            st.code(latest.sql_content, language="sql")
            st.caption(
                f"Version v{latest.version} · "
                f"Updated by **{latest.changed_by}** on {fmt_datetime(latest.changed_at)} · "
                f"_{latest.change_summary or 'no summary'}_"
            )

        # ── Edit ──────────────────────────────────────────────────────────
        with tab_edit:
            with st.form(f"edit_{query.id}"):
                new_desc = st.text_area(
                    "Description",
                    value=query.description or "",
                    height=80,
                )
                new_tags = st.text_input(
                    "Tags",
                    value=", ".join(query.tags),
                )
                new_sql = st.text_area(
                    "SQL",
                    value=latest.sql_content,
                    height=280,
                )
                change_note = st.text_input(
                    "Change Summary",
                    placeholder="What changed and why?",
                )
                saved = st.form_submit_button("💾 Save as New Version", type="primary")
                if saved:
                    ok, version_num = version_service.save_new_version(
                        query_id=query.id,
                        sql_content=new_sql,
                        description=new_desc,
                        change_summary=change_note or "Updated",
                        changed_by=st.session_state.user,
                    )
                    if ok:
                        # Update tags meta
                        from services.query_service import query_service
                        query_service.update_meta(
                            query.id,
                            name=query.name,
                            description=new_desc,
                            tags=parse_tags(new_tags),
                        )
                        st.success(f"✅ Saved as version v{version_num}")
                        st.rerun()
                    else:
                        st.warning("No changes detected — nothing was saved.")

        # ── Version History ───────────────────────────────────────────────
        with tab_history:
            versions = version_service.get_all(query.id)
            st.markdown(
                f'<p style="color:#3a4d63;font-size:0.8rem;margin-bottom:0.8rem">'
                f'{len(versions)} version(s) total</p>',
                unsafe_allow_html=True,
            )

            for i, ver in enumerate(versions):
                is_latest = i == 0
                version_row(
                    version=ver.version,
                    changed_by=ver.changed_by,
                    changed_at=ver.changed_at,
                    change_summary=ver.change_summary,
                    is_latest=is_latest,
                )
                with st.expander(f"View v{ver.version} SQL & diff"):
                    st.code(ver.sql_content, language="sql")

                    if i < len(versions) - 1:
                        prev = versions[i + 1]
                        st.markdown("**Changes from previous version:**")
                        diff = compute_unified_diff(prev.sql_content, ver.sql_content)
                        st.markdown(render_diff_html(diff), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
