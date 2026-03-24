"""
tasks/load.py
Embeds transformed documents and upserts them into ChromaDB.
Supports HuggingFace (local, default) and OpenAI embedding providers.
"""
import logging
from typing import Any, Dict, List

import chromadb

logger = logging.getLogger(__name__)


def get_embedder(provider: str, model_name: str):
    """Return a LangChain embedder instance based on provider config."""
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model_name)
    else:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model_name)


def embed_and_load(
    documents: List[Dict[str, Any]],
    chroma_host: str,
    chroma_port: int,
    collection_name: str,
    embedding_provider: str,
    embedding_model: str,
    batch_size: int = 100,
) -> int:
    """
    Embed each document's `text` field and upsert into the ChromaDB collection.

    Uses document `id` as the ChromaDB ID so re-runs are idempotent (upsert).
    Returns the number of documents successfully loaded.
    """
    if not documents:
        logger.info("No documents to load — skipping.")
        return 0

    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    embedder = get_embedder(embedding_provider, embedding_model)
    total_loaded = 0

    for batch_start in range(0, len(documents), batch_size):
        batch = documents[batch_start : batch_start + batch_size]

        ids       = [doc["id"]       for doc in batch]
        texts     = [doc["text"]     for doc in batch]
        metadatas = [doc["metadata"] for doc in batch]

        embeddings = embedder.embed_documents(texts)

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        total_loaded += len(batch)
        logger.info(
            "Upserted batch %d-%d (%d docs)",
            batch_start,
            batch_start + len(batch) - 1,
            len(batch),
        )

    logger.info("Total documents loaded into ChromaDB: %d", total_loaded)
    return total_loaded


def delete_from_collection(
    query_ids: List[int],
    chroma_host: str,
    chroma_port: int,
    collection_name: str,
) -> int:
    """Remove deleted queries from the ChromaDB collection."""
    if not query_ids:
        return 0

    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    try:
        collection = client.get_collection(collection_name)
    except Exception:
        logger.warning("Collection %s not found — nothing to delete.", collection_name)
        return 0

    chroma_ids = [f"query_{qid}" for qid in query_ids]
    collection.delete(ids=chroma_ids)
    logger.info("Deleted %d documents from ChromaDB", len(chroma_ids))
    return len(chroma_ids)
