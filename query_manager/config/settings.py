"""
config/settings.py
Application configuration loaded from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # PostgreSQL connection string
    DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://balaji:balajiU%4012@localhost:5433/queryValut"
)

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    APP_TITLE: str = os.getenv("APP_TITLE", "Query Manager")
    APP_VERSION: str = "1.0.0"

    # Password policy
    MIN_PASSWORD_LENGTH: int = 6
    MIN_USERNAME_LENGTH: int = 3

    # Pagination
    ACTIVITY_FEED_LIMIT: int = 50
    SEARCH_RESULTS_LIMIT: int = 100

    # ChromaDB (vector store — shared with ETL pipeline)
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "query_vault_queries")

    # Embedding provider used for semantic search queries
    # "huggingface" (local, default) or "openai"
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # LLM provider for the AI SQL assistant
    # "ollama" (local, default) or "openai"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen:14b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Number of similar queries fetched from ChromaDB per RAG request
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
