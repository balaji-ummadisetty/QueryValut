"""
ui/components.py
Reusable HTML/Streamlit UI building blocks.
"""
import streamlit as st
from utils.helpers import fmt_datetime, tags_to_html
import textwrap


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="margin-bottom:1.5rem">
            <h2 style="font-family:'IBM Plex Mono',monospace;color:#00b8d9;
                       font-size:1.4rem;margin:0;letter-spacing:0.04em">{title}</h2>
            {'<p style="color:#627890;font-size:0.85rem;margin:0.25rem 0 0">' + subtitle + '</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str):
    st.markdown(
        f'<p style="color:#4a5e78;font-size:0.7rem;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;'
        f'border-bottom:1px solid #1a2235;padding-bottom:0.3rem;'
        f'margin:1rem 0 0.5rem">{text}</p>',
        unsafe_allow_html=True,
    )


def query_card(name: str, description: str, version: int, tags: list,
               created_by: str, changed_by: str, changed_at: str):
    tags_html = tags_to_html(tags)
    st.markdown(textwrap.dedent(
        f"""
        <div style="background:#0f1624;border:1px solid #1a2235;border-left:3px solid #00b8d9;
                    border-radius:6px;padding:0.9rem 1rem;margin-bottom:0.3rem">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;color:#c9d4e8">{name}</span>
                <span style="background:#0a2030;border:1px solid #00b8d955;color:#00b8d9;
                             padding:2px 8px;border-radius:4px;font-size:0.72rem;
                             font-family:'IBM Plex Mono',monospace">v{version}</span>
            </div>
            <p style="color:#627890;font-size:0.83rem;margin:0.3rem 0 0.4rem">
                {description or '<em>No description</em>'}
            </p>
            {tags_html}
            <p style="color:#3a4d63;font-size:0.72rem;margin:0.4rem 0 0">
                Created by <strong style="color:#4a6a8a">{created_by}</strong> ·
                Last edited by <strong style="color:#4a6a8a">{changed_by}</strong>
                on {fmt_datetime(changed_at)}
            </p>
        </div>
        """
    ),
        unsafe_allow_html=True,
    )
    st.write(tags_html)


def version_row(version: int, changed_by: str, changed_at: str,
                change_summary: str, is_latest: bool = False):
    dot_color = "#4ade80" if is_latest else "#3a4d63"
    badge = '<span style="background:#052e16;color:#4ade80;border:1px solid #4ade8044;padding:1px 6px;border-radius:4px;font-size:0.7rem">LATEST</span>' if is_latest else ""
    st.markdown(
        f"""
        <div style="display:flex;align-items:flex-start;gap:0.8rem;
                    padding:0.7rem 0;border-bottom:1px solid #111827">
            <div style="width:10px;height:10px;border-radius:50%;
                        background:{dot_color};margin-top:5px;flex-shrink:0"></div>
            <div style="flex:1">
                <div style="display:flex;align-items:center;gap:0.5rem">
                    <span style="font-family:'IBM Plex Mono',monospace;
                                 color:#00b8d9;font-size:0.85rem">v{version}</span>
                    {badge}
                    <span style="color:#3a4d63;font-size:0.78rem">{fmt_datetime(changed_at)}</span>
                </div>
                <p style="margin:0.2rem 0 0;color:#8899b4;font-size:0.83rem">
                    <strong style="color:#627890">{changed_by}</strong>
                    — {change_summary or 'No summary provided'}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    


def activity_row(query_name: str, folder_name: str, version: int,
                 changed_by: str, changed_at: str, change_summary: str):
    st.markdown(
        f"""
        <div style="background:#0b0f1a;border:1px solid #1a2235;border-left:2px solid #7c3aed;
                    border-radius:6px;padding:0.7rem 1rem;margin-bottom:0.4rem">
            <div style="display:flex;justify-content:space-between">
                <div>
                    <span style="color:#c9d4e8;font-weight:500">{query_name}</span>
                    <span style="color:#3a4d63;margin:0 0.4rem">in</span>
                    <span style="color:#7c3aed;font-size:0.82rem">{folder_name}</span>
                    <span style="color:#3a4d63;font-size:0.78rem;margin-left:0.5rem">→ v{version}</span>
                </div>
                <span style="color:#3a4d63;font-size:0.78rem">{fmt_datetime(changed_at)}</span>
            </div>
            <p style="margin:0.25rem 0 0;color:#4a5e78;font-size:0.8rem">
                <strong style="color:#627890">{changed_by}</strong>
                {': ' + change_summary if change_summary else ''}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, message: str):
    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 2rem;color:#3a4d63">
            <div style="font-size:2.5rem;margin-bottom:0.5rem">{icon}</div>
            <p style="font-size:0.9rem">{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
