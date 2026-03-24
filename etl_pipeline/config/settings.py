"""
config/settings.py
ETL pipeline configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class ETLSettings:
    # Source PostgreSQL (QueryVault app DB)
    SOURCE_DB_URL: str = os.getenv("SOURCE_DB_URL", "")

    # ChromaDB
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "chromadb")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "query_vault_queries")

    # Embedding provider: "huggingface" (default, local) or "openai"
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Airflow Variable key used to persist the sync watermark
    WATERMARK_VARIABLE: str = "query_vault_last_sync"

    # Fallback start date when no watermark exists yet (full initial load)
    DEFAULT_START_DATE: str = os.getenv("ETL_DEFAULT_START_DATE", "2020-01-01T00:00:00")

    # Batch size for upsert calls to ChromaDB
    UPSERT_BATCH_SIZE: int = int(os.getenv("UPSERT_BATCH_SIZE", "100"))


etl_settings = ETLSettings()
