"""
ui/pages/chat_page.py
AI SQL Assistant — RAG-powered chat interface.

Uses ChromaDB (populated by the ETL pipeline) to retrieve similar stored
queries as context, then passes them to an LLM (Ollama or OpenAI) to
generate schema-aware SQL.

Session state keys used:
    chat_messages  – list of { role, content, sql, sources }
"""

import streamlit as st
from services.rag_service import rag_service
from ui.components import page_header


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render():
    page_header(
        "AI SQL Assistant",
        "Describe what data you need — the assistant generates SQL using your query repository as context.",
    )

    _init_chat_state()
    _render_status_bar()
    _render_chat_history()
    _render_input_bar()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def _init_chat_state():
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_thinking" not in st.session_state:
        st.session_state.chat_thinking = False


# ---------------------------------------------------------------------------
# Status bar (shows ChromaDB / LLM provider info)
# ---------------------------------------------------------------------------

def _render_status_bar():
    from config.settings import settings

    llm_label   = f"{settings.LLM_PROVIDER.upper()} · {settings.LLM_MODEL}"
    embed_label = f"{settings.EMBEDDING_PROVIDER.upper()} · {settings.EMBEDDING_MODEL}"
    chroma_label = f"{settings.CHROMA_HOST}:{settings.CHROMA_PORT}"

    st.markdown(
        f"""
        <div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:1rem;
                    background:#0b0f1a;border:1px solid #1a2235;border-radius:6px;
                    padding:0.5rem 1rem;font-size:0.75rem;color:#4a5e78">
            <span>LLM: <strong style="color:#00b8d9">{llm_label}</strong></span>
            <span style="color:#1a2235">|</span>
            <span>Embeddings: <strong style="color:#7c3aed">{embed_label}</strong></span>
            <span style="color:#1a2235">|</span>
            <span>Vector DB: <strong style="color:#4ade80">{chroma_label}</strong></span>
            <span style="color:#1a2235">|</span>
            <span>Context queries: <strong style="color:#f59e0b">{settings.RAG_TOP_K}</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------

def _render_chat_history():
    messages = st.session_state.chat_messages

    if not messages:
        _welcome_message()
        return

    for msg in messages:
        if msg["role"] == "user":
            _user_bubble(msg["content"])
        else:
            _assistant_bubble(msg["content"], msg.get("sql"), msg.get("sources", []))

    # Thinking indicator
    if st.session_state.chat_thinking:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:0.6rem;
                        padding:0.7rem 1rem;color:#627890;font-size:0.85rem">
                <div style="width:8px;height:8px;border-radius:50%;background:#00b8d9;
                            animation:pulse 1s infinite"></div>
                Generating SQL…
            </div>
            <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}</style>
            """,
            unsafe_allow_html=True,
        )


def _welcome_message():
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 2rem">
            <div style="font-size:2.8rem;margin-bottom:0.8rem">🤖</div>
            <h3 style="color:#c9d4e8;font-family:'IBM Plex Mono',monospace;
                       font-size:1.1rem;margin-bottom:0.5rem">
                Ask me to write SQL for you
            </h3>
            <p style="color:#4a5e78;font-size:0.85rem;max-width:480px;margin:0 auto">
                I'll search your query repository for similar examples and use them
                as context to generate accurate, schema-aware SQL.
            </p>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;
                    max-width:600px;margin:0 auto 2rem">
        """,
        unsafe_allow_html=True,
    )

    suggestions = [
        "Show all active listings with agent details",
        "Find top 10 customers by revenue last month",
        "Count queries created per folder this week",
        "Join orders with products and filter by status",
    ]
    cols = st.columns(2)
    for i, hint in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(hint, key=f"hint_{i}", use_container_width=True):
                _submit_message(hint)

    st.markdown("</div>", unsafe_allow_html=True)


def _user_bubble(content: str):
    st.markdown(
        f"""
        <div style="display:flex;justify-content:flex-end;margin:0.5rem 0">
            <div style="background:#0a2030;border:1px solid #00b8d955;color:#c9d4e8;
                        border-radius:12px 12px 2px 12px;padding:0.65rem 1rem;
                        max-width:75%;font-size:0.88rem;line-height:1.5">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _assistant_bubble(
    content: str,
    sql: str | None,
    sources: list,
):
    # Detect if content IS the SQL (starts with SELECT/WITH/INSERT/etc.)
    sql_keywords = ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE", "-- ")
    content_is_sql = content.lstrip().upper().startswith(sql_keywords)

    st.markdown(
        """
        <div style="display:flex;justify-content:flex-start;margin:0.5rem 0">
            <div style="background:#0f1624;border:1px solid #1a2235;border-left:3px solid #00b8d9;
                        color:#c9d4e8;border-radius:2px 12px 12px 12px;
                        padding:0.75rem 1rem;max-width:90%;width:100%;font-size:0.88rem">
        """,
        unsafe_allow_html=True,
    )

    if content_is_sql:
        st.code(content, language="sql")
    else:
        # Split on SQL fences if the LLM wrapped output in markdown
        if "```sql" in content:
            parts = content.split("```sql")
            if parts[0].strip():
                st.markdown(
                    f'<p style="color:#8899b4;margin-bottom:0.5rem">{parts[0].strip()}</p>',
                    unsafe_allow_html=True,
                )
            sql_block = parts[1].split("```")[0].strip() if len(parts) > 1 else ""
            if sql_block:
                st.code(sql_block, language="sql")
        elif "```" in content:
            parts = content.split("```")
            if parts[0].strip():
                st.markdown(
                    f'<p style="color:#8899b4;margin-bottom:0.5rem">{parts[0].strip()}</p>',
                    unsafe_allow_html=True,
                )
            if len(parts) > 1:
                st.code(parts[1].strip(), language="sql")
        else:
            st.markdown(
                f'<p style="color:#8899b4;line-height:1.6">{content}</p>',
                unsafe_allow_html=True,
            )

    # Sources expander
    if sources:
        with st.expander(f"📚 {len(sources)} context quer{'y' if len(sources)==1 else 'ies'} used"):
            for src in sources:
                meta = src.get("metadata", {})
                dist = src.get("distance", 0)
                similarity = max(0, round((1 - dist) * 100, 1))
                st.markdown(
                    f"""
                    <div style="background:#080d18;border:1px solid #1a2235;
                                border-radius:6px;padding:0.55rem 0.8rem;margin-bottom:0.4rem">
                        <div style="display:flex;justify-content:space-between;
                                    align-items:center;margin-bottom:0.3rem">
                            <span style="color:#c9d4e8;font-size:0.82rem;font-weight:500">
                                {meta.get('query_name', 'Query')}
                            </span>
                            <span style="background:#052e16;color:#4ade80;
                                         border:1px solid #4ade8033;padding:1px 7px;
                                         border-radius:4px;font-size:0.7rem">
                                {similarity}% match
                            </span>
                        </div>
                        <span style="color:#7c3aed;font-size:0.75rem">
                            📁 {meta.get('folder_name', '')} · v{meta.get('version', '?')}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            '<p style="color:#3a4d63;font-size:0.72rem;margin-top:0.4rem">'
            '⚠️ No context from repository (ChromaDB unavailable or collection empty)</p>',
            unsafe_allow_html=True,
        )

    st.markdown("</div></div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Input bar
# ---------------------------------------------------------------------------

def _render_input_bar():
    st.markdown('<div style="margin-top:1.5rem">', unsafe_allow_html=True)

    cols = st.columns([0.85, 0.15], gap="small")

    with cols[0]:
        user_input = st.text_input(
            "",
            placeholder="Describe the SQL you need, e.g. 'Show monthly sales grouped by region'…",
            label_visibility="collapsed",
            key="chat_input",
            disabled=st.session_state.chat_thinking,
        )

    with cols[1]:
        send = st.button(
            "Send",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.chat_thinking,
        )

    if st.session_state.chat_messages:
        if st.button("🗑 Clear chat", use_container_width=False):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if send and user_input.strip():
        _submit_message(user_input.strip())


# ---------------------------------------------------------------------------
# Message submission + LLM call
# ---------------------------------------------------------------------------

def _submit_message(text: str):
    # Append user message
    st.session_state.chat_messages.append(
        {"role": "user", "content": text, "sql": None, "sources": []}
    )
    st.session_state.chat_thinking = True
    st.rerun()


def _process_pending():
    """
    Called on each rerun while chat_thinking is True.
    Runs the RAG call and appends the assistant reply.
    """
    if not st.session_state.get("chat_thinking"):
        return

    messages = st.session_state.chat_messages
    # Last message is the user turn waiting for a reply
    last_user = messages[-1]["content"]

    # Build history (all turns except the last pending one)
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[:-1]
    ]

    try:
        answer, sources = rag_service.generate_sql(last_user, history)
    except Exception as exc:
        answer = f"Sorry, I couldn't generate SQL: {exc}"
        sources = []

    st.session_state.chat_messages.append(
        {"role": "assistant", "content": answer, "sql": None, "sources": sources}
    )
    st.session_state.chat_thinking = False


# Run pending LLM call before rendering (fires on the rerun triggered by _submit_message)
_process_pending()
