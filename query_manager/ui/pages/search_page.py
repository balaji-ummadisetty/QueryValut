"""
ui/pages/search_page.py
Two search modes:
  1. Keyword Search  – full-text ILIKE across name, description, SQL content (existing)
  2. Semantic Search – embedding-based similarity via ChromaDB (new)
"""
import streamlit as st
from services.query_service import query_service
from services.rag_service import rag_service
from ui.components import page_header, empty_state
from utils.helpers import fmt_datetime


def render():
    page_header("Search Queries", "Find queries by keyword or by meaning")

    tab_kw, tab_sem = st.tabs(["🔍 Keyword Search", "🧠 Semantic Search"])

    with tab_kw:
        _keyword_search()

    with tab_sem:
        _semantic_search()


# ---------------------------------------------------------------------------
# Keyword search (original)
# ---------------------------------------------------------------------------

def _keyword_search():
    term = st.text_input(
        "",
        placeholder="🔍  Type to search names, descriptions, and SQL content…",
        label_visibility="collapsed",
        key="kw_search_term",
    )

    if not term:
        empty_state("🔍", "Enter a search term above to find queries.")
        return

    results = query_service.search(term)

    st.markdown(
        f'<p style="color:#3a4d63;font-size:0.8rem;margin-bottom:0.8rem">'
        f'{len(results)} result(s) for <strong style="color:#00b8d9">"{term}"</strong></p>',
        unsafe_allow_html=True,
    )

    if not results:
        empty_state("😶", "No queries matched your search.")
        return

    for row in results:
        _keyword_result_card(row, term)


def _keyword_result_card(row, term: str):
    sql_preview  = _highlight(row["sql_content"][:300], term)
    desc_preview = _highlight((row["description"] or "No description")[:200], term)

    st.markdown(
        f"""
        <div style="background:#0f1624;border:1px solid #1a2235;border-left:3px solid #00b8d9;
                    border-radius:6px;padding:0.9rem 1rem;margin-bottom:0.6rem">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;color:#c9d4e8">{_highlight(row['name'], term)}</span>
                <span style="color:#7c3aed;font-size:0.8rem">{row['folder_name']}</span>
            </div>
            <p style="color:#627890;font-size:0.82rem;margin:0.3rem 0 0.4rem">{desc_preview}</p>
            <pre style="background:#0b1120;border:1px solid #1a2235;border-radius:4px;
                        padding:0.5rem;font-size:0.78rem;color:#94a3b8;
                        overflow:auto;max-height:120px;white-space:pre-wrap">{sql_preview}</pre>
            <p style="color:#3a4d63;font-size:0.72rem;margin:0.4rem 0 0">
                v{row['version']} · Last updated by
                <strong style="color:#4a6a8a">{row['changed_by']}</strong>
                on {fmt_datetime(row['changed_at'])}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Semantic search (new — uses ChromaDB + embeddings)
# ---------------------------------------------------------------------------

def _semantic_search():
    st.markdown(
        '<p style="color:#4a5e78;font-size:0.8rem;margin-bottom:0.6rem">'
        "Describe what you're looking for in plain English — finds queries by <em>meaning</em>, "
        "not just exact keyword matches.</p>",
        unsafe_allow_html=True,
    )

    col_input, col_k = st.columns([0.75, 0.25], gap="small")
    with col_input:
        query_text = st.text_input(
            "",
            placeholder="🧠  e.g. 'find orders grouped by customer last 30 days'…",
            label_visibility="collapsed",
            key="sem_search_term",
        )
    with col_k:
        top_k = st.number_input(
            "Results",
            min_value=1,
            max_value=20,
            value=5,
            key="sem_top_k",
            help="Number of similar queries to return",
        )

    if not query_text.strip():
        empty_state("🧠", "Describe what you're looking for and press Enter.")
        return

    with st.spinner("Searching vector store…"):
        hits = rag_service.semantic_search(query_text.strip(), n_results=int(top_k))

    if not hits:
        st.warning(
            "No results — ChromaDB may be empty or unavailable. "
            "Make sure the ETL pipeline has run at least once."
        )
        return

    st.markdown(
        f'<p style="color:#3a4d63;font-size:0.8rem;margin-bottom:0.8rem">'
        f'Top <strong style="color:#00b8d9">{len(hits)}</strong> semantically similar '
        f'queries for <strong style="color:#00b8d9">"{query_text}"</strong></p>',
        unsafe_allow_html=True,
    )

    for hit in hits:
        _semantic_result_card(hit)


def _semantic_result_card(hit: dict):
    meta       = hit.get("metadata", {})
    document   = hit.get("document", "")
    distance   = hit.get("distance", 1.0)
    similarity = max(0, round((1 - distance) * 100, 1))

    # Extract SQL from the stored document text (after "SQL:\n")
    sql_block = ""
    if "SQL:\n" in document:
        sql_block = document.split("SQL:\n", 1)[1].strip()[:400]

    bar_color = (
        "#4ade80" if similarity >= 70
        else "#f59e0b" if similarity >= 40
        else "#ef4444"
    )

    st.markdown(
        f"""
        <div style="background:#0f1624;border:1px solid #1a2235;border-left:3px solid {bar_color};
                    border-radius:6px;padding:0.9rem 1rem;margin-bottom:0.6rem">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;color:#c9d4e8">
                    {meta.get('query_name', '—')}
                </span>
                <div style="display:flex;align-items:center;gap:0.6rem">
                    <span style="color:#7c3aed;font-size:0.78rem">
                        📁 {meta.get('folder_name', '—')}
                    </span>
                    <span style="background:#0b1a0b;color:{bar_color};
                                 border:1px solid {bar_color}33;padding:2px 8px;
                                 border-radius:4px;font-size:0.72rem">
                        {similarity}% match
                    </span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    if sql_block:
        st.code(sql_block + ("…" if len(sql_block) >= 400 else ""), language="sql")

    st.markdown(
        f"""
            <p style="color:#3a4d63;font-size:0.72rem;margin:0.4rem 0 0">
                v{meta.get('version', '?')} ·
                Last changed by <strong style="color:#4a6a8a">{meta.get('changed_by', '—')}</strong>
                on {fmt_datetime(meta.get('changed_at', ''))}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _highlight(text: str, term: str) -> str:
    if not term:
        return text
    lower = text.lower()
    t = term.lower()
    idx = lower.find(t)
    if idx == -1:
        return text
    return (
        text[:idx]
        + '<mark style="background:#003d55;color:#00b8d9;border-radius:2px">'
        + text[idx : idx + len(term)]
        + "</mark>"
        + text[idx + len(term) :]
    )
