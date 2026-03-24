"""
main.py
Application entry point.

Run with:
    streamlit run main.py
"""
import sys
import os

# Ensure project root is on sys.path so all imports resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from config.settings import settings
from database.migrations import run_migrations
from ui.styles import inject_css
from ui.sidebar import render_sidebar
from ui.pages import auth_page, browse_page, activity_page, search_page, manage_page, chat_page


def init_session():
    """Set default session state keys."""
    defaults = {
        "user": None,
        "page": "browse",
        "selected_folder": None,
        "selected_query": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main():
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon="🗄️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_css()
    run_migrations()
    init_session()

    # Auth gate
    if not st.session_state.user:
        auth_page.render()
        return

    # Authenticated layout
    render_sidebar()

    page = st.session_state.page
    PAGE_MAP = {
        "browse":   browse_page.render,
        "activity": activity_page.render,
        "search":   search_page.render,
        "manage":   manage_page.render,
        "chat":     chat_page.render,
    }

    renderer = PAGE_MAP.get(page, browse_page.render)
    renderer()


if __name__ == "__main__":
    main()
