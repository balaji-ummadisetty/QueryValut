"""
database/migrations.py
PostgreSQL schema creation and migrations using psycopg2.
%s placeholders used throughout (psycopg2 style, not SQLite's ?).
"""
from database.connection import get_conn


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active     INTEGER DEFAULT 1,
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS folders (
    id          SERIAL PRIMARY KEY,
    parent_id   INTEGER REFERENCES folders(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    created_by  TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(parent_id, name)
);

CREATE TABLE IF NOT EXISTS queries (
    id          SERIAL PRIMARY KEY,
    folder_id   INTEGER NOT NULL REFERENCES folders(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT,
    tags        TEXT DEFAULT '[]',
    created_by  TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(folder_id, name)
);

CREATE TABLE IF NOT EXISTS query_versions (
    id             SERIAL PRIMARY KEY,
    query_id       INTEGER NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    version        INTEGER NOT NULL,
    sql_content    TEXT NOT NULL,
    description    TEXT,
    change_summary TEXT,
    changed_by     TEXT NOT NULL,
    changed_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(query_id, version)
);

CREATE INDEX IF NOT EXISTS idx_query_versions_query_id ON query_versions(query_id);
CREATE INDEX IF NOT EXISTS idx_queries_folder_id       ON queries(folder_id);
CREATE INDEX IF NOT EXISTS idx_folders_parent_id       ON folders(parent_id);
"""


def run_migrations() -> None:
    """Run all pending schema migrations and seed default admin if needed."""
    conn = get_conn()
    try:
        cur = conn.cursor()

        # Run schema statements one by one (psycopg2 doesn't support executescript)
        for statement in SCHEMA_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                cur.execute(stmt)

        # Seed default admin if no users exist
        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        row = cur.fetchone()
        if row["cnt"] == 0:
            _seed_admin(cur)

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def _seed_admin(cur) -> None:
    """Insert a default admin user (password: admin123)."""
    import bcrypt
    hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        ("admin", hashed),
    )
