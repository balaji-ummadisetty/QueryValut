import streamlit as st
from services.folder_service import folder_service
from services.query_service import query_service
from services.version_service import version_service
from ui.components import query_card, empty_state
from ui.pages.query_page import render_query_detail
from utils.helpers import parse_tags


def render():
    # Inject page-level CSS tweaks
    st.markdown("""
    <style>
    /* tighten column gap */
    [data-testid="column"] { padding: 0 0.4rem !important; }
    /* remove extra padding from buttons in folder tree */
    .folder-tree .stButton button {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.84rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 2.8], gap="small")

    # ── LEFT: Folder Tree ────────────────────────────────────────────────────
    with left:
        _section("Folders")

        folders = list(folder_service.walk_tree())
        if not folders:
            st.caption("No folders yet.")
        else:
            for folder, depth in folders:
                selected = st.session_state.get("selected_folder") == folder.id
                indent = depth * 16
                icon = "📂" if depth == 0 else "📄"
                label = f"{icon} {folder.name}"
                # Use markdown indent + button
                col_gap, col_btn = st.columns([max(indent, 1), 100 - max(indent, 1)]) if depth > 0 else [None, None]
                if depth > 0:
                    with col_gap:
                        st.markdown(
                            f'<div style="width:{indent}px"></div>',
                            unsafe_allow_html=True
                        )
                    with col_btn:
                        if st.button(label, key=f"f_{folder.id}",
                                     use_container_width=True,
                                     type="primary" if selected else "secondary"):
                            st.session_state.selected_folder = folder.id
                            st.session_state.selected_query = None
                            st.rerun()
                else:
                    if st.button(label, key=f"f_{folder.id}",
                                 use_container_width=True,
                                 type="primary" if selected else "secondary"):
                        st.session_state.selected_folder = folder.id
                        st.session_state.selected_query = None
                        st.rerun()

        st.markdown('<div style="margin-top:1rem;border-top:1px solid #1a2235;padding-top:0.8rem"></div>',
                    unsafe_allow_html=True)
        with st.expander("➕ New Root Folder"):
            _folder_form(parent_id=None)

    # ── RIGHT: Content ───────────────────────────────────────────────────────
    with right:
        folder_id = st.session_state.get("selected_folder")
        if not folder_id:
            empty_state("📂", "Select a folder from the left to get started.")
            return

        folder = folder_service.get_by_id(folder_id)
        if not folder:
            st.warning("Folder not found.")
            return

        # Breadcrumb
        path = folder_service.get_path(folder_id)
        crumbs = path.split(" / ")
        crumb_html = " <span style='color:#3a4d63'>›</span> ".join(
            f'<span style="color:{"#00b8d9" if i == len(crumbs)-1 else "#8899b4"};">{c}</span>'
            for i, c in enumerate(crumbs)
        )
        st.markdown(
            f'<div style="background:#0b0f1a;border:1px solid #1a2235;border-radius:6px;'
            f'padding:0.55rem 1rem;margin-bottom:1rem;font-size:0.85rem;line-height:1.4">'
            f'📍 {crumb_html}</div>',
            unsafe_allow_html=True,
        )

        # Action buttons — toggle panels via session state
        action = st.session_state.get("browse_action")
        b1, b2, b3 = st.columns(3, gap="small")
        if b1.button("📁  Add Subfolder", use_container_width=True):
            st.session_state.browse_action = None if action == "subfolder" else "subfolder"
            st.rerun()
        if b2.button("➕  New Query", use_container_width=True):
            st.session_state.browse_action = None if action == "newquery" else "newquery"
            st.rerun()
        if b3.button("🗑️  Delete Folder", use_container_width=True):
            st.session_state.browse_action = None if action == "delete" else "delete"
            st.rerun()

        # Action panels (only one open at a time)
        if action == "subfolder":
            with st.container(border=True):
                _folder_form(parent_id=folder_id)

        elif action == "newquery":
            with st.container(border=True):
                _query_form(folder_id)

        elif action == "delete":
            with st.container(border=True):
                st.warning(f"This will permanently delete **{folder.name}** and all its queries.")
                dc1, dc2 = st.columns(2)
                if dc1.button("✅ Confirm Delete", type="primary", use_container_width=True):
                    folder_service.delete(folder_id)
                    st.session_state.selected_folder = None
                    st.session_state.selected_query = None
                    st.session_state.browse_action = None
                    st.rerun()
                if dc2.button("Cancel", use_container_width=True):
                    st.session_state.browse_action = None
                    st.rerun()

        _divider()

        # Subfolders row
        children = folder_service.get_children(folder_id)
        if children:
            _section("Subfolders")
            cols = st.columns(min(len(children), 4), gap="small")
            for i, child in enumerate(children):
                with cols[i % 4]:
                    if st.button(f"📁 {child.name}", key=f"ch_{child.id}",
                                 use_container_width=True):
                        st.session_state.selected_folder = child.id
                        st.session_state.selected_query = None
                        st.session_state.browse_action = None
                        st.rerun()
            _divider()

        # Queries
        queries = query_service.get_by_folder(folder_id)
        if not queries:
            empty_state("📝", "No queries yet — click '➕ New Query' above.")
            return

        _section(f"{len(queries)} Quer{'y' if len(queries)==1 else 'ies'}")

        for q in queries:
            latest = version_service.get_latest(q.id)
            if not latest:
                continue

            is_selected = st.session_state.get("selected_query") == q.id

            # Row: toggle button + delete
            rc1, rc2 = st.columns([0.94, 0.06], gap="small")
            with rc1:
                label = f"{'▼' if is_selected else '▶'}  📝  {q.name}"
                if st.button(label, key=f"qs_{q.id}", use_container_width=True,
                             type="primary" if is_selected else "secondary"):
                    st.session_state.selected_query = q.id if not is_selected else None
                    st.rerun()
            with rc2:
                if st.button("🗑", key=f"qd_{q.id}", help=f"Delete '{q.name}'"):
                    query_service.delete(q.id)
                    if st.session_state.get("selected_query") == q.id:
                        st.session_state.selected_query = None
                    st.rerun()

            # Summary card
            query_card(
                name=q.name,
                description=q.description,
                version=latest.version,
                tags=q.tags,
                created_by=q.created_by,
                changed_by=latest.changed_by,
                changed_at=latest.changed_at,
            )

            # Expanded detail
            if is_selected:
                render_query_detail(q, latest)

            _divider()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _section(label: str):
    st.markdown(
        f'<p style="color:#4a5e78;font-size:0.7rem;font-weight:700;letter-spacing:0.12em;'
        f'text-transform:uppercase;border-bottom:1px solid #1a2235;'
        f'padding-bottom:0.3rem;margin:0.2rem 0 0.6rem">{label}</p>',
        unsafe_allow_html=True,
    )

def _divider():
    st.markdown(
        '<div style="border-top:1px solid #111827;margin:0.6rem 0"></div>',
        unsafe_allow_html=True,
    )

def _folder_form(parent_id):
    key = f"ff_{parent_id or 'root'}"
    with st.form(key):
        name = st.text_input("Folder name", placeholder="e.g. Listings")
        desc = st.text_input("Description (optional)")
        if st.form_submit_button("Create Folder", use_container_width=True):
            if not name.strip():
                st.error("Name is required.")
                return
            ok, msg = folder_service.create(
                name=name.strip(),
                created_by=st.session_state.user,
                parent_id=parent_id,
                description=desc.strip() or None,
            )
            if ok:
                st.success(msg)
                st.session_state.browse_action = None
                st.rerun()
            else:
                st.error(msg)

def _query_form(folder_id):
    with st.form(f"qf_{folder_id}"):
        name     = st.text_input("Query name *", placeholder="e.g. Active Listings")
        desc     = st.text_area("Description", height=80,
                                placeholder="What does this query return?")
        tags_raw = st.text_input("Tags (comma-separated)",
                                 placeholder="listing, mls, active")
        sql      = st.text_area(
            "SQL *", height=240,
            placeholder="SELECT *\nFROM listings\nWHERE status = 'active'\nORDER BY created_at DESC"
        )
        if st.form_submit_button("💾  Save Query", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("Query name is required.")
                return
            if not sql.strip():
                st.error("SQL content is required.")
                return
            ok, msg = query_service.create(
                folder_id=folder_id,
                name=name.strip(),
                description=desc.strip(),
                sql_content=sql.strip(),
                tags=parse_tags(tags_raw),
                created_by=st.session_state.user,
            )
            if ok:
                st.success("Query saved!")
                st.session_state.selected_query = int(msg)
                st.session_state.browse_action = None
                st.rerun()
            else:
                st.error(msg)