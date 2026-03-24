# QueryVault

QueryVault is a tool for managing SQL queries as a team. You can organize queries into folders, track every edit with version history, search by meaning (not just keywords), and ask an AI assistant to write or explain SQL.

It has two parts:
- **query_manager** — the web app (Streamlit)
- **etl_pipeline** — a background sync job (Airflow) that keeps the search index up to date

---

## How it works

When you save a query, it's stored in PostgreSQL. The Airflow ETL pipeline picks up changes on a schedule, generates embeddings, and pushes them to ChromaDB. The web app uses those embeddings to power semantic search and the AI chat assistant.

```
PostgreSQL → Airflow ETL → ChromaDB → Web App (search + AI chat)
```

---

## Running locally

### Step 1 — Start the database

```bash
cd infra/postgres
docker compose up -d
```

PostgreSQL runs on port `5433`. PgAdmin is available at `http://localhost:8080` (`admin@admin.com` / `adminpassword`).

### Step 2 — Start Airflow and ChromaDB

```bash
cd infra/airflow
docker compose up -d
```

Give it about a minute to initialize. Airflow UI is at `http://localhost:8081` (login: `admin` / `admin`).

Once it's up, trigger the `query_vault_sync` DAG manually from the UI to do the first full sync.

### Step 3 — Run the web app

```bash
cd query_manager
cp .env.example .env   # fill in your values
pip install -r requirements.txt
streamlit run main.py
```

App runs at `http://localhost:8501`. Default login: `admin` / `admin123`.

---

## Project structure

```
├── infra/
│   ├── postgres/docker-compose.yaml   # PostgreSQL + PgAdmin
│   └── airflow/docker-compose.yaml    # Airflow + ChromaDB
│
├── query_manager/                     # Streamlit web app
│   ├── main.py
│   ├── config/          # settings and env vars
│   ├── database/        # connection pool, migrations
│   ├── models/          # User, Folder, Query, QueryVersion
│   ├── services/        # auth, query CRUD, versioning, RAG
│   ├── ui/              # pages and components
│   └── utils/           # SQL diff, helpers
│
└── etl_pipeline/                      # Airflow ETL
    ├── dags/            # query_vault_sync DAG
    ├── tasks/           # extract, transform, load
    └── config/          # ETL settings
```

---

## Environment variables

Each app has its own `.env`. Copy from `.env.example` at the root as a reference.

| Variable | Used by | Notes |
|---|---|---|
| `DATABASE_URL` | query_manager | direct PostgreSQL connection |
| `SOURCE_DB_URL` | etl_pipeline | use `host.docker.internal` when running in Docker |
| `CHROMA_HOST`, `CHROMA_PORT` | both | ChromaDB location |
| `EMBEDDING_PROVIDER` | both | `huggingface` (local) or `openai` |
| `LLM_PROVIDER` | query_manager | `ollama` (local) or `openai` |
| `LLM_MODEL` | query_manager | e.g. `qwen:14b` for Ollama |
| `OPENAI_API_KEY` | both | only needed when using OpenAI |

---

## Stack

- **Web app** — Python, Streamlit, psycopg2, LangChain
- **Database** — PostgreSQL 17
- **Vector store** — ChromaDB
- **Embeddings** — HuggingFace `all-MiniLM-L6-v2` (or OpenAI)
- **LLM** — Ollama (local) or OpenAI
- **ETL** — Apache Airflow
# real-time-ecommerce-etl-pipeline
