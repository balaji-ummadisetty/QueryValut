"""
ui/styles.py
All custom CSS for the application.
"""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background: #090d16 !important;
    color: #c9d4e8 !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0b0f1a !important;
    border-right: 1px solid #1a2235 !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #8899b4 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 0.9rem !important;
    transition: all 0.15s !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #12192e !important;
    border-color: #1e3050 !important;
    color: #c9d4e8 !important;
}

/* ── Inputs ── */
.stTextInput input,
.stTextArea textarea,
.stSelectbox > div > div {
    background: #0f1624 !important;
    border: 1px solid #1e2d45 !important;
    color: #c9d4e8 !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #00b8d9 !important;
    box-shadow: 0 0 0 2px #00b8d920 !important;
}

/* ── Buttons ── */
.stButton button {
    border-radius: 6px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.15s !important;
}
.stButton button[kind="primary"] {
    background: #006080 !important;
    border: 1px solid #0090b8 !important;
    color: #e0f6ff !important;
}
.stButton button[kind="primary"]:hover {
    background: #0077a0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0b0f1a !important;
    border-bottom: 1px solid #1a2235 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #627890 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.2rem !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    color: #00b8d9 !important;
    border-bottom: 2px solid #00b8d9 !important;
    background: transparent !important;
}

/* ── Code blocks ── */
pre, code {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    background: #0b1120 !important;
    border: 1px solid #1a2235 !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: #0f1624 !important;
    border: 1px solid #1a2235 !important;
    border-radius: 6px !important;
    color: #8899b4 !important;
    font-size: 0.88rem !important;
}

/* ── Alerts ── */
.stAlert {
    border-radius: 6px !important;
}

/* ── Dividers ── */
hr {
    border-color: #1a2235 !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: #0f1624;
    border: 1px solid #1a2235;
    border-radius: 8px;
    padding: 0.8rem 1rem;
}
[data-testid="stMetricValue"] {
    color: #00b8d9 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(APP_CSS, unsafe_allow_html=True)
