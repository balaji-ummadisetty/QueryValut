"""
ui/pages/auth_page.py
Login and registration page.
"""
import streamlit as st
from services.auth_service import auth_service


def render():
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            """
            <div style="text-align:center;padding:3rem 0 2rem">
                <h1 style="font-family:'IBM Plex Mono',monospace;color:#00b8d9;font-size:2rem;margin:0">
                    🗄️ Query Manager
                </h1>
                <p style="color:#3a4d63;margin:0.4rem 0 0">
                    Centralized SQL versioning &amp; collaboration
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                if submitted:
                    user = auth_service.login(username, password)
                    if user:
                        st.session_state.user = user.username
                        st.session_state.page = "browse"
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

            st.caption("Default: `admin` / `admin123`")

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Username")
                new_pw   = st.text_input("Password", type="password")
                new_pw2  = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    if new_pw != new_pw2:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = auth_service.register(new_user, new_pw)
                        if ok:
                            st.success(f"{msg} Please log in.")
                        else:
                            st.error(msg)
