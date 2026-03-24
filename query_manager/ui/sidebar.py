"""
ui/sidebar.py
Renders the sidebar: folder tree navigation + page links + user info.
"""
import streamlit as st
from services.folder_service import folder_service
from ui.components import section_label


PAGES = [
    ("browse",   "📂  Browse Queries"),
    ("search",   "🔍  Search"),
    ("chat",     "🤖  AI Assistant"),
    ("activity", "📋  Activity Feed"),
    ("manage",   "⚙️  Manage Folders"),
]


def render_sidebar():
    with st.sidebar:
        # App brand
        st.markdown(
            """
            <div style="padding:1rem 0.5rem 0.5rem">
                <h1 style="font-family:'IBM Plex Mono',monospace;color:#00b8d9;
                           font-size:1.2rem;margin:0;letter-spacing:0.06em">
                    🗄️ Query Manager
                </h1>
                <p style="color:#3a4d63;font-size:0.72rem;margin:0.2rem 0 0">
                    SQL versioning & collaboration
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Navigation
        section_label("Navigation")
        for key, label in PAGES:
            active = st.session_state.get("page") == key
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.page = key
                st.session_state.selected_folder = None
                st.session_state.selected_query = None
                st.rerun()

        st.markdown("---")

        # Folder quick-access tree
        section_label("Folders")
        st.markdown('<div style="height: 300px; overflow-y: auto;">', unsafe_allow_html=True)
        _render_folder_tree()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # User info + logout
        user = st.session_state.get("user", "")
        st.markdown(
            f'<p style="color:#3a4d63;font-size:0.78rem;margin:0.3rem 0">Logged in as '
            f'<strong style="color:#00b8d9">{user}</strong></p>',
            unsafe_allow_html=True,
        )
        if st.button("🚪  Logout", use_container_width=True):
            for key in ["user", "page", "selected_folder", "selected_query"]:
                st.session_state.pop(key, None)
            st.rerun()


def _render_folder_tree():
    """Clickable folder tree in sidebar."""
    for folder, depth in folder_service.walk_tree():
        indent = "　" * depth
        icon = "📂" if depth == 0 else "📄"
        label = f"{indent}{icon} {folder.name}"
        selected = st.session_state.get("selected_folder") == folder.id

        if st.button(
            label,
            key=f"sidebar_folder_{folder.id}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            st.session_state.page = "browse"
            st.session_state.selected_folder = folder.id
            st.session_state.selected_query = None
            st.rerun()
