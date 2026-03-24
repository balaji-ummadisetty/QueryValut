"""
services/rag_service.py
RAG-powered SQL generation and semantic search.

Two capabilities:
  1. semantic_search(query_text) → finds similar stored queries via ChromaDB
  2. generate_sql(user_request, chat_history) → uses retrieved queries as context
     and calls an LLM (Ollama or OpenAI) to generate new SQL

ChromaDB is populated by the separate etl_pipeline/ Airflow service.
If ChromaDB is unavailable the service degrades gracefully:
  - semantic_search returns []
  - generate_sql falls back to LLM-only (no context)
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from config.settings import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def _get_embedder():
    if settings.EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
        )
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def _get_llm():
    if settings.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
        )
    from langchain_community.chat_models import ChatOllama
    return ChatOllama(
        model=settings.LLM_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.1,
    )


# ---------------------------------------------------------------------------
# ChromaDB client helper
# ---------------------------------------------------------------------------

def _get_chroma_collection():
    import chromadb
    client = chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )
    return client.get_collection(settings.CHROMA_COLLECTION)


# ---------------------------------------------------------------------------
# RAGService
# ---------------------------------------------------------------------------

class RAGService:

    def semantic_search(
        self,
        query_text: str,
        n_results: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Embed `query_text` and find the most similar stored queries in ChromaDB.

        Returns a list of dicts:
            {
                "id":          chroma doc id,
                "document":    raw stored text,
                "metadata":    { query_name, folder_name, version, ... },
                "distance":    cosine distance (lower = more similar),
            }

        Returns [] if ChromaDB is unreachable or the collection is empty.
        """
        if not query_text.strip():
            return []

        top_k = n_results or settings.RAG_TOP_K

        try:
            embedder = _get_embedder()
            query_embedding = embedder.embed_query(query_text)

            collection = _get_chroma_collection()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            hits = []
            for i in range(len(results["ids"][0])):
                hits.append(
                    {
                        "id":       results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )
            return hits

        except Exception as exc:
            logger.warning("Semantic search unavailable: %s", exc)
            return []

    def generate_sql(
        self,
        user_request: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Generate SQL for `user_request` using RAG context from ChromaDB.

        Returns:
            (generated_sql_or_response, sources)

        `sources` is the list of similar queries used as context
        (empty if ChromaDB was unavailable).
        """
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        # ---- 1. Retrieve similar queries ----------------------------------
        sources = self.semantic_search(user_request)

        # ---- 2. Build context block from retrieved queries ----------------
        if sources:
            context_parts = []
            for i, src in enumerate(sources, 1):
                meta = src["metadata"]
                context_parts.append(
                    f"Example {i} — {meta.get('query_name', 'Query')} "
                    f"(folder: {meta.get('folder_name', '')}, "
                    f"v{meta.get('version', '?')}):\n"
                    f"{src['document']}"
                )
            context_block = "\n\n---\n\n".join(context_parts)
        else:
            context_block = "No similar queries found in the repository."

        # ---- 3. System prompt ---------------------------------------------
        system_prompt = (
            "You are an expert SQL assistant integrated into QueryVault, "
            "a collaborative SQL management platform backed by PostgreSQL.\n\n"
            "Your job is to help users write accurate, well-formatted SQL queries.\n\n"
            "You have access to the following similar queries from the repository "
            "as reference examples — use their patterns, table names, and conventions "
            "when generating new SQL:\n\n"
            f"{context_block}\n\n"
            "Rules:\n"
            "1. Return ONLY valid SQL. No prose before or after unless the user "
            "   explicitly asks for an explanation.\n"
            "2. Format SQL with consistent indentation and uppercase keywords.\n"
            "3. Add brief inline comments (-- ...) for non-obvious clauses.\n"
            "4. If the request is ambiguous, make reasonable assumptions and note "
            "   them in a short comment at the top of the query.\n"
            "5. If you cannot produce SQL (e.g. the request is not SQL-related), "
            "   say so clearly in one sentence."
        )

        # ---- 4. Assemble message history ----------------------------------
        messages = [SystemMessage(content=system_prompt)]

        for turn in (chat_history or []):
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn["role"] == "assistant":
                messages.append(AIMessage(content=turn["content"]))

        messages.append(HumanMessage(content=user_request))

        # ---- 5. Call LLM --------------------------------------------------
        try:
            llm = _get_llm()
            response = llm.invoke(messages)
            return response.content.strip(), sources
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            raise


rag_service = RAGService()
