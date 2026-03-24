"""
ui/pages/manage_page.py
Folder management: create, rename, delete, view tree stats.
"""
import streamlit as st
from services.folder_service import folder_service
from services.query_service import query_service
from ui.components import page_header, section_label, empty_state
from utils.helpers import fmt_datetime


def render():
    page_header("Manage Folders", "Create, rename, and delete folder structure")

    # ── Create root folder ─────────────────────────────────────────────────
    with st.expander("➕ Create Root Folder"):
        with st.form("manage_root_folder"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Folder Name*")
            desc = c2.text_input("Description")
            if st.form_submit_button("Create", type="primary"):
                ok, msg = folder_service.create(
                    name=name, created_by=st.session_state.user,
                    parent_id=None, description=desc or None
                )
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.rerun()

    st.markdown("---")
    section_label("All Folders")

    all_folders = list(folder_service.walk_tree())
    if not all_folders:
        empty_state("📂", "No folders created yet.")
        return

    for folder, depth in all_folders:
        queries = query_service.get_by_folder(folder.id)
        children = folder_service.get_children(folder.id)
        indent = "　" * depth

        with st.expander(
            f"{indent}{'📂' if depth == 0 else '📄'} **{folder.name}** "
            f"— {len(queries)} queries · {len(children)} subfolders"
        ):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.markdown(
                f"**Path:** `{folder_service.get_path(folder.id)}`  \n"
                f"**Created by:** {folder.created_by}  \n"
                f"**Created at:** {fmt_datetime(folder.created_at)}"
            )

            # Rename form
            with c2:
                with st.form(f"rename_{folder.id}"):
                    new_name = st.text_input("Rename to", value=folder.name)
                    new_desc = st.text_input("Description", value=folder.description or "")
                    if st.form_submit_button("Rename"):
                        ok, msg = folder_service.update(folder.id, new_name, new_desc or None)
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()

            # Add subfolder
            with c3:
                with st.form(f"sub_{folder.id}"):
                    sub_name = st.text_input("Subfolder name")
                    if st.form_submit_button("Add"):
                        ok, msg = folder_service.create(
                            name=sub_name,
                            created_by=st.session_state.user,
                            parent_id=folder.id,
                        )
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()

            # Danger zone
            st.markdown(
                '<p style="color:#dc2626;font-size:0.78rem;margin:0.5rem 0 0.2rem">⚠️ Danger Zone</p>',
                unsafe_allow_html=True,
            )
            if st.button(
                f"🗑️ Delete '{folder.name}' and all its content",
                key=f"del_folder_{folder.id}",
            ):
                folder_service.delete(folder.id)
                st.warning(f"Folder '{folder.name}' deleted.")
                st.rerun()
