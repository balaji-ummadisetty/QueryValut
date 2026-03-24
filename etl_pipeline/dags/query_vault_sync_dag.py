"""
dags/query_vault_sync_dag.py

QueryVault daily sync DAG
--------------------------
Schedule: daily at 02:00 UTC

Pipeline steps
--------------
1. get_watermark        – Read last successful sync timestamp from Airflow Variable
2. extract              – Pull changed/new queries from PostgreSQL since watermark
3. transform            – Build embeddable document dicts from raw rows
4. embed_and_load       – Generate embeddings and upsert into ChromaDB
5. update_watermark     – Persist the new watermark so next run is incremental

Watermark strategy
------------------
The Airflow Variable `query_vault_last_sync` stores an ISO-8601 UTC timestamp.
On the very first run (variable missing) the pipeline does a full load from
ETL_DEFAULT_START_DATE, giving a complete initial index.

Idempotency
-----------
ChromaDB upsert is keyed on `query_{query_id}`, so re-running the DAG for the
same time window is safe — it simply overwrites identical vectors.
"""

import logging
from datetime import datetime, timezone

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.utils.dates import days_ago

# The config / task modules are importable because /opt/airflow is on PYTHONPATH
# (set via AIRFLOW__CORE__PYTHONPATH or the docker-compose environment block).
from config.settings import etl_settings
from tasks.extract import extract_changed_queries
from tasks.transform import transform_to_documents
from tasks.load import embed_and_load

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------

@dag(
    dag_id="query_vault_daily_sync",
    description="Incremental sync of QueryVault queries to ChromaDB embeddings",
    schedule_interval="*/1 * * * *",
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["queryvault", "etl", "embeddings"],
    default_args={
        "owner": "queryvault",
        "retries": 2,
    },
)
def query_vault_sync():

    # ------------------------------------------------------------------
    # Task 1 – Read watermark
    # ------------------------------------------------------------------
    @task()
    def get_watermark() -> str:
        """
        Return the ISO-8601 UTC timestamp of the last successful sync.
        Falls back to ETL_DEFAULT_START_DATE on the very first run.
        """
        raw = Variable.get(
            etl_settings.WATERMARK_VARIABLE,
            default_var=etl_settings.DEFAULT_START_DATE,
        )
        logger.info("Watermark: %s", raw)
        return raw

    # ------------------------------------------------------------------
    # Task 2 – Extract
    # ------------------------------------------------------------------
    @task()
    def extract(watermark: str) -> list:
        """Pull rows changed since the watermark from PostgreSQL."""
        since = datetime.fromisoformat(watermark)
        rows = extract_changed_queries(
            source_db_url=etl_settings.SOURCE_DB_URL,
            since=since,
        )
        logger.info("Extracted %d rows", len(rows))
        return rows

    # ------------------------------------------------------------------
    # Task 3 – Transform
    # ------------------------------------------------------------------
    @task()
    def transform(rows: list) -> list:
        """Convert raw rows to embeddable document dicts."""
        if not rows:
            logger.info("Nothing to transform.")
            return []
        documents = transform_to_documents(rows)
        logger.info("Transformed %d documents", len(documents))
        return documents

    # ------------------------------------------------------------------
    # Task 4 – Embed & load
    # ------------------------------------------------------------------
    @task()
    def load(documents: list) -> int:
        """Embed documents and upsert into ChromaDB."""
        if not documents:
            logger.info("No documents to embed — skipping ChromaDB upsert.")
            return 0

        count = embed_and_load(
            documents=documents,
            chroma_host=etl_settings.CHROMA_HOST,
            chroma_port=etl_settings.CHROMA_PORT,
            collection_name=etl_settings.CHROMA_COLLECTION,
            embedding_provider=etl_settings.EMBEDDING_PROVIDER,
            embedding_model=etl_settings.EMBEDDING_MODEL,
            batch_size=etl_settings.UPSERT_BATCH_SIZE,
        )
        logger.info("Loaded %d documents into ChromaDB collection '%s'",
                    count, etl_settings.CHROMA_COLLECTION)
        return count

    # ------------------------------------------------------------------
    # Task 5 – Update watermark
    # ------------------------------------------------------------------
    @task()
    def update_watermark(loaded_count: int) -> None:
        """
        Advance the watermark to now so the next run only processes new changes.
        We only update the watermark if the pipeline actually ran (even 0 docs
        is fine — it means nothing changed, still advance the clock).
        """
        new_ts = datetime.now(tz=timezone.utc).isoformat()
        Variable.set(etl_settings.WATERMARK_VARIABLE, new_ts)
        logger.info(
            "Watermark updated to %s (processed %d docs this run)",
            new_ts,
            loaded_count,
        )

    # ------------------------------------------------------------------
    # Wire tasks together
    # ------------------------------------------------------------------
    wm        = get_watermark()
    raw_rows  = extract(wm)
    docs      = transform(raw_rows)
    count     = load(docs)
    update_watermark(count)


# Instantiate the DAG
query_vault_sync()
